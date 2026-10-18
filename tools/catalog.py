#!/usr/bin/env python3
"""Tyrion katalogi — butun tizimning mashina o'qiydigan yagona reestri.

Muammo: tizimda nima bor (agent, skill, bot, tool, qayd) — qo'lda yozilgan
ro'yxatlar bilan yuritilsa, raqamlar eskiradi va nusxalar bir-biridan uzoqlashadi
(hozir 33 charterning 12 tasi ikki nusxada farq qiladi).

Yechim: katalog HAR DOIM fayl tizimidan generatsiya qilinadi. Qo'lda tahrirlanmaydi.
`check` buyrug'i katalog bilan haqiqatni solishtiradi va farq bo'lsa xato qaytaradi.

Buyruqlar:
  py -3 tools\\catalog.py build            # manifests/catalog.json ni qayta yozadi
  py -3 tools\\catalog.py check            # katalog haqiqatga mos keladimi (CI/doctor uchun)
  py -3 tools\\catalog.py drift            # nusxalar (mirror) farqini ko'rsatadi
  py -3 tools\\catalog.py sync-mirrors     # nusxalarni kanonikdan qayta quradi (eskisi arxivga)
  py -3 tools\\catalog.py sync-claims      # hujjatlardagi (marker + oddiy matn) raqamlarni moslashtiradi
  py -3 tools\\catalog.py list --layer agents
  py -3 tools\\catalog.py summary

Chiqish kodi: 0 — mos, 1 — farq bor, 2 — xato.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

try:  # PyYAML bor bo'lsa ishlatiladi, bo'lmasa minimal parser
    import yaml  # type: ignore
except Exception:  # pragma: no cover - muhitga bog'liq
    yaml = None

VAULT = Path(__file__).resolve().parent.parent
MANIFEST = VAULT / "manifests" / "catalog.json"
SCHEMA = "tyrion-catalog/v1"

# Windows: konsol yoki quvur (pipe) bo'lsa ham UTF-8 chiqarish.
# Modul darajasida — skript boshqa skript ichidan chaqirilganda ham ishlashi uchun.
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        try:
            _stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:  # pragma: no cover
            pass

# Har bir qatlam: nom -> (ildiz papka, glob, tur)
# "canonical" — hozircha manba; "mirror" — nusxa (drift tekshiriladi)
LAYERS: dict[str, tuple[Path, str, str]] = {
    "wiki": (VAULT / "wiki", "*.md", "note"),
    "playbooks": (VAULT / "playbooks", "*.md", "playbook"),
    "contexts": (VAULT / "contexts", "*.md", "context"),
    "agents": (VAULT / "agents", "*.md", "agent"),
    "skills": (VAULT / "skills", "*/SKILL.md", "skill"),
    "commands": (VAULT / "commands", "*.md", "command"),
    "commands.mirror": (VAULT / ".claude" / "commands", "*.md", "command"),
    "rules": (VAULT / "rules", "*.md", "rule"),
    "hooks": (VAULT / "hooks", "*", "hook"),
    "tools": (VAULT / "tools", "*", "tool"),
    "tests": (VAULT / "tests", "test_*.py", "test"),
    "templates": (VAULT / "templates", "*.md", "template"),
    "evals": (VAULT / "evals", "*.json", "eval"),
}

# Drift tekshiriladigan juftliklar: (kanonik qatlam, nusxa qatlam)
MIRROR_PAIRS = [
    ("commands", "commands.mirror"),
]

# Marker bo'lmagan oddiy matndagi qo'lda yozilgan raqamlar.
# Har yozuv: (fayl, 3 guruhli regex — (old)(raqam)(keyin), katalog kaliti).
# Nega kerak: `<!-- tyrion:catalog -->` markeri faqat AGENTS.md/README.md da bor;
# INDEX.md va rules/ dagi "wiki 41 qayd" kabi jumlalar eskirib, miya o'zi haqida
# yolg'on gapiradigan bo'lib qolgan edi (41 ≠ 42). Endi `sync-claims` ularni ham
# tuzatadi, `doctor` esa tekshiradi.
HUMAN_CLAIMS: list[tuple[str, "re.Pattern[str]", str]] = [
    ("INDEX.md",
     re.compile(r"(\| `wiki/` \| Atomik, wikilink bog'langan bilim qaydlari \()(\d+)(\) \|)"),
     "wiki"),
    ("README.md",
     re.compile(r"(Bilim: atomik qaydlar \()(\d+)(\))"),
     "wiki"),
    ("rules/20-token-gigiyena.md",
     re.compile(r"(`wiki/` )(\d+)( qayd)"),
     "wiki"),
]

FRONTMATTER_RE = re.compile(r"\A---\r?\n(.*?)\r?\n---", re.DOTALL)
# YAML'da `\` dan keyin faqat shu belgilar kelishi mumkin. Boshqasi — xato
# (`\y` kabi), lekin PyYAML xatosini o'qish qiyin; o'zimiz aniqroq aytamiz.
INVALID_ESCAPE = re.compile(r'\\(?![0abtnvfre "\\/N_LPuxU])')
# Eng xavflisi: `\t` TO'G'RI escape, lekin yo'lni JIM buzadi —
# Windows backslash path -> TAB belgisi, xato chiqmaydi. Faqat qiymatni ko'zdan
# kechirib topiladi (2026-09-16 da 5 qaydda shu holat bo'lgan).
CONTROL_CHARS = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]|\t")


def _control_char_error(data: object) -> str | None:
    """Parse qilingan qiymatlar ichida ko'rinmas control belgi bormi."""
    stack: list[object] = [data]
    while stack:
        value = stack.pop()
        if isinstance(value, str):
            if CONTROL_CHARS.search(value):
                return "YAML escape qiymatni buzdi (ko'rinmas belgi) — \\ o'rniga / ishlatilsin"
        elif isinstance(value, dict):
            stack.extend(value.values())
            stack.extend(value.keys())
        elif isinstance(value, list):
            stack.extend(value)
    return None


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _fallback_frontmatter(text: str) -> dict:
    """PyYAML bo'lmaganda: `key: value` qatorlarini o'qish (ichma-ich tuzilma yo'q)."""
    data = {}
    for line in text.splitlines():
        if not line or line.startswith(("#", " ", "\t", "-")):
            continue
        if ":" in line:
            key, _, value = line.partition(":")
            data[key.strip()] = value.strip().strip('"').strip("'")
    return data


def read_frontmatter(path: Path) -> dict:
    """Fayl boshidagi YAML frontmatter. Buzilgan bo'lsa `_error` kaliti qo'shiladi."""
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        return {"_error": f"o'qib bo'lmadi: {exc}"}

    match = FRONTMATTER_RE.match(text)
    if not match:
        return {"_error": "frontmatter yo'q"}

    raw = match.group(1)
    if INVALID_ESCAPE.search(raw):
        return {"_error": "YAML'da yaroqsiz escape (\\ dan keyin noto'g'ri belgi) — / ishlatilsin"}

    if yaml is not None:
        try:
            data = yaml.safe_load(raw) or {}
            if not isinstance(data, dict):
                return {"_error": "frontmatter dict emas"}
            control = _control_char_error(data)
            return {"_error": control} if control else data
        except Exception as exc:  # YAML buzilgan
            return {"_error": f"YAML buzilgan: {exc}"}

    return _fallback_frontmatter(raw)


def _item(layer: str, path: Path) -> dict:
    stat = path.stat()
    fm = read_frontmatter(path)
    return {
        "name": path.parent.name if path.name == "SKILL.md" else path.stem,
        "layer": layer,
        "path": path.relative_to(VAULT).as_posix(),
        "sha256": _sha256(path)[:16],
        "bytes": stat.st_size,
        "updated": datetime.fromtimestamp(stat.st_mtime, timezone.utc)
        .astimezone()
        .isoformat(timespec="seconds"),
        "title": fm.get("name"),
        "description": (fm.get("description") or None),
        "source": fm.get("source"),
        "fm_error": fm.get("_error"),
    }


def scan() -> dict:
    """Fayl tizimini skanerlab, katalog tuzilmasini qaytaradi."""
    items: dict[str, list[dict]] = {}
    for layer, (root, pattern, _kind) in LAYERS.items():
        found: list[dict] = []
        if root.is_dir():
            for path in sorted(root.glob(pattern)):
                if path.is_file():
                    found.append(_item(layer, path))
        items[layer] = found

    counts = {layer: len(found) for layer, found in items.items()}

    return {
        "schema": SCHEMA,
        "generated": datetime.now().astimezone().isoformat(timespec="seconds"),
        "generator": "tools/catalog.py",
        "vault": str(VAULT),
        "counts": counts,
        "items": items,
        "mirrors": mirror_status(items),
        "warnings": warnings(items),
    }


def human_claims(counts: dict) -> list[dict]:
    """Hujjatlardagi oddiy matn raqamlari holati (mos / mos emas / topilmadi)."""
    result: list[dict] = []
    for rel, pattern, key in HUMAN_CLAIMS:
        path = VAULT / rel
        if not path.is_file():
            result.append({"file": rel, "key": key, "written": None,
                           "expected": counts.get(key), "ok": False,
                           "reason": "fayl yo'q"})
            continue
        match = pattern.search(path.read_text(encoding="utf-8", errors="replace"))
        if not match:
            result.append({"file": rel, "key": key, "written": None,
                           "expected": counts.get(key), "ok": False,
                           "reason": "naqsh topilmadi"})
            continue
        written = int(match.group(2))
        result.append({"file": rel, "key": key, "written": written,
                       "expected": counts.get(key), "ok": written == counts.get(key),
                       "reason": ""})
    return result


def mirror_status(items: dict[str, list[dict]]) -> list[dict]:
    """Nusxa juftliklari holati: identical | drifted | missing."""
    result: list[dict] = []
    for canonical_layer, mirror_layer in MIRROR_PAIRS:
        if canonical_layer not in items or mirror_layer not in items:
            continue
        canonical = {i["name"]: i for i in items.get(canonical_layer, [])}
        mirror = {i["name"]: i for i in items.get(mirror_layer, [])}
        for name in sorted(set(canonical) | set(mirror)):
            left, right = canonical.get(name), mirror.get(name)
            if left and right:
                status = "identical" if left["sha256"] == right["sha256"] else "drifted"
            else:
                status = "missing"
            result.append(
                {
                    "name": name,
                    "canonical": left["path"] if left else None,
                    "mirror": right["path"] if right else None,
                    "status": status,
                }
            )
    return result


def warnings(items: dict[str, list[dict]]) -> list[str]:
    """Diqqat talab qiladigan holatlar (bo'sh qatlam, buzilgan frontmatter, drift)."""
    notes: list[str] = []
    for layer in ("commands", "rules", "hooks", "tests"):
        if not items.get(layer):
            notes.append(f"qatlam bo'sh: {layer}/")
    for layer, found in items.items():
        broken = [i for i in found if i.get("fm_error") and layer in ("wiki", "agents", "skills")]
        if broken:
            notes.append(f"{layer}: {len(broken)} faylda frontmatter muammosi")
    drifted = [m for m in mirror_status(items) if m["status"] == "drifted"]
    if drifted:
        notes.append(f"drift: {len(drifted)} nusxa kanonikdan farq qiladi")
    return notes


def cmd_build(_args: argparse.Namespace) -> int:
    data = scan()
    import tyrion_core as tcore
    tcore.atomic_write_json(MANIFEST, data)
    print(f"✓ katalog yozildi: {MANIFEST.relative_to(VAULT).as_posix()}")
    print_summary(data)
    return 0


def _comparable(data: dict) -> dict:
    """Taqqoslash uchun: vaqt va yo'llarsiz mazmun."""
    return {
        "counts": data.get("counts"),
        "items": {
            layer: sorted((i["name"], i["sha256"]) for i in found)
            for layer, found in (data.get("items") or {}).items()
        },
    }


def cmd_check(_args: argparse.Namespace) -> int:
    if not MANIFEST.is_file():
        print("✗ katalog yo'q — avval: py -3 tools\\catalog.py build")
        return 2
    stored = json.loads(MANIFEST.read_text(encoding="utf-8"))
    current = scan()
    if stored.get("schema") != SCHEMA:
        print(f"✗ katalog sxemasi eski: {stored.get('schema')} != {SCHEMA}")
        return 2

    old, new = _comparable(stored), _comparable(current)
    if old == new:
        print(f"✓ katalog mos ({sum(current['counts'].values())} element)")
        return 0

    problems = 0
    for layer in sorted(set(old["items"]) | set(new["items"])):
        o, n = set(old["items"].get(layer, [])), set(new["items"].get(layer, []))
        for name, _sha in sorted(n - o):
            print(f"  + yangi:   {layer}/{name}")
            problems += 1
        for name, _sha in sorted(o - n):
            print(f"  - yo'qolgan/o'zgargan: {layer}/{name}")
            problems += 1
    for key in sorted(set(old["counts"]) | set(new["counts"])):
        if old["counts"].get(key) != new["counts"].get(key):
            print(f"  ~ soni: {key}: {old['counts'].get(key)} → {new['counts'].get(key)}")
            problems += 1
    print(f"\n✗ katalog eskirgan — {problems} farq. Tuzatish: py -3 tools\\catalog.py build")
    return 1


def cmd_drift(_args: argparse.Namespace) -> int:
    data = scan()
    drifted = [m for m in data["mirrors"] if m["status"] != "identical"]
    if not drifted:
        print(f"✓ nusxalar mos ({len(data['mirrors'])} juftlik tekshirildi)")
        return 0
    print(f"⚠ {len(drifted)} nusxa kanonik bilan mos emas:\n")
    for m in drifted:
        print(f"  [{m['status']:9}] {m['name']}")
        print(f"              kanonik: {m['canonical']}")
        print(f"              nusxa  : {m['mirror']}")
    print("\nEslatma: nusxa qo'lda tahrirlanmaydi — manba tuzatiladi, keyin sinxronlanadi.")
    return 1


def cmd_list(args: argparse.Namespace) -> int:
    data = scan()
    layers = [args.layer] if args.layer else list(LAYERS)
    for layer in layers:
        if layer not in data["items"]:
            print(f"✗ noma'lum qatlam: {layer}. Mavjud: {', '.join(LAYERS)}")
            return 2
        print(f"\n## {layer} ({len(data['items'][layer])})")
        for item in data["items"][layer]:
            flag = " ⚠" if item.get("fm_error") and layer in ("wiki", "agents", "skills") else ""
            print(f"  {item['name']:28} {item['path']}{flag}")
    return 0


def cmd_sync_claims(args: argparse.Namespace) -> int:
    """Hujjatlardagi e'lon qilingan raqamlarni katalogga moslashtiradi (ECC'dagi `--write`).

    Ikki xil yozuv tuzatiladi:
    1. `<!-- tyrion:catalog ... -->` markeri (AGENTS.md, README.md).
    2. Oddiy matndagi raqamlar (`HUMAN_CLAIMS` — INDEX.md, README.md, rules/...).

    Nega: qo'lda yozilgan "33 agent, 41 qayd" kabi sonlar vaqt o'tib eskiradi va
    yolg'on da'voga aylanadi. Bu buyruq ularni fayl tizimidagi haqiqatdan yozadi.
    """
    data = scan()
    counts = data["counts"]
    marker_re = re.compile(r"(<!--\s*tyrion:catalog\s+)([^>]*?)(\s*-->)")
    changed: list[str] = []

    for doc in (VAULT / "AGENTS.md", VAULT / "README.md"):
        if not doc.is_file():
            continue
        text = doc.read_text(encoding="utf-8")
        match = marker_re.search(text)
        if not match:
            continue
        keys = re.findall(r"(\w+)=", match.group(2))
        payload = " ".join(f"{key}={counts.get(key, 0)}" for key in keys)
        if payload == match.group(2).strip():
            continue
        if not args.dry_run:
            doc.write_text(marker_re.sub(lambda m: m.group(1) + payload + m.group(3), text, count=1),
                           encoding="utf-8")
        changed.append(f"{doc.name}: {match.group(2).strip()} → {payload}")

    # Marker bo'lmagan oddiy matn raqamlari (INDEX.md, README.md, rules/...)
    for rel, pattern, key in HUMAN_CLAIMS:
        path = VAULT / rel
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        match = pattern.search(text)
        if not match or int(match.group(2)) == counts.get(key):
            continue
        payload = str(counts.get(key, 0))
        if not args.dry_run:
            path.write_text(
                pattern.sub(lambda m: m.group(1) + payload + m.group(3), text, count=1),
                encoding="utf-8",
            )
        changed.append(f"{rel}: {match.group(2)} → {payload}")

    if not changed:
        print("✓ hujjatlardagi raqamlar katalogga mos")
        return 0
    for line in changed:
        print(("  yangilandi: " if not args.dry_run else "  yangilanadi: ") + line)
    print(f"\n{'✗ --dry-run: hech narsa yozilmadi' if args.dry_run else '✓ raqamlar yangilandi'}")
    return 0


def cmd_sync_mirrors(args: argparse.Namespace) -> int:
    """Kanonik qatlamlardan nusxalarni qayta quradi (bayt-aniq).

    Nusxa qo'lda tahrirlanmaydi: manba — `LAYERS` dagi kanonik qatlam. Eski nusxa
    **o'chirilmaydi** — `archive/mirror-sync-<sana>/` ga ko'chiriladi (vault qoidasi:
    hech narsa yo'qolmaydi).
    """
    data = scan()
    stamp = datetime.now().strftime("%Y-%m-%d")
    archive_root = VAULT / "archive" / f"mirror-sync-{stamp}"
    copied: list[str] = []
    archived: list[str] = []
    orphans: list[str] = []

    for canonical_layer, mirror_layer in MIRROR_PAIRS:
        canonical = {i["name"]: i for i in data["items"].get(canonical_layer, [])}
        mirror = {i["name"]: i for i in data["items"].get(mirror_layer, [])}
        mirror_root = LAYERS[mirror_layer][0]

        for name, item in sorted(canonical.items()):
            existing = mirror.get(name)
            if existing and existing["sha256"] == item["sha256"]:
                continue
            source = VAULT / item["path"]
            destination = mirror_root / f"{name}.md"
            copied.append(f"{canonical_layer} → {mirror_layer}: {name}")
            if args.dry_run:
                continue

            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(source.read_bytes())

        orphans.extend(
            f"{mirror_layer}/{name} (kanonikda yo'q)" for name in sorted(set(mirror) - set(canonical))
        )



    if not copied:
        print(f"✓ nusxalar mos — yangilash kerak emas ({len(data['mirrors'])} juftlik)")
        return 0

    label = "Ko'chiriladi" if not args.dry_run else "Ko'chiriladi (dry-run)"
    print(f"{label}: {len(copied)}")
    for line in copied:
        print(f"  → {line}")
    if archived:
        print(f"\nArxivga olindi ({len(archived)}): {archive_root.relative_to(VAULT).as_posix()}")
    if orphans:
        print(f"\n⚠ kanonigi yo'q nusxalar ({len(orphans)}) — o'chirilmadi:")
        for line in orphans:
            print(f"  ? {line}")
    print("\n" + ("· --dry-run: hech narsa yozilmadi" if args.dry_run else
                  "✓ tayyor. Tekshirish: py -3 tools\\catalog.py drift"))
    return 0


def print_summary(data: dict) -> None:
    counts = data["counts"]
    print("\nQatlamlar:")
    for layer in list(LAYERS):
        print(f"  {layer:18} {counts.get(layer, 0)}")
    if data["warnings"]:
        print("\nDiqqat:")
        for note in data["warnings"]:
            print(f"  ⚠ {note}")


def cmd_summary(_args: argparse.Namespace) -> int:
    print_summary(scan())
    return 0


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser(
        prog="catalog.py", description="Tyrion katalogi — yagona reestr (fayl tizimidan generatsiya)"
    )
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("build", help="manifests/catalog.json ni qayta yozadi").set_defaults(func=cmd_build)
    sub.add_parser("check", help="katalog haqiqatga mos keladimi").set_defaults(func=cmd_check)
    sub.add_parser("drift", help="nusxalar farqini ko'rsatadi").set_defaults(func=cmd_drift)
    sub.add_parser("summary", help="qisqa hisobot").set_defaults(func=cmd_summary)
    list_parser = sub.add_parser("list", help="qatlam elementlarini sanaydi")
    list_parser.add_argument("--layer", help=f"qatlam nomi: {', '.join(LAYERS)}")
    list_parser.set_defaults(func=cmd_list)

    sync_parser = sub.add_parser("sync-claims", help="hujjatlardagi raqamlarni katalogga moslashtiradi")
    sync_parser.add_argument("--dry-run", action="store_true", help="yozmasdan ko'rsatadi")
    sync_parser.set_defaults(func=cmd_sync_claims)

    mirrors_parser = sub.add_parser("sync-mirrors", help="nusxalarni kanonikdan qayta quradi")
    mirrors_parser.add_argument("--dry-run", action="store_true", help="yozmasdan ko'rsatadi")
    mirrors_parser.set_defaults(func=cmd_sync_mirrors)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
