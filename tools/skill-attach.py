#!/usr/bin/env python3
"""skill-attach — skill'ni agentga ulash (ikki tomonlama, idempotent, dry-run bilan).

Muammo: ulanish ikki tomonlama bo'lishi kerak — skillda `attached_agents:`, agentda `skills:`.
Qo'lda yozilsa bir tomon unutiladi (skill yangilanadi, agent topmaydi) va buni hech kim sezmaydi.

Yechim: bitta buyruq ikki tomonni ham yozadi; frontmatter satr-satr tahrirlanadi (qolgan fayl
bayt-aniq qoladi); `--dry-run` rejasi ko'rsatiladi; `skill-search.py check` natijani tekshiradi.

Buyruqlar:
  py -3 tools\\skill-attach.py set copywriting --agents copy-writer
  py -3 tools\\skill-attach.py set social --agents social-content-writer --dry-run
  py -3 tools\\skill-attach.py set tyrion --standalone
  py -3 tools\\skill-attach.py remove social --agent social-content-writer
  py -3 tools\\skill-attach.py list

Chiqish: `+` qo'shildi, `~` yangilandi, `=` o'zgarmadi. Kod: 0 — bajarildi,
1 — topilmadi/mumkin emas, 2 — argument xatosi.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

VAULT = Path(__file__).resolve().parent.parent
SKILL_ROOT = VAULT / "skills"
SKILL_ROOTS = [SKILL_ROOT]
AGENT_ROOT = VAULT / "agents"
FRONTMATTER_RE = re.compile(r"\A---\r?\n(.*?)\r?\n---", re.DOTALL)

for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        try:
            _stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:  # pragma: no cover
            pass


# --------------------------------------------------------------------------- #
# Frontmatter (satr darajasida — format saqlanadi)
# --------------------------------------------------------------------------- #

def split_frontmatter(text: str) -> tuple[str, str] | None:
    match = FRONTMATTER_RE.match(text)
    if not match:
        return None
    return match.group(1), text[match.end():]


def read_key(block: str, key: str) -> list[str]:
    inline = re.search(rf"^{key}:\s*\[(.*?)\]\s*$", block, re.M)
    if inline:
        return [x.strip().strip("'\"") for x in inline.group(1).split(",") if x.strip()]
    block_form = re.search(rf"^{key}:\s*\n((?:\s*-\s*.+\n?)+)", block, re.M)
    if block_form:
        return [ln.strip().lstrip("-").strip().strip("'\"")
                for ln in block_form.group(1).splitlines() if ln.strip()]
    return []


def write_list(block: str, key: str, values: list[str]) -> tuple[str, str]:
    """`key: [a, b]` yozadi. Qaytaradi: (yangi blok, amal: '=' | '+' | '~')."""
    line = f"{key}: [{', '.join(values)}]" if values else f"{key}: []"
    inline = re.search(rf"^{key}:\s*\[.*?\]\s*$", block, re.M)
    if inline:
        if inline.group(0) == line:
            return block, "="
        return block[:inline.start()] + line + block[inline.end():], "~"
    block_form = re.search(rf"^{key}:\s*\n((?:\s*-\s*.+\n?)+)", block, re.M)
    if block_form:
        suffix = "\n" if block_form.group(0).endswith("\n") else ""
        return block[:block_form.start()] + line + suffix + block[block_form.end():], "~"
    sep = "" if block.endswith("\n") else "\n"
    return f"{block}{sep}{line}", "+"


def write_flag(block: str, key: str, value: bool) -> tuple[str, str]:
    line = f"{key}: {'true' if value else 'false'}"
    existing = re.search(rf"^{key}:\s*\S+\s*$", block, re.M)
    if existing:
        if existing.group(0) == line:
            return block, "="
        return block[:existing.start()] + line + block[existing.end():], "~"
    if not value:
        return block, "="
    sep = "" if block.endswith("\n") else "\n"
    return f"{block}{sep}{line}", "+"


def drop_key(block: str, key: str) -> tuple[str, str]:
    inline = re.search(rf"^{key}:\s*\[.*?\]\s*\n?", block, re.M)
    if inline:
        return block[:inline.start()] + block[inline.end():], "~"
    block_form = re.search(rf"^{key}:\s*\n((?:\s*-\s*.+\n?)+)", block, re.M)
    if block_form:
        return block[:block_form.start()] + block[block_form.end():], "~"
    return block, "="


def update_file(path: Path, changes: list[tuple[str, object]], dry_run: bool) -> list[str]:
    """changes: [(key, [values] | True/False | None)] — None = kalitni o'chirish."""
    text = path.read_text(encoding="utf-8")
    parts = split_frontmatter(text)
    if parts is None:
        raise ValueError(f"{path}: frontmatter yo'q")
    block, rest = parts
    notes: list[str] = []
    for key, value in changes:
        if value is None:
            block, action = drop_key(block, key)
        elif isinstance(value, bool):
            block, action = write_flag(block, key, value)
        else:
            block, action = write_list(block, key, list(value))  # type: ignore[arg-type]
        notes.append(f"{action} {key}={value if not isinstance(value, bool) else str(value).lower()}")
    new_text = f"---\n{block}\n---{rest}"
    rel = path.relative_to(VAULT).as_posix()
    if new_text != text and not dry_run:
        path.write_text(new_text, encoding="utf-8")
    return [f"  {rel}: " + ", ".join(notes)]


# --------------------------------------------------------------------------- #
# Reyestr
# --------------------------------------------------------------------------- #

def find_skill(name: str) -> Path | None:
    for root in SKILL_ROOTS:
        candidate = root / name / "SKILL.md"
        if candidate.is_file():
            return candidate
    return None


def agent_path(name: str) -> Path | None:
    candidate = AGENT_ROOT / f"{name}.md"
    return candidate if candidate.is_file() else None


def list_all() -> int:
    print("Skill → agent ulanishlari:")
    op_count = 0
    plat_count = 0
    if SKILL_ROOT.is_dir():
        for skill_dir in sorted(p for p in SKILL_ROOT.iterdir() if p.is_dir()):
            path = skill_dir / "SKILL.md"
            if not path.is_file():
                continue
            layer = "platform" if (skill_dir.name == "ads" or skill_dir.name.startswith("ads-")) else "operator"
            parts = split_frontmatter(path.read_text(encoding="utf-8", errors="replace"))
            block = parts[0] if parts else ""
            agents = read_key(block, "attached_agents")
            standalone = re.search(r"^standalone:\s*true\s*$", block, re.M) is not None
            state = ", ".join(agents) if agents else ("standalone" if standalone else "— ulanmagan")
            print(f"  {layer:9} {skill_dir.name:28} → {state}")
            if layer == "operator":
                op_count += 1
            else:
                plat_count += 1
    print(f"Operator skill: {op_count} · Platforma skill: {plat_count}")
    return 0


# --------------------------------------------------------------------------- #
# Buyruqlar
# --------------------------------------------------------------------------- #

def cmd_set(args: argparse.Namespace) -> int:
    skill_path = find_skill(args.skill)
    if skill_path is None:
        print(f"✗ skill topilmadi: {args.skill}")
        return 1
    targets = [a.strip() for a in (args.agents or "").split(",") if a.strip()]
    missing = [a for a in targets if agent_path(a) is None]
    if missing:
        print(f"✗ agent charteri topilmadi: {', '.join(missing)} (agents/)")
        return 1
    if not targets and not args.standalone:
        print("✗ --agents yoki --standalone kerak")
        return 2

    changes: list[str] = []
    if targets:
        parts = split_frontmatter(skill_path.read_text(encoding="utf-8"))
        current = read_key(parts[0] if parts else "", "attached_agents")
        merged = sorted(set(current) | set(targets))
        changes += update_file(skill_path, [("attached_agents", merged),
                                            ("standalone", None)], args.dry_run)
    if args.standalone:
        changes += update_file(skill_path, [("attached_agents", None),
                                            ("standalone", True)], args.dry_run)

    for agent in targets:
        path = agent_path(agent)
        assert path is not None
        parts = split_frontmatter(path.read_text(encoding="utf-8"))
        current = read_key(parts[0] if parts else "", "skills")
        merged = sorted(set(current) | {args.skill})
        changes += update_file(path, [("skills", merged)], args.dry_run)

    head = "REJA (dry-run)" if args.dry_run else "BAJARILDI"
    print(f"{head}: {args.skill} → {', '.join(targets) or 'standalone'}")
    print("\n".join(changes))
    if not args.dry_run:
        print("Tekshiruv: py -3 tools\\skill-search.py check")
    return 0


def cmd_remove(args: argparse.Namespace) -> int:
    skill_path = find_skill(args.skill)
    if skill_path is None:
        print(f"✗ skill topilmadi: {args.skill}")
        return 1
    parts = split_frontmatter(skill_path.read_text(encoding="utf-8"))
    current = [a for a in read_key(parts[0] if parts else "", "attached_agents") if a != args.agent]
    changes = update_file(skill_path, [("attached_agents", current)], args.dry_run)
    path = agent_path(args.agent)
    if path is not None:
        parts = split_frontmatter(path.read_text(encoding="utf-8"))
        keep = [s for s in read_key(parts[0] if parts else "", "skills") if s != args.skill]
        changes += update_file(path, [("skills", keep)], args.dry_run)
    print(f"{'REJA (dry-run)' if args.dry_run else 'BAJARILDI'}: {args.skill} ✂ {args.agent}")
    print("\n".join(changes))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="skill-attach.py", description="skill ↔ agent ulash")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("set", help="skill'ni agent(lar)ga ulash")
    p.add_argument("skill")
    p.add_argument("--agents", default="", help="vergul bilan: copy-writer,social-content-writer")
    p.add_argument("--standalone", action="store_true", help="agentga ulanmaydi (konduktor/umumiy skill)")
    p.add_argument("--dry-run", action="store_true")
    p.set_defaults(func=cmd_set)

    p = sub.add_parser("remove", help="bitta agentdan uzish")
    p.add_argument("skill")
    p.add_argument("--agent", required=True)
    p.add_argument("--dry-run", action="store_true")
    p.set_defaults(func=cmd_remove)

    p = sub.add_parser("list", help="operator skilllar va ulanishlari")
    p.set_defaults(func=lambda _a: list_all())

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
