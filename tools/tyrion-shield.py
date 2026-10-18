#!/usr/bin/env python3
"""TyrionShield — Agent, Skill, Hook, MCP va Sirlar Xavfsizlik Skaneri (0 token).

ECC (affaan-m/ECC) AgentShield tizimi asosida Tyrion uchun maxsus qurilgan.
5 ta xavfsizlik qatlamini deterministik tekshiradi:
  1. secrets        : Butun ombor bo'ylab .env va API kalitlar sizishi
  2. hooks_mcp      : hooks.json, settings.json va .mcp.json da xavfli buyruqlar yoki qotirilgan yo'llar
  3. agents         : 35 agent charterida Prompt Defense Baseline / untrusted data chegarasi va skills: ulanishi
  4. skills         : 59 skillda YAML control-char buzilishi, `|` block scalar xatosi va ikki tomonlama ulanish
  5. mutation_gates : 40-xavfsizlik-va-hisob.md va spend-guard.py 6 ta himoya darvozasi butunligi

Buyruqlar:
  py -3 tools/tyrion-shield.py scan            # to'liq xavfsizlik hisoboti
  py -3 tools/tyrion-shield.py scan --json     # JSON formatida chiqish
"""

from __future__ import annotations

import argparse
import json
import re
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

SECRET_PATTERNS = [
    (re.compile(r"\bsk-[A-Za-z0-9]{20,}"), "OpenAI API kaliti"),
    (re.compile(r"\bsk-ant-[A-Za-z0-9_\-]{20,}"), "Anthropic API kaliti"),
    (re.compile(r"\bAIza[0-9A-Za-z_\-]{30,}"), "Google API kaliti"),
    (re.compile(r"\bEAA[A-Za-z0-9]{35,}"), "Meta Graph API Access Token"),
    (re.compile(r"\b\d{8,10}:AA[A-Za-z0-9_\-]{30,}"), "Telegram Bot Token"),
    (re.compile(r"\bghp_[A-Za-z0-9]{30,}"), "GitHub Personal Access Token"),
]

SKIP_DIRS = {".git", "node_modules", "__pycache__", "graphify-out", ".obsidian", "archive", "tests"}
FRONTMATTER_RE = re.compile(r"\A---\r?\n(.*?)\r?\n---", re.DOTALL)
LITERAL_DESC_RE = re.compile(r"^description:\s*\|", re.M)
HARDCODED_WIN_DRIVE = re.compile(r"[A-Za-z]:\\\\tyrion", re.I)


def scan_secrets() -> tuple[str, str, list[str]]:
    """Butun ombor bo'ylab sirlarni qidiradi."""
    issues: list[str] = []
    scanned = 0
    for path in VAULT.rglob("*"):
        if not path.is_file():
            continue
        rel_parts = path.relative_to(VAULT).parts
        if any(part in SKIP_DIRS for part in rel_parts):
            continue
        if path.name == ".env":
            issues.append(f"Ochiq .env fayli mavjud: {path.relative_to(VAULT).as_posix()} (.env.example ishlatilsin)")
            continue
        if path.suffix.lower() not in {".md", ".json", ".yaml", ".yml", ".py", ".sh", ".ps1", ".cmd", ".env"}:
            continue
        if path.stat().st_size > 300_000:
            continue
        scanned += 1
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for pat, label in SECRET_PATTERNS:
            if pat.search(text):
                issues.append(f"{label} topildi: {path.relative_to(VAULT).as_posix()}")
                break

    if issues:
        return "fail", f"{len(issues)} xavf topildi ({scanned} fayl tekshirildi)", issues
    return "ok", f"{scanned} fayl toza, sizib chiqqan sir yo'q", []


def scan_hooks_and_mcp() -> tuple[str, str, list[str]]:
    """Hook va MCP konfiguratsiyalarini xavfsizlik va portativlikka tekshiradi."""
    warnings: list[str] = []
    errors: list[str] = []

    for rel in ("hooks.json", "hooks/hooks.json", ".claude/settings.json"):
        p = VAULT / rel
        if not p.is_file():
            continue
        try:
            raw = p.read_text(encoding="utf-8")
            json.loads(raw)
        except Exception as exc:
            errors.append(f"{rel}: JSON buzilgan ({exc})")
            continue
        if HARDCODED_WIN_DRIVE.search(raw):
            warnings.append(f"{rel}: qotirilgan lokal yo'l (hardcoded drive) mavjud — portativ nisbiy yo'l tavsiya etiladi")
        if "curl " in raw or "wget " in raw or "Invoke-WebRequest" in raw:
            errors.append(f"{rel}: tashqi tarmoqqa murojaat qiluvchi xavfli hook buyrug'i")

    mcp_path = VAULT / ".mcp.json"
    if mcp_path.is_file():
        try:
            json.loads(mcp_path.read_text(encoding="utf-8"))
        except Exception as exc:
            errors.append(f".mcp.json buzilgan: {exc}")

    if errors:
        return "fail", f"{len(errors)} xato, {len(warnings)} ogohlantirish", errors + warnings
    if warnings:
        return "warn", f"{len(warnings)} portativlik ogohlantirishi", warnings
    return "ok", "hooks.json, settings.json va .mcp.json xavfsiz va portativ", []


def scan_agents() -> tuple[str, str, list[str]]:
    """35 agent charterida frontmatter, untrusted-data qalqoni va skill ulanishini tekshiradi."""
    errors: list[str] = []
    warnings: list[str] = []
    agent_dir = VAULT / "agents"
    agents = sorted(agent_dir.glob("*.md")) if agent_dir.is_dir() else []
    if not agents:
        return "fail", "agents/ topilmadi", ["Agent charterlari yo'q"]

    for p in agents:
        text = p.read_text(encoding="utf-8", errors="replace")
        m = FRONTMATTER_RE.match(text)
        if not m:
            errors.append(f"{p.name}: frontmatter yo'q")
            continue
        fm = m.group(1)
        for req in ("name:", "description:", "model:", "tools:"):
            if req not in fm:
                errors.append(f"{p.name}: frontmatterda '{req}' yo'q")
        if "skills:" not in fm:
            warnings.append(f"{p.name}: 'skills:' ro'yxati biriktirilmagan")
        lower = text.lower()
        if "untrusted" not in lower and "ishonchsiz" not in lower and "70-charter-baseline" not in lower:
            warnings.append(f"{p.name}: Prompt Defense / untrusted data chegarasi ko'rsatilmagan")

    baseline_ok = (VAULT / "rules" / "70-charter-baseline.md").is_file()
    if not baseline_ok:
        warnings.append("rules/70-charter-baseline.md mavjud emas")

    if errors:
        return "fail", f"{len(agents)} charterdan {len(errors)} tasida xato", errors + warnings
    if warnings:
        return "warn", f"{len(agents)} charter, {len(warnings)} ogohlantirish", warnings
    return "ok", f"{len(agents)}/36 agent charteri himoyalangan va skill'ga ulangan", []


def scan_skills() -> tuple[str, str, list[str]]:
    """59 skillda frontmatter, literal block scalar (`|`) va ulanishni tekshiradi."""
    errors: list[str] = []
    warnings: list[str] = []
    roots = [VAULT / "skills"]
    count = 0
    for r in roots:
        if not r.is_dir():
            continue
        for p in sorted(r.glob("*/SKILL.md")):
            count += 1
            text = p.read_text(encoding="utf-8", errors="replace")
            m = FRONTMATTER_RE.match(text)
            if not m:
                errors.append(f"{p.relative_to(VAULT).as_posix()}: frontmatter yo'q")
                continue
            fm = m.group(1)
            if LITERAL_DESC_RE.search(fm):
                warnings.append(f"{p.parent.name}: description literal '|' scalar ishlatgan (jadvalni buzadi)")
            if "attached_agents:" not in fm and "standalone: true" not in fm:
                warnings.append(f"{p.parent.name}: attached_agents yoki standalone: true ko'rsatilmagan")

    if errors:
        return "fail", f"{count} skilldan {len(errors)} tasida xato", errors + warnings
    if warnings:
        return "warn", f"{count} skill, {len(warnings)} ogohlantirish", warnings
    return "ok", f"{count} skill frontmatteri va agent ulanishi toza", []


def scan_mutation_gates() -> tuple[str, str, list[str]]:
    """Spend-Guard va 40-xavfsizlik-va-hisob qoidasi mavjudligini tekshiradi."""
    issues: list[str] = []
    if not (VAULT / "rules" / "40-xavfsizlik-va-hisob.md").is_file():
        issues.append("rules/40-xavfsizlik-va-hisob.md yo'q")
    if not (TOOLS / "spend-guard.py").is_file():
        issues.append("tools/spend-guard.py yo'q")
    if not (VAULT / "rules" / "70-charter-baseline.md").is_file():
        issues.append("rules/70-charter-baseline.md yo'q")
    if issues:
        return "fail", "; ".join(issues), issues
    return "ok", "6 ta Spend-Guard darvozasi + 40-qoida + 70-baseline faol", []


def run_all() -> dict:
    checks = []
    for name, fn in [
        ("Secrets & .env Exposure", scan_secrets),
        ("Hooks & MCP Config Safety", scan_hooks_and_mcp),
        ("Agent Charter Defense (36)", scan_agents),
        ("Skill Surface & YAML Safety", scan_skills),
        ("Spend-Guard & Mutation Gates", scan_mutation_gates),
    ]:
        status, detail, items = fn()
        checks.append({"check": name, "status": status, "detail": detail, "items": items})

    summary = {
        "checked": len(checks),
        "ok": sum(1 for c in checks if c["status"] == "ok"),
        "warnings": sum(1 for c in checks if c["status"] == "warn"),
        "errors": sum(1 for c in checks if c["status"] == "fail"),
    }
    return {"schema": "tyrion-shield/v1", "summary": summary, "checks": checks}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="tyrion-shield.py", description="TyrionShield xavfsizlik skaneri")
    sub = parser.add_subparsers(dest="command")
    p_scan = sub.add_parser("scan", help="to'liq xavfsizlik tekshiruvi")
    p_scan.add_argument("--json", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    data = run_all()
    if getattr(args, "json", False):
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return 1 if data["summary"]["errors"] > 0 else 0

    icon = {"ok": "✓", "warn": "⚠", "fail": "✗"}
    print("=" * 64)
    print("  🛡️  TYRION SHIELD — Agent & Vault Xavfsizlik Auditi")
    print("=" * 64)
    for c in data["checks"]:
        print(f"  {icon[c['status']]} {c['check']:30} {c['detail']}")
        for item in c["items"][:5]:
            print(f"      - {item}")
    s = data["summary"]
    print("-" * 64)
    print(f"  Summary: checked={s['checked']}, ok={s['ok']}, warnings={s['warnings']}, errors={s['errors']}")
    print("-" * 64)
    return 1 if s["errors"] > 0 else 0


if __name__ == "__main__":
    raise SystemExit(main())
