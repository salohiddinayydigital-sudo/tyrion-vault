#!/usr/bin/env python3
r"""Vault sog'liq auditi va deterministik Delivery Gate — haftalik-audit va Stop hook uchun.

Tekshiradi:
  1. wiki/ qaydlari: frontmatter (name/description/tags/source/updated), YAML to'g'riligi
     (PyYAML bor bo'lsa qat'iy — qo'shtirnoq ichidagi `\` kabi escape xatolari tutiladi)
  2. har qaydda kamida 2 ta wikilink
  3. butun vault bo'ylab buzilgan wikilinklar
  4. yetim (orphan) qaydlar — hech kim havola qilmagan
  5. INDEX.md qamrovi — har qayd jadvalda bormi
  6. CLAUDE.md <= 300 qator
  7. dublikat nomlar
  8. LOG.md format bir xilligi (qator + jadval aralashmasi)

ECC (affaan-m/ECC) rejimlar:
  --gate   : Stop hook deterministik darvozasi (0 muammo + kompleks sessiyada LOG/wiki yangilanganligi)
  --write  : INDEX.md da qolib ketgan wiki qaydlarni avtomatik jadvalga qo'shish (doc-drift auto-fix)

Ishlatish:
  python tools/vault-audit.py [vault_ildizi] [--gate] [--write]
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import Counter, defaultdict
from datetime import date, datetime
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:  # pragma: no cover
    pass

try:
    import yaml
except Exception:  # pragma: no cover
    yaml = None

SKIP_DIRS = {
    ".git", ".obsidian", ".claude", ".codebuddy", ".cursor", ".gemini", ".qoder",
    "graphify-out", ".code-review-graph", "node_modules", "__pycache__", "output", "tmp",
    "claude-ads-main", "agents", "skills", "plugins", "archive",
}
REQUIRED_FM = ("name", "description", "tags", "source", "updated")
WIKILINK = re.compile(r"\[\[([^\]\|#]+)(?:#[^\]\|]*)?(?:\|[^\]]*)?\]\]")
FENCED = re.compile(r"```.*?```", re.S)
INLINE_CODE = re.compile(r"`[^`\n]*`")
INVALID_ESCAPE = re.compile(r'\\(?![0abtnvfre "\\/N_LPuxU])')
CONTROL_CHARS = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]|\t")


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def strip_code(text: str) -> str:
    """Kod bloklari va inline kod ichidagi `[[...]]` — havola emas."""
    return INLINE_CODE.sub(" ", FENCED.sub(" ", text))


def frontmatter_block(text: str) -> str | None:
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    if end == -1:
        return None
    return text[3:end]


def _control_chars_in(data: object) -> bool:
    stack: list[object] = [data]
    while stack:
        value = stack.pop()
        if isinstance(value, str):
            if CONTROL_CHARS.search(value):
                return True
        elif isinstance(value, dict):
            stack.extend(value.values())
            stack.extend(value.keys())
        elif isinstance(value, list):
            stack.extend(value)
    return False


def validate_yaml(block: str) -> str | None:
    if yaml is not None:
        try:
            loaded = yaml.safe_load(block)
        except Exception as exc:
            first = str(exc).splitlines()[0]
            hint = " [\\ dan keyin noto'g'ri belgi — / ishlatilsin]" if INVALID_ESCAPE.search(block) else ""
            return f"YAML xato: {first}{hint}"
        if loaded is not None and not isinstance(loaded, dict):
            return "YAML ildizi dict emas"
        if _control_chars_in(loaded):
            return "YAML escape qiymatni buzdi (ko'rinmas belgi) — \\ o'rniga / ishlatilsin"
        return None

    if INVALID_ESCAPE.search(block):
        return "yaroqsiz escape (\\ dan keyin noto'g'ri belgi) — / ishlatilsin"
    if re.search(r'"[^"\n]*\\t[^"\n]*"', block):
        return "qo'shtirnoq ichida \\t bor — yo'l buziladi (PyYAML yo'q, taxminiy tekshiruv)"
    return None


def frontmatter(text: str) -> dict | None:
    block = frontmatter_block(text)
    if block is None:
        return None
    data: dict = {}
    for raw in block.splitlines():
        line = raw.rstrip()
        if not line.strip() or line.lstrip().startswith("#") or line[0] in " \t-":
            continue
        if ":" not in line:
            data.setdefault("__badlines__", []).append(line)
            continue
        key, _, value = line.partition(":")
        data[key.strip()] = value.strip()
    return data


def auto_fix_index(root: Path, not_indexed: list[str]) -> int:
    """--write rejimi: INDEX.md jadvaliga tushib qolgan wiki qaydlarni avtomatik qo'shadi."""
    if not not_indexed:
        return 0
    index_path = root / "INDEX.md"
    if not index_path.is_file():
        return 0
    text = read(index_path)
    added_rows: list[str] = []
    for stem in not_indexed:
        note_path = root / "wiki" / f"{stem}.md"
        if not note_path.is_file():
            continue
        fm = frontmatter(read(note_path)) or {}
        desc = str(fm.get("description") or stem).strip().strip('"').strip("'")
        src = str(fm.get("source") or "wiki").strip().strip('"').strip("'")
        added_rows.append(f"| [[{stem}]] | {desc} | {src} |")

    if not added_rows:
        return 0

    new_text = text.rstrip() + "\n" + "\n".join(added_rows) + "\n"
    index_path.write_text(new_text, encoding="utf-8")
    return len(added_rows)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="vault-audit.py", description="Tyrion bilim qatlami auditi va Delivery Gate")
    parser.add_argument("root", nargs="?", default=".", help="Vault ildizi")
    parser.add_argument("--gate", action="store_true", help="ECC delivery-gate Stop hook rejimi (xato bo'lsa exit 1)")
    parser.add_argument("--write", action="store_true", help="INDEX.md doc-drift ni avtomatik to'ldirish")
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    wiki = root / "wiki"
    issues: list[str] = []

    notes = sorted(p for p in wiki.glob("*.md") if p.is_file())
    stems = {p.stem for p in notes}

    name_counter: Counter[str] = Counter()
    fm_missing: list[str] = []
    fm_bad: list[str] = []
    yaml_bad: list[str] = []
    few_links: list[str] = []
    for p in notes:
        text = read(p)
        fm = frontmatter(text)
        if fm is None:
            fm_bad.append(f"{p.name} (frontmatter yo'q)")
        else:
            if "__badlines__" in fm:
                fm_bad.append(f"{p.name} (YAML qatori buzilgan: {fm['__badlines__'][0][:40]})")
            yaml_error = validate_yaml(frontmatter_block(text) or "")
            if yaml_error:
                yaml_bad.append(f"{p.name} -> {yaml_error}")
            missing = [k for k in REQUIRED_FM if k not in fm or fm[k] in ("", '""')]
            if missing:
                fm_missing.append(f"{p.name} -> {', '.join(missing)}")
            declared = fm.get("name", "").strip().strip('"')
            if declared:
                name_counter[declared] += 1
        links = [m.strip() for m in WIKILINK.findall(strip_code(text))]
        if len(set(links)) < 2:
            few_links.append(f"{p.name} ({len(set(links))} ta)")

    all_md = [
        p for p in root.rglob("*.md")
        if not any(part in SKIP_DIRS for part in p.relative_to(root).parts)
    ]
    known = {p.stem for p in all_md}
    known |= {p.name for p in all_md}
    known |= {
        str(p.relative_to(root).with_suffix("")).replace("\\", "/").lower() for p in all_md
    }
    broken: dict[str, set[str]] = defaultdict(set)
    broken_src: dict[str, set[str]] = defaultdict(set)
    inbound: Counter[str] = Counter()
    for p in all_md:
        rel_path = p.relative_to(root)
        rel = rel_path.as_posix()
        first_part = rel_path.parts[0] if rel_path.parts else ""
        is_source = first_part in ("raw", "youtubedagilar", "vedio bilimlar", "templates")
        for target in WIKILINK.findall(strip_code(read(p))):
            t = target.strip().replace("\\", "/")
            stem = t.split("/")[-1]
            stem_no_ext = stem[:-3] if stem.lower().endswith(".md") else stem
            ok = (
                t in known
                or stem in known
                or stem_no_ext in known
                or t.lower() in known
                or stem_no_ext.lower() in known
                or (root / t).exists()
                or (root / f"{t}.md").exists()
            )
            if not ok:
                (broken_src if is_source else broken)[rel].add(target.strip())
            else:
                inbound[stem_no_ext] += 1

    orphans = sorted(s for s in stems if inbound.get(s, 0) == 0)

    index_text = read(root / "INDEX.md") if (root / "INDEX.md").exists() else ""
    not_indexed = sorted(s for s in stems if s not in index_text)
    if args.write and not_indexed:
        fixed_count = auto_fix_index(root, not_indexed)
        if fixed_count:
            print(f"✓ --write: INDEX.md ga {fixed_count} ta yangi qayd qo'shildi")
            index_text = read(root / "INDEX.md")
            not_indexed = sorted(s for s in stems if s not in index_text)

    claude = root / "CLAUDE.md"
    claude_lines = len(read(claude).splitlines()) if claude.exists() else 0
    if claude_lines > 300:
        issues.append(f"CLAUDE.md {claude_lines} qator (>300 limit)")

    log_path = root / "LOG.md"
    log_text = read(log_path) if log_path.exists() else ""
    line_rows = sum(1 for l in log_text.splitlines() if re.match(r"^\d{4}-\d{2}-\d{2} \|", l))
    table_rows = sum(1 for l in log_text.splitlines() if re.match(r"^\|\s*\d{4}-\d{2}-\d{2}\s*\|", l))
    if line_rows and table_rows:
        issues.append(f"LOG.md ikki format aralash: {line_rows} qator-uslub + {table_rows} jadval-uslub")

    if args.gate:
        today_str = date.today().isoformat()
        touched_today = [
            p for p in notes
            if datetime.fromtimestamp(p.stat().st_mtime).date().isoformat() == today_str
        ]
        if len(touched_today) >= 3 and today_str not in log_text:
            issues.append(f"Delivery Gate: bugun {len(touched_today)} wiki qayd o'zgargan, lekin LOG.md da '{today_str}' qatori yo'q")

    dupes = {n: c for n, c in name_counter.items() if c > 1}

    print(f"VAULT: {root}")
    print(f"wiki qaydlar: {len(notes)} | skanerlangan .md: {len(all_md)} | CLAUDE.md: {claude_lines} qator")
    print(f"frontmatter to'liq: {len(notes) - len(fm_missing) - len(fm_bad)}/{len(notes)}")

    def dump(title: str, rows: list[str]) -> None:
        print(f"\n[{title}] {len(rows)}")
        for r in rows[:40]:
            print(f"  - {r}")
        if len(rows) > 40:
            print(f"  ... yana {len(rows) - 40} ta")

    dump("FRONTMATTER BUZILGAN", fm_bad)
    dump("YAML XATO (Obsidian/Dataview ko'rmaydi)", yaml_bad)
    dump("FRONTMATTER MAYDON YETISHMAYDI", fm_missing)
    dump("WIKILINK < 2", few_links)
    dump("BUZILGAN WIKILINK (bilim qatlami)", [f"{f}: {', '.join(sorted(t))}" for f, t in sorted(broken.items())])
    dump("BUZILGAN WIKILINK (xom manba/andoza — axborot)", [
        f"{f}: {', '.join(sorted(t))}" for f, t in sorted(broken_src.items())
    ])
    dump("ORPHAN QAYD", orphans)
    dump("INDEX'DA YO'Q", not_indexed)
    dump("DUBLIKAT NOM", [f"{n} x{c}" for n, c in dupes.items()])
    dump("BOSHQA", issues)

    total = (
        len(fm_bad) + len(yaml_bad) + len(fm_missing) + len(few_links) + len(broken)
        + len(orphans) + len(not_indexed) + len(dupes) + len(issues)
    )
    print(f"\nJAMI MUAMMO (bilim qatlami): {total}"
          f" | xom manbadagi dangling havola: {sum(len(v) for v in broken_src.values())}")
    if args.gate and total > 0:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
