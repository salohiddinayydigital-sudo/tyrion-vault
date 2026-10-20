#!/usr/bin/env python3
"""Tyrion hook'lari — deterministik nazorat va ECC hook profillari (LLM hukmisiz).

Qo'llab-quvvatlanadigan muhit o'zgaruvchilari (ECC 2.2 mos):
  TYRION_HOOK_PROFILE   : minimal | standard | strict (default: standard)
  TYRION_DISABLED_HOOKS : vergul bilan ajratilgan hook ID ro'yxati (session:brief,pre:guard,post:ingest,stop:dod)

Buyruqlar:
  py -3 hooks/tyrion-hook.py brief     # sessiya boshi: holat + instinktlar (SessionStart, ID: session:brief)
  py -3 hooks/tyrion-hook.py guard     # muhim konfiguratsiya himoyasi (PreToolUse, ID: pre:guard)
  py -3 hooks/tyrion-hook.py ingest    # ingest protokoli: INDEX/LOG/graf (PostToolUse, ID: post:ingest)
  py -3 hooks/tyrion-hook.py dod       # topshirish darvozasi: doctor + ingest + gate (Stop, ID: stop:dod)

Chiqish kodi: 0 — joyida, 1 — qoida buzilgan (hook bloklaydi), 2 — xato.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import date, datetime
from pathlib import Path

HOOKS = Path(__file__).resolve().parent
VAULT = HOOKS.parent
TOOLS = VAULT / "tools"

sys.path.insert(0, str(TOOLS))
import catalog as cat  # noqa: E402

for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        try:
            _stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:  # pragma: no cover
            pass


def get_profile() -> str:
    raw = os.environ.get("TYRION_HOOK_PROFILE", "standard").strip().lower()
    return raw if raw in ("minimal", "standard", "strict") else "standard"


def is_disabled(hook_id: str) -> bool:
    disabled = {
        x.strip().lower()
        for x in os.environ.get("TYRION_DISABLED_HOOKS", "").split(",")
        if x.strip()
    }
    if hook_id.lower() in disabled:
        return True
    profile = get_profile()
    if profile == "minimal" and hook_id in ("post:ingest", "pre:guard"):
        return True
    return False


def run(cmd: list[str], timeout: int = 120) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=str(VAULT), capture_output=True, text=True,
                          encoding="utf-8", errors="replace", timeout=timeout)


# --------------------------------------------------------------------------- #
# brief — sessiya boshi (ID: session:brief)
# --------------------------------------------------------------------------- #

def cmd_brief(_args: argparse.Namespace) -> int:
    if is_disabled("session:brief"):
        return 0
    data = cat.scan()
    notes = [VAULT / i["path"] for i in data["items"]["wiki"]]
    total_skills = data["counts"].get("skills", 0) + data["counts"].get("skills.marketing", 0)
    instincts_path = VAULT / "manifests" / "instincts.json"
    instincts_count = 0
    if instincts_path.is_file():
        try:
            instincts_count = len(json.loads(instincts_path.read_text(encoding="utf-8")).get("instincts", []))
        except Exception:
            pass

    bits: list[str] = [
        f"Tyrion: wiki {data['counts']['wiki']} · agent {data['counts']['agents']} · "
        f"skill {total_skills} · instinkt {instincts_count} · profil {get_profile()}"
    ]

    graph = VAULT / "graphify-out" / "graph.json"
    if graph.is_file():
        newest = max((p.stat().st_mtime for p in notes if p.is_file()), default=0)
        if newest > graph.stat().st_mtime:
            days = (newest - graph.stat().st_mtime) / 86400
            bits.append(f"graf {days:.0f} kun eski → `py -3 tools/brain-graph.py build`")

    drift = [m for m in data["mirrors"] if m["status"] != "identical"]
    if drift:
        bits.append(f"⚠ {len(drift)} nusxada drift → `catalog.py sync-mirrors`")

    print(" | ".join(bits))
    return 0


# --------------------------------------------------------------------------- #
# guard — konfiguratsiya va generatsiya reestrini himoya qilish (ID: pre:guard)
# --------------------------------------------------------------------------- #

PROTECTED_GENERATED = {"manifests/catalog.json", "graphify-out/graph.json"}


def cmd_guard(args: argparse.Namespace) -> int:
    if is_disabled("pre:guard"):
        return 0
    target = (args.target or "").replace("\\", "/").strip()
    if any(target.endswith(p) for p in PROTECTED_GENERATED):
        msg = f"⚠ HIMOYA (pre:guard): '{target}' generatsiya fayli — qo'lda tahrirlamang (`catalog.py build` / `brain-graph.py build` ishlating)."
        print(msg)
        return 0 if args.warn_only or get_profile() != "strict" else 2
    if not args.quiet:
        print("✓ pre:guard: ruxsat berildi")
    return 0


# --------------------------------------------------------------------------- #
# ingest — CLAUDE.md ingest protokoli nazorati (ID: post:ingest)
# --------------------------------------------------------------------------- #

def _today() -> str:
    return date.today().isoformat()


def cmd_ingest(args: argparse.Namespace) -> int:
    if is_disabled("post:ingest"):
        return 0
    problems: list[str] = []
    data = cat.scan()
    notes = data["items"]["wiki"]

    index_path = VAULT / "INDEX.md"
    index_text = index_path.read_text(encoding="utf-8") if index_path.is_file() else ""
    not_indexed = [n["name"] for n in notes if n["name"] not in index_text]

    log_path = VAULT / "LOG.md"
    log_text = log_path.read_text(encoding="utf-8") if log_path.is_file() else ""
    today = _today()

    today_notes = [
        n for n in notes
        if datetime.fromisoformat(n["updated"]).date().isoformat() == today
    ]
    if today_notes and today not in log_text:
        problems.append(f"bugun {len(today_notes)} qayd yozilgan, LOG.md da '{today}' qatori yo'q")

    for name in not_indexed:
        problems.append(f"INDEX.md da yo'q: {name}")

    if not problems:
        script = TOOLS / "brain-graph.py"
        if script.is_file():
            try:
                run([sys.executable, str(script), "build"], timeout=60)
            except Exception:
                pass
        if not args.quiet:
            print(f"✓ ingest protokoli joyida ({len(notes)} qayd, INDEX qamrovi to'liq; graf yangilandi)")
        return 0

    print("⚠ INGEST PROTOKOLI BUZILGAN (CLAUDE.md: raw → wiki → INDEX → LOG):")
    for line in problems[:8]:
        print(f"  - {line}")
    if len(problems) > 8:
        print(f"  ... yana {len(problems) - 8} ta")
    print("  Tuzatish: `py -3 tools/vault-audit.py --write` va LOG.md tepasiga sana muhrlang.")
    strict = (get_profile() == "strict") and not args.warn_only
    return 1 if (not args.warn_only or strict) else 0


# --------------------------------------------------------------------------- #
# dod — topshirish darvozasi (doctor + ingest + vault-audit --gate, ID: stop:dod)
# --------------------------------------------------------------------------- #

def cmd_dod(args: argparse.Namespace) -> int:
    if is_disabled("stop:dod"):
        return 0
    failures: list[str] = []

    try:
        proc = run([sys.executable, str(TOOLS / "doctor.py"), "--quick", "--json"], timeout=180)
        payload = json.loads(proc.stdout or "{}")
        for check in payload.get("checks", []):
            if check["status"] == "fail":
                failures.append(f"{check['check']}: {check['detail']}")
    except Exception as exc:
        failures.append(f"doctor ishga tushmadi: {exc}")

    ingest = cmd_ingest(argparse.Namespace(warn_only=True, quiet=True))
    if ingest != 0:
        failures.append("ingest protokoli buzilgan (batafsil: hooks/tyrion-hook.py ingest)")

    gate_proc = run([sys.executable, str(TOOLS / "vault-audit.py"), str(VAULT), "--gate"], timeout=120)
    if gate_proc.returncode != 0:
        failures.append("vault-audit --gate: bilim qatlami yoki LOG.md delivery gate yopiq")

    if not failures:
        print("✓ topshirish darvozasi: to'siq yo'q")
        return 0

    print("✗ TOPSHIRISH DARVOZASI YOPIQ:")
    for line in failures:
        print(f"  - {line}")
    if get_profile() == "strict" and not args.warn_only:
        return 1
    return 0 if args.warn_only else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="tyrion-hook.py", description="Tyrion deterministik hook'lari")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("brief", help="sessiya boshi holati (session:brief)").set_defaults(func=cmd_brief)

    guard = sub.add_parser("guard", help="generatsiya va config himoyasi (pre:guard)")
    guard.add_argument("--target", default="", help="tekshirilayotgan fayl yo'li")
    guard.add_argument("--warn-only", action="store_true")
    guard.add_argument("--quiet", action="store_true")
    guard.set_defaults(func=cmd_guard)

    ingest = sub.add_parser("ingest", help="ingest protokoli nazorati (post:ingest)")
    ingest.add_argument("--warn-only", action="store_true", help="xato kodisiz, faqat ogohlantirish")
    ingest.add_argument("--quiet", action="store_true", help="muammo bo'lmasa jim turadi")
    ingest.set_defaults(func=cmd_ingest)

    dod = sub.add_parser("dod", help="topshirish darvozasi (stop:dod)")
    dod.add_argument("--warn-only", action="store_true",
                     help="faqat ogohlantiradi (Stop hook uchun — ishni bloklamaydi)")
    dod.set_defaults(func=cmd_dod)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
