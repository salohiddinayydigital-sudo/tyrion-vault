#!/usr/bin/env python3
"""Tyrion hook va buyruqlarini harness sozlamalariga o'rnatadi (idempotent).

Kanonik manba: `hooks/hooks.json` va `commands/*.md`. Bu skript `{{VAULT}}` o'rniga haqiqiy
yo'lni qo'yadi, `<target>/.claude/settings.json` ga hook'larni **qo'shadi** (mavjudlarini
o'chirmaydi, o'zinikini takrorlamaydi) va buyruqlarni `<target>/.claude/commands/` ga
ko'chiradi. Yozishdan oldin `settings.json.bak` nusxasi olinadi.

Ishlatish:
  py -3 tools\\install-hooks.py --dry-run          # nima o'zgarishini ko'rsatadi
  py -3 tools\\install-hooks.py                    # vault .claude/
  py -3 tools\\install-hooks.py --target <papka>   # boshqa loyiha (masalan claude-ads-main)

Chiqish kodi: 0 — o'rnatildi yoki allaqachon bor, 1 — xato.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
VAULT = TOOLS.parent
HOOKS_JSON = VAULT / "hooks" / "hooks.json"

for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        try:
            _stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:  # pragma: no cover
            pass


def _substitute(node: object, needle: str, value: str) -> object:
    """Tuzilmadagi matnlarda `needle` ni almashtiradi.

    MUHIM: almashtirish **parse qilingandan keyin** bajariladi, xom matnda emas.
    Xom matnda qilinsa `path\\to\\vault` JSON ichida qo'yilganda `\\t` TAB belgisiga aylanadi
    (2026-09-16 da dry-run aynan shuni tutdi — YAML frontmatter'dagi xatoning bir turi).
    """
    if isinstance(node, str):
        return node.replace(needle, value)
    if isinstance(node, dict):
        return {key: _substitute(item, needle, value) for key, item in node.items()}
    if isinstance(node, list):
        return [_substitute(item, needle, value) for item in node]
    return node


def build_config(target_root: Path, vault: Path) -> dict:
    """Kanonik hook'larni o'qib, `{{VAULT}}` ni almashtiradi."""
    try:
        data = json.loads(HOOKS_JSON.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"✗ hooks/hooks.json buzilgan: {exc}")
    return _substitute(data, "{{VAULT}}", str(vault))  # type: ignore[return-value]


def merge(settings: dict, canonical: dict) -> tuple[dict, list[str]]:
    """Mavjud sozlamalarga hook'larni qo'shadi. Qaytaradi: (yangi sozlama, qo'shilganlar)."""
    added: list[str] = []
    hooks = settings.setdefault("hooks", {})

    for event, groups in canonical.get("hooks", {}).items():
        existing: list[dict] = hooks.setdefault(event, [])
        known = {
            hook.get("command")
            for group in existing
            for hook in group.get("hooks", [])
        }
        for group in groups:
            new_hooks = [h for h in group.get("hooks", []) if h.get("command") not in known]
            if not new_hooks:
                continue
            existing.append({"matcher": group.get("matcher", ""), "hooks": new_hooks})
            for hook in new_hooks:
                added.append(f"{event}: {hook['command']}")
                known.add(hook.get("command"))

    return settings, added


def sync_commands(target_root: Path, dry_run: bool) -> list[str]:
    """`commands/*.md` ni `<target>/.claude/commands/` ga ko'chiradi (kanonik → nusxa).

    Nusxa bir xil bo'lsa tegmaydi (idempotent). Qaytaradi: o'zgargan fayllar ro'yxati.
    """
    source = VAULT / "commands"
    if not source.is_dir():
        return []
    destination = target_root / ".claude" / "commands"
    changed: list[str] = []
    for path in sorted(source.glob("*.md")):
        target = destination / path.name
        # Bayt-aniq taqqoslash: `write_text` Windows'da \n ni \r\n ga aylantirib,
        # nusxani "farqli" qilib ko'rsatardi (drift noto'g'ri signali).
        if target.is_file() and target.read_bytes().replace(b'\r\n', b'\n') == path.read_bytes().replace(b'\r\n', b'\n'):
            continue
        changed.append(f"commands/{path.name}")
        if not dry_run:
            destination.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)
    return changed


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="install-hooks.py", description="Tyrion hook'larini o'rnatish")
    parser.add_argument("--target", default=str(VAULT), help="loyiha ildizi (default: vault)")
    parser.add_argument("--dry-run", action="store_true", help="yozmasdan ko'rsatadi")
    parser.add_argument("--vault", default=str(VAULT), help="Tyrion ildizi (hook yo'llari uchun)")
    parser.add_argument("--no-commands", action="store_true", help="commands/ ni ko'chirmaslik")
    args = parser.parse_args(argv)

    if not HOOKS_JSON.is_file():
        print(f"✗ {HOOKS_JSON} topilmadi")
        return 1

    target_root = Path(args.target).resolve()
    settings_path = target_root / ".claude" / "settings.json"
    settings_path.parent.mkdir(parents=True, exist_ok=True)

    settings: dict = {}
    if settings_path.is_file():
        try:
            settings = json.loads(settings_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            print(f"✗ mavjud settings.json buzilgan ({exc}) — qo'lda tuzating")
            return 1

    canonical = build_config(target_root, Path(args.vault).resolve())
    updated, added = merge(settings, canonical)
    commands = [] if args.no_commands else sync_commands(target_root, args.dry_run)

    if not added and not commands:
        print(f"✓ hook va buyruqlar allaqachon joyida: {target_root}")
        return 0

    if added:
        print(f"Qo'shiladigan hook'lar ({len(added)}):")
        for line in added:
            print(f"  + {line}")
    if commands:
        print(f"Ko'chiriladigan buyruqlar ({len(commands)}): " + ", ".join(commands))

    if args.dry_run:
        print(f"\n· --dry-run: {target_root} ichida hech narsa yozilmadi")
        return 0

    if added:
        if settings_path.is_file():
            backup = settings_path.with_suffix(".json.bak")
            shutil.copy2(settings_path, backup)
            print(f"\n· nusxa: {backup.name}")
        settings_path.write_text(json.dumps(updated, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"✓ settings yozildi: {settings_path}")
    print("✓ tayyor")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
