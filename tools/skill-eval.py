#!/usr/bin/env python3
"""Tyrion Behavioral & Deterministic Eval Runner (ECC skill-comply analogi, 0 token).

`evals/scenarios.json` dagi 10 ta real marketing va xavfsizlik stsenariysini
avtomatik ishga tushirib, har bir dvigatelning aniqligini (100% pass rate) tekshiradi.

Ishlatish:
  python3 tools/skill-eval.py [--json]
"""

from __future__ import annotations

import argparse
import importlib
import json
import subprocess
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
VAULT = TOOLS.parent
EVALS_FILE = VAULT / "evals" / "scenarios.json"
sys.path.insert(0, str(TOOLS))

for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        try:
            _stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:  # pragma: no cover
            pass


def run_evals() -> dict:
    data = json.loads(EVALS_FILE.read_text(encoding="utf-8"))
    ae = importlib.import_module("ad-export-analyzer")
    sg = importlib.import_module("spend-guard")
    cu = importlib.import_module("capi-utm-builder")
    ma = importlib.import_module("meta-audience")
    mcp = importlib.import_module("tyrion-mcp-server")

    results: list[dict] = []
    for sc in data.get("scenarios", []):
        sid = sc["id"]
        stype = sc["type"]
        passed = False
        detail = ""
        if stype == "skill_route":
            proc = subprocess.run(
                [sys.executable, str(TOOLS / "skill-search.py"), "brief", sc["query"], "--agent", sc["agent"]],
                capture_output=True, text=True, encoding="utf-8", errors="replace",
            )
            passed = f"Tanlandi: {sc['expected']}" in proc.stdout
            detail = f"expected={sc['expected']}"
        elif stype == "breakdown":
            res = ae.analyze_breakdown_effect("SegA", sc["seg_a_spend"], sc["seg_a_conv"], "SegB", sc["seg_b_spend"], sc["seg_b_conv"])
            passed = res["breakdown_effect_trap_detected"] is sc["expected_trap"]
            detail = f"trap={res['breakdown_effect_trap_detected']}"
        elif stype == "spend_guard":
            res = sg.check_budget_change(sc["current"], sc["proposed"], sc["max_cap"])
            passed = res["passed"] is sc["expected_pass"]
            detail = f"passed={res['passed']}"
        elif stype == "capi_emq":
            res = cu.build_capi_payload("Lead", phone=sc["phone"], email=sc["email"])
            passed = res["estimated_emq_score_10"] >= sc["min_emq"]
            detail = f"EMQ={res['estimated_emq_score_10']}/10"
        elif stype == "tg_utm":
            res = cu.build_utm_links("https://brand.uz", "meta", sc["campaign"], "test_bot")
            tg = res["telegram_bot_tracking"]
            passed = tg["within_64_char_limit"] and tg["payload_length"] <= sc["max_len"]
            detail = f"len={tg['payload_length']}/64"
        elif stype == "diagnose":
            res = ma.diagnose_metrics(cpm=sc["cpm"], ctr=sc["ctr"], cpc=0.4, lp_cvr=sc["lp_cvr"])
            stages = [b["stage"] for b in res["bottlenecks"]]
            passed = sc["expected_stage"] in stages
            detail = f"stages={stages}"
        elif stype == "mcp_list":
            resp = mcp.handle_request({"jsonrpc": "2.0", "id": 1, "method": "tools/list"})
            tcount = len((resp or {}).get("result", {}).get("tools", []))
            passed = tcount >= sc["min_tools"]
            detail = f"mcp_tools={tcount}"

        results.append({"id": sid, "type": stype, "passed": passed, "detail": detail})

    passed_count = sum(1 for r in results if r["passed"])
    return {
        "total": len(results),
        "passed": passed_count,
        "failed": len(results) - passed_count,
        "pass_rate_pct": round((passed_count / max(len(results), 1)) * 100.0, 1),
        "results": results,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="skill-eval.py", description="Tyrion Behavioral & Deterministic Eval Suite")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    summary = run_evals()
    if args.json:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    else:
        print("=" * 64)
        print(f"  🧪 TYRION EVAL SUITE — {summary['passed']}/{summary['total']} ({summary['pass_rate_pct']}%) PASS")
        print("=" * 64)
        for r in summary["results"]:
            icon = "✓" if r["passed"] else "✗"
            print(f"  {icon} {r['id']:28} [{r['type']:11}] {r['detail']}")
        print("=" * 64)
    return 0 if summary["failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
