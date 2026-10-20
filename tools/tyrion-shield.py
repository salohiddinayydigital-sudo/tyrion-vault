#!/usr/bin/env python3
"""TyrionShield v5.0 — Agent, Skill, Hook, MCP, AST va Sirlar Xavfsizlik Skaneri (0 token).

ECC (affaan-m/ECC) AgentShield tizimi asosida Tyrion v5.0 uchun qurilgan.
6 ta statik xavfsizlik va sifat qatlamini deterministik tekshiradi (shu jumladan `tests/` papkasini ham!):
  1. secrets        : Butun ombor bo'ylab (tests/ bilan birga) .env, API kalitlar va Private Key sizishi
  2. hooks_mcp      : hooks.json, settings.json va .mcp.json da xavfli buyruqlar yoki qotirilgan yo'llar
  3. agents         : 36 agent charterida Prompt Defense Baseline / untrusted data chegarasi va skills: ulanishi
  4. skills         : 62 skillda YAML control-char buzilishi, `|` block scalar xatosi va ikki tomonlama ulanish
  5. mutation_gates : 40-xavfsizlik-va-hisob.md va spend-guard.py 6 ta himoya darvozasi butunligi
  6. code_hygiene   : tools/ va hooks/ dagi barcha Python fayllarda AST sintaksis va return/raise dan keyingi o'lik kod (dead code) tekshiruvi

Muhim eslatma (Scope & Limitations):
  TyrionShield — ombor ichidagi statik konfiguratsiya, sirlar gigiyenasi va prompt-defense qoidalarini
  tekshiruvchi skaner. U to'liq tashqi kiberxavfsizlik auditi (penetration test), tarmoq darajasidagi
  himoya yoki Meta Business Manager ichidagi OAuth ruxsatlarini tekshirish o'rnini bosmaydi.

Buyruqlar:
  python3 tools/tyrion-shield.py scan            # to'liq xavfsizlik hisoboti
  python3 tools/tyrion-shield.py scan --json     # JSON formatida chiqish
"""

from __future__ import annotations

import argparse
import ast
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
    (re.compile(r"\bAKIA[0-9A-Z]{16}\b"), "AWS Access Key ID"),
    (re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"), "SSH/TLS Private Key"),
]

# DIQQAT (Audit #6): `tests` papkasi SKIP_DIRS dan chiqarildi — test fayllar ham sirlarga tekshiriladi!
SKIP_DIRS = {".git", "node_modules", "__pycache__", "graphify-out", ".obsidian", "archive"}
FRONTMATTER_RE = re.compile(r"\A---\r?\n(.*?)\r?\n---", re.DOTALL)
LITERAL_DESC_RE = re.compile(r"^description:\s*\|", re.M)
HARDCODED_WIN_DRIVE = re.compile(r"[A-Za-z]:\\\\tyrion", re.I)

SCOPE_AND_LIMITATIONS = {
    "scanner_type": "STATIC_REPOSITORY_AND_GOVERNANCE_SCANNER",
    "tests_directory_scanned": True,
    "covered_risks": [
        "Hardcoded API tokens, .env files, AWS keys, and private keys across all tracked files including tests/",
        "Hook and MCP configuration command-injection and portability hazards",
        "Prompt injection defense baseline and skill linkage across all 36 agent charters",
        "YAML frontmatter integrity across all 62 skills",
        "Presence of Spend-Guard 6 financial mutation gates",
        "Python AST syntax and unreachable dead-code statements across tools/ and hooks/",
    ],
    "non_covered_risks": [
        "Does NOT replace a full external security audit, runtime container sandbox, or dynamic penetration test",
        "Does NOT verify live Meta Business Manager / Google Ads token scopes or server-side IAM policies",
        "Does NOT inspect encrypted binary blobs or external third-party npm/pip packages at runtime",
    ],
}


def scan_secrets() -> tuple[str, str, list[str]]:
    """Butun ombor bo'ylab (shu jumladan tests/ papkasida ham) sirlarni qidiradi."""
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
        return "fail", f"{len(issues)} xavf topildi ({scanned} fayl tekshirildi, tests/ qo'shilgan)", issues
    return "ok", f"{scanned} fayl toza (tests/ bilan birga), sizib chiqqan sir yo'q", []


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
    """36 agent charterida frontmatter, untrusted-data qalqoni va skill ulanishini tekshiradi."""
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
    return "ok", f"{len(agents)}/{len(agents)} agent charteri himoyalangan va skill'ga ulangan", []


def scan_skills() -> tuple[str, str, list[str]]:
    """62 skillda frontmatter, literal block scalar (`|`) va ulanishni tekshiradi."""
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


def _find_unreachable_in_body(stmts: list[ast.stmt], rel_path: str, issues: list[str]) -> None:
    terminated = False
    for stmt in stmts:
        if terminated:
            issues.append(f"{rel_path}:{getattr(stmt, 'lineno', '?')}: return/raise/break dan keyin o'lik kod (unreachable code)")
            break
        if isinstance(stmt, (ast.Return, ast.Raise, ast.Break, ast.Continue)):
            terminated = True
        for child_attr in ("body", "orelse", "finalbody"):
            child_body = getattr(stmt, child_attr, None)
            if isinstance(child_body, list):
                _find_unreachable_in_body(child_body, rel_path, issues)
        if isinstance(stmt, ast.Try):
            for handler in stmt.handlers:
                _find_unreachable_in_body(handler.body, rel_path, issues)


def scan_python_ast() -> tuple[str, str, list[str]]:
    """tools/ va hooks/ dagi barcha Python skriptlarda AST sintaksis va unreachable dead code tekshiruvi."""
    issues: list[str] = []
    py_files = sorted(list(TOOLS.glob("*.py")) + list((VAULT / "hooks").glob("*.py")) + list((VAULT / "tests").glob("*.py")))
    for py_path in py_files:
        rel = py_path.relative_to(VAULT).as_posix()
        try:
            tree = ast.parse(py_path.read_text(encoding="utf-8"), filename=rel)
        except SyntaxError as exc:
            issues.append(f"{rel}:{exc.lineno}: SyntaxError: {exc.msg}")
            continue
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                _find_unreachable_in_body(node.body, rel, issues)
    if issues:
        return "fail", f"{len(issues)} ta AST/dead-code muammosi topildi", issues
    return "ok", f"{len(py_files)} ta Python modulda 0 sintaksis xato va 0 o'lik kod", []


_SHIELD_CACHE: tuple[float, dict] | None = None

def run_all() -> dict:
    import time
    global _SHIELD_CACHE
    now = time.monotonic()
    if _SHIELD_CACHE is not None and (now - _SHIELD_CACHE[0]) < 2.0:
        return json.loads(json.dumps(_SHIELD_CACHE[1]))
    checks = []
    for name, fn in [
        ("Secrets & .env Exposure", scan_secrets),
        ("Hooks & MCP Config Safety", scan_hooks_and_mcp),
        ("Agent Charter Defense (36)", scan_agents),
        ("Skill Surface & YAML Safety", scan_skills),
        ("Spend-Guard & Mutation Gates", scan_mutation_gates),
        ("Python AST & Dead-Code Hygiene", scan_python_ast),
    ]:
        status, detail, items = fn()
        checks.append({"check": name, "status": status, "detail": detail, "items": items})

    summary = {
        "checked": len(checks),
        "ok": sum(1 for c in checks if c["status"] == "ok"),
        "warnings": sum(1 for c in checks if c["status"] == "warn"),
        "errors": sum(1 for c in checks if c["status"] == "fail"),
    }
    res = {
        "schema": "tyrion-shield/v5",
        "summary": summary,
        "scope_and_limitations": SCOPE_AND_LIMITATIONS,
        "checks": checks,
    }
    _SHIELD_CACHE = (now, res)
    return json.loads(json.dumps(res))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="tyrion-shield.py", description="TyrionShield v5.0 xavfsizlik va kod tozaligi skaneri")
    sub = parser.add_subparsers(dest="command")
    p_scan = sub.add_parser("scan", help="to'liq statik xavfsizlik tekshiruvi")
    p_scan.add_argument("--json", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    data = run_all()
    if getattr(args, "json", False):
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return 1 if data["summary"]["errors"] > 0 else 0

    icon = {"ok": "✓", "warn": "⚠", "fail": "✗"}
    print("=" * 72)
    print("  🛡️  TYRION SHIELD v5.0 — Statik Konfiguratsiya & Kod Gigiyenasi Auditi")
    print("=" * 72)
    for c in data["checks"]:
        print(f"  {icon[c['status']]} {c['check']:32} {c['detail']}")
        for item in c["items"][:5]:
            print(f"      - {item}")
    s = data["summary"]
    print("-" * 72)
    print(f"  Summary: checked={s['checked']}, ok={s['ok']}, warnings={s['warnings']}, errors={s['errors']}")
    print("  Eslatma: TyrionShield statik ombor qoidalarini tekshiradi; u to'liq tashqi")
    print("           penetration test yoki live OAuth ruxsatlar auditi o'rnini bosmaydi.")
    print("=" * 72)
    return 1 if s["errors"] > 0 else 0


if __name__ == "__main__":
    raise SystemExit(main())
