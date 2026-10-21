#!/usr/bin/env python3
"""Tyrion Behavioral, Deterministic & Universal Routing Eval Runner (0 token).

`evals/scenarios.json` dagi 24 ta real marketing, xavfsizlik va Universal Auto-Router
stsenariysini ishga tushiradi hamda 7 ta marshrutlash sifat ko'rsatkichini hisoblaydi:
  1. Primary agent routing accuracy
  2. Required-skill recall
  3. Unnecessary-skill selection rate
  4. Missing-skill fallback success
  5. Multilingual routing success (uz_latin, uz_cyrillic, ru, en)
  6. Agent duplication rate
  7. Safety-rule coverage

Ishlatish:
  python3 tools/skill-eval.py [--json]
"""

from __future__ import annotations

import argparse
import contextlib
import importlib
import io
import json
import os
import sys
from pathlib import Path
from typing import Any

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


def run_evals() -> dict[str, Any]:
    data = json.loads(EVALS_FILE.read_text(encoding="utf-8"))
    ae = importlib.import_module("ad-export-analyzer")
    sg = importlib.import_module("spend-guard")
    cu = importlib.import_module("capi-utm-builder")
    ma = importlib.import_module("meta-audience")
    mcp = importlib.import_module("tyrion-mcp-server")
    ss_mod = importlib.import_module("skill-search")

    results: list[dict[str, Any]] = []

    # Counters for the 7 Universal Routing Metrics
    route_total = 0
    primary_agent_correct = 0
    expected_skills_total = 0
    expected_skills_recalled = 0
    unnecessary_skill_incidents = 0
    fallback_cases_total = 0
    fallback_cases_passed = 0
    multilingual_cases_total = 0
    multilingual_cases_passed = 0
    agent_duplication_incidents = 0
    expected_rules_total = 0
    expected_rules_covered = 0

    for sc in data.get("scenarios", []):
        sid = sc["id"]
        stype = sc["type"]
        passed = False
        detail = ""
        if stype == "skill_route":
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                ss_mod.main(["brief", sc["query"], "--agent", sc["agent"]])
            passed = f"Tanlandi: {sc['expected']}" in buf.getvalue()
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
        elif stype == "detailed_targeting_guard":
            mte = importlib.import_module("meta-targeting-engine")
            old_tok = os.environ.pop("META_ACCESS_TOKEN", None)
            try:
                rep = mte.search_and_validate_targeting(product=sc["product"], niche=sc["niche"])
            finally:
                if old_tok is not None:
                    os.environ["META_ACCESS_TOKEN"] = old_tok
            passed = (
                rep["live_check_status"]["status"] == sc["expected_status"]
                and len(rep["verified_targeting_options"]) == 0
                and all(x["validation_status"] == "RELATED_UNVERIFIED" for x in rep["related_unverified_ideas"])
            )
            detail = f"status={rep['live_check_status']['status']}, verified=0"
        elif stype == "mcp_tool_present":
            resp = mcp.handle_request({"jsonrpc": "2.0", "id": 1, "method": "tools/list"})
            names = [t["name"] for t in (resp or {}).get("result", {}).get("tools", [])]
            passed = sc["tool_name"] in names
            detail = f"present={passed}"
        elif stype == "universal_route":
            route_total += 1
            plan = ss_mod.route_task(sc["query"], load=True)
            selected_skills = set(plan["required_skills"] + plan["supporting_skills"])
            all_agents_list = [plan["primary_agent"]] + list(plan["supporting_agents"])
            selected_agents = set(all_agents_list)
            selected_rules = set(plan["rules_to_load"])

            # 1. Primary agent match
            ag_ok = plan["primary_agent"] == sc["expected_primary_agent"]
            if ag_ok:
                primary_agent_correct += 1

            # 2. Required skill recall
            exp_skills = sc.get("expected_skills", [])
            expected_skills_total += len(exp_skills)
            recalled_here = sum(1 for s in exp_skills if s in selected_skills)
            expected_skills_recalled += recalled_here
            skills_ok = recalled_here == len(exp_skills)

            # 3. Unnecessary / forbidden skills or agents
            forb_skills = set(sc.get("forbidden_skills", []))
            forb_agents = set(sc.get("forbidden_agents", []))
            has_unnecessary = bool((selected_skills & forb_skills) or (selected_agents & forb_agents))
            if has_unnecessary:
                unnecessary_skill_incidents += 1

            # 4. Agent duplication check
            has_dup_agents = len(all_agents_list) != len(set(all_agents_list))
            if has_dup_agents:
                agent_duplication_incidents += 1

            # 5. Safety rules coverage
            exp_rules = sc.get("expected_rules", [])
            expected_rules_total += len(exp_rules)
            rules_hit = sum(1 for r in exp_rules if r in selected_rules)
            expected_rules_covered += rules_hit
            rules_ok = rules_hit == len(exp_rules)

            # 6. Status & Fallback checks
            status_ok = plan["status"] == sc["expected_status"]
            fb_ok = bool(plan["fallback_plan"]["triggered"]) is bool(sc["expected_fallback_triggered"])
            if sc.get("expected_fallback_triggered"):
                fallback_cases_total += 1
                if status_ok and fb_ok and ag_ok and not plan.get("asks_user_for_skill_or_agent"):
                    fallback_cases_passed += 1

            # 7. Multilingual routing check
            multilingual_cases_total += 1
            case_ok = ag_ok and skills_ok and (not has_unnecessary) and (not has_dup_agents) and rules_ok and status_ok and fb_ok
            if case_ok:
                multilingual_cases_passed += 1

            passed = case_ok
            detail = (
                f"agent={plan['primary_agent']}, skills={plan['required_skills']}, "
                f"status={plan['status']}, lang={plan['intent_analysis']['detected_language']}"
            )

        results.append({"id": sid, "type": stype, "passed": passed, "detail": detail})

    passed_count = sum(1 for r in results if r["passed"])
    routing_metrics = {
        "primary_agent_routing_accuracy_pct": round((primary_agent_correct / max(route_total, 1)) * 100.0, 1),
        "required_skill_recall_pct": round((expected_skills_recalled / max(expected_skills_total, 1)) * 100.0, 1),
        "unnecessary_skill_selection_rate_pct": round((unnecessary_skill_incidents / max(route_total, 1)) * 100.0, 1),
        "missing_skill_fallback_success_pct": round((fallback_cases_passed / max(fallback_cases_total, 1)) * 100.0, 1),
        "multilingual_routing_success_pct": round((multilingual_cases_passed / max(multilingual_cases_total, 1)) * 100.0, 1),
        "agent_duplication_rate_pct": round((agent_duplication_incidents / max(route_total, 1)) * 100.0, 1),
        "safety_rule_coverage_pct": round((expected_rules_covered / max(expected_rules_total, 1)) * 100.0, 1),
    }

    return {
        "total": len(results),
        "passed": passed_count,
        "failed": len(results) - passed_count,
        "pass_rate_pct": round((passed_count / max(len(results), 1)) * 100.0, 1),
        "routing_metrics": routing_metrics,
        "results": results,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="skill-eval.py", description="Tyrion Behavioral, Deterministic & Routing Eval Suite")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    summary = run_evals()
    if args.json:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    else:
        print("=" * 76)
        print(f"  🧪 TYRION EVAL SUITE — {summary['passed']}/{summary['total']} ({summary['pass_rate_pct']}%) PASS")
        print("=" * 76)
        for r in summary["results"]:
            icon = "✓" if r["passed"] else "✗"
            print(f"  {icon} {r['id']:38} [{r['type']:15}] {r['detail']}")
        rm = summary["routing_metrics"]
        print("-" * 76)
        print("  🧭 UNIVERSAL ROUTER 7-METRIC SCORECARD:")
        print(f"    1. Primary Agent Routing Accuracy : {rm['primary_agent_routing_accuracy_pct']}%")
        print(f"    2. Required-Skill Recall          : {rm['required_skill_recall_pct']}%")
        print(f"    3. Unnecessary-Skill Selection    : {rm['unnecessary_skill_selection_rate_pct']}% (target: 0.0%)")
        print(f"    4. Missing-Skill Fallback Success : {rm['missing_skill_fallback_success_pct']}%")
        print(f"    5. Multilingual Routing Success   : {rm['multilingual_routing_success_pct']}% (uz_latin, uz_cyrillic, ru, en)")
        print(f"    6. Agent Duplication Rate         : {rm['agent_duplication_rate_pct']}% (target: 0.0%)")
        print(f"    7. Safety-Rule Coverage           : {rm['safety_rule_coverage_pct']}%")
        print("=" * 76)
    return 0 if summary["failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
