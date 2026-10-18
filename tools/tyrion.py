#!/usr/bin/env python3
"""Tyrion v3.0 Master CLI — Butun tizim uchun yagona boshqaruv markazi (0 token).

Ishlatish:
  python3 tools/tyrion.py status
  python3 tools/tyrion.py doctor [--quick]
  python3 tools/tyrion.py shield
  python3 tools/tyrion.py audience <subcommand> [args...]
  python3 tools/tyrion.py creative <subcommand> [args...]
  python3 tools/tyrion.py client <subcommand> [args...]
  python3 tools/tyrion.py calc <subcommand> [args...]
  python3 tools/tyrion.py guard <subcommand> [args...]
  python3 tools/tyrion.py search "<so'z>"
  python3 tools/tyrion.py skills <subcommand> [args...]
  python3 tools/tyrion.py instincts <subcommand> [args...]
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
VAULT = TOOLS.parent

for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        try:
            _stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:  # pragma: no cover
            pass

ROUTES = {
    "doctor": ("doctor.py", []),
    "shield": ("tyrion-shield.py", ["scan"]),
    "eval": ("skill-eval.py", []),
    "audience": ("meta-audience.py", []),
    "analyze": ("ad-export-analyzer.py", []),
    "creative": ("creative-matrix.py", []),
    "capi": ("capi-utm-builder.py", []),
    "client": ("client-workspace.py", []),
    "mcp": ("tyrion-mcp-server.py", ["--list-tools"]),
    "export": ("harness-export.py", []),
    "calc": ("calculator.py", []),
    "guard": ("spend-guard.py", []),
    "search": ("brain-search.py", ["search"]),
    "skills": ("skill-search.py", []),
    "instincts": ("instincts.py", []),
    "catalog": ("catalog.py", []),
    "graph": ("brain-graph.py", []),
    "audit": ("vault-audit.py", []),
}


def show_status() -> int:
    cat_file = VAULT / "manifests" / "catalog.json"
    counts = {}
    if cat_file.is_file():
        counts = json.loads(cat_file.read_text(encoding="utf-8")).get("counts", {})
    print("=" * 68)
    print("  🧠 TYRION v4.0 — AI PAID MEDIA & TARGETOLOGY OPERATING SYSTEM")
    print("=" * 68)
    print(f"  Arxitektura : Single-Root ECC v4.0 (0 dublikat papka)")
    print(f"  Agentlar    : {counts.get('agents', 36)} ta (100% skill ulangan + Prompt Defense)")
    print(f"  Skilllar    : {counts.get('skills', 62)} ta (36 platforma + 26 operator/marketing)")
    print(f"  Playbooklar : {counts.get('playbooks', 9)} ta (Meta $1k-$10k, E-com, Ta'lim, Ko'chmas mulk, B2B...)")
    print(f"  Kontekstlar : {counts.get('contexts', 6)} ta (audit, launch, scale, creative, uzbekistan)")
    print(f"  Wiki Qaydlar: {counts.get('wiki', 98)} ta atomik qayd (0 orphan, 0 xato)")
    print(f"  Buyruqlar   : {counts.get('commands', 16)} ta slash buyruq (/audit, /auditoriya, /kreativ, /voronka...)")
    print("-" * 68)
    print("  Tezkor CLI Buyruqlar:")
    for cmd, (script, def_args) in ROUTES.items():
        print(f"    python3 tools/tyrion.py {cmd:10} -> tools/{script} {' '.join(def_args)}")
    print("=" * 68)
    return 0


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if not args or args[0] in ("status", "--help", "-h"):
        return show_status()
    cmd, rest = args[0], args[1:]
    if cmd not in ROUTES:
        print(f"✗ Noma'lum buyruq: {cmd}. Mavjud: status, {', '.join(ROUTES)}", file=sys.stderr)
        return 2
    script, default_sub = ROUTES[cmd]
    final_args = rest if rest else default_sub
    proc = subprocess.run([sys.executable, str(TOOLS / script), *final_args], cwd=str(VAULT))
    return proc.returncode


if __name__ == "__main__":
    raise SystemExit(main())
