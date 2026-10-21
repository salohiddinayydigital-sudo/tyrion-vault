#!/usr/bin/env python3
"""Tyrion Native MCP Server (JSON-RPC 2.0 over STDIO, Production-Hardened v5.0.0).

Guards against oversized payloads (>1 MB), malformed JSON (-32700), unknown methods (-32601),
invalid/NaN parameters (-32602), and subprocess hangs (15s timeout).
Includes:
  - `tyrion_meta_detailed_targeting` (6-status Detailed Targeting Accuracy Engine with official API provenance)
  - `tyrion_meta_live_insights` (paginated Meta Ads Graph API v26.0 account telemetry & conversion separation)
"""

from __future__ import annotations

import argparse
import importlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

TOOLS = Path(__file__).resolve().parent
VAULT = TOOLS.parent
sys.path.insert(0, str(TOOLS))

import tyrion_core as tcore  # noqa: E402

SERVER_VERSION = "5.0.0"

MCP_TOOLS = [
    {
        "name": "tyrion_universal_router",
        "description": "Universal Auto-Router & Autonomous Agent Orchestrator: analyzes any natural-language marketing task (UZ Latin, UZ Cyrillic, RU, EN), selects primary_agent, supporting_agents, required_skills, supporting_skills, references_to_load, rules_to_load, tools_to_use, and workflow, enforces Spend-Guard mutation gates, and loads the required charter/skill/reference context.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "agent_hint": {"type": "string", "default": ""},
                "load": {"type": "boolean", "default": True},
                "mutation_approved": {"type": "boolean", "default": False},
                "reroute_with": {"type": "string", "default": ""},
            },
            "required": ["query"],
        },
    },
    {
        "name": "tyrion_meta_detailed_targeting",
        "description": "Search and validate Meta Ads Detailed Targeting options (Interests, Behaviors, Demographics) via official Meta Graph API endpoints (/search, /act_<id>/targetingsearch, /targetingsuggestions, /targetingvalidation) with 6 strict verification statuses (VERIFIED_AVAILABLE, FOUND_NOT_VALIDATED, UNAVAILABLE_OR_CONSOLIDATED, RELATED_UNVERIFIED, NOT_FOUND, API_UNAVAILABLE). Never hallucinates unverified interests as valid Meta options.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "product": {"type": "string", "default": ""},
                "niche": {"type": "string", "default": "ecom"},
                "customer_profile": {"type": "string", "default": ""},
                "objective": {"type": "string", "default": "SALES"},
                "country": {"type": "string", "default": "UZ"},
                "language": {"type": "string", "default": "auto"},
                "queries": {"type": "array", "items": {"type": "string"}},
                "ad_account_id": {"type": "string", "default": ""},
                "special_ad_category": {"type": "string", "default": "NONE"},
                "include_suggestions": {"type": "boolean", "default": False},
                "validate_results": {"type": "boolean", "default": True},
            },
        },
    },
    {
        "name": "tyrion_meta_audience",
        "description": "Build 4-layer Meta Ads Andromeda 2 audience architecture with calibrated unit-economics CPA derivation, exclusion matrix, and solventnost hypotheses.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "niche": {"type": "string", "default": "ecom"},
                "daily_budget": {"type": "number", "default": 100.0},
                "geo": {"type": "string", "default": "tashkent"},
                "target_cpa": {"type": "number"},
                "measured_cpa": {"type": "number"},
                "aov": {"type": "number"},
                "margin_pct": {"type": "number"},
                "lead_to_sale_cvr": {"type": "number"},
            },
            "required": ["niche", "daily_budget"],
        },
    },
    {
        "name": "tyrion_meta_live_insights",
        "description": "Pull and audit live Meta Ads account telemetry (Graph API v26.0 /act_<id>/insights with paging.next pagination, account_currency, and conversion-family separation) or parse a raw Graph API insights JSON file.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "account_id": {"type": "string", "default": ""},
                "level": {"type": "string", "default": "adset"},
                "date_preset": {"type": "string", "default": "last_7d"},
                "target_cpa": {"type": "number", "default": 15.0},
                "breakeven_roas": {"type": "number", "default": 2.0},
                "primary_conversion": {"type": "string", "default": "auto"},
                "currency": {"type": "string", "default": ""},
                "max_pages": {"type": "integer", "default": 20},
                "from_raw_json": {"type": "string", "default": ""},
            },
        },
    },
    {
        "name": "tyrion_breakdown_effect",
        "description": "Detect Meta Ads 'Breakdown Effect' (Marginal vs Average CPA trap) across two placements or segments.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "seg_a_name": {"type": "string"},
                "seg_a_spend": {"type": "number"},
                "seg_a_conv": {"type": "integer"},
                "seg_b_name": {"type": "string"},
                "seg_b_spend": {"type": "number"},
                "seg_b_conv": {"type": "integer"},
            },
            "required": ["seg_a_name", "seg_a_spend", "seg_a_conv", "seg_b_name", "seg_b_spend", "seg_b_conv"],
        },
    },
    {
        "name": "tyrion_creative_matrix",
        "description": "Generate Andromeda 2 3x3 Angle x Format creative matrix and 3-language (UZ Latin, UZ Cyrillic, RU) hooks.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "niche": {"type": "string", "default": "ecom"},
                "product": {"type": "string"},
                "price": {"type": "number", "default": 100.0},
            },
            "required": ["product"],
        },
    },
    {
        "name": "tyrion_capi_utm",
        "description": "Build Meta CAPI v26.0 SHA-256 hashed payload with EMQ score or Telegram Bot <=64-char UTM deep-links.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "default": "https://brand.uz"},
                "platform": {"type": "string", "default": "meta"},
                "campaign": {"type": "string", "default": "launch"},
                "bot": {"type": "string", "default": ""},
            },
        },
    },
    {
        "name": "tyrion_media_calculator",
        "description": "Calculate break-even CPA, break-even ROAS, and gross profit per unit.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "price": {"type": "number"},
                "cogs": {"type": "number"},
                "shipping": {"type": "number", "default": 0.0},
            },
            "required": ["price", "cogs"],
        },
    },
    {
        "name": "tyrion_spend_guard",
        "description": "Validate budget hike against the 20% learning-phase safety threshold and daily ceiling.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "current_daily": {"type": "number"},
                "proposed_daily": {"type": "number"},
                "max_daily_cap": {"type": "number", "default": 500.0},
            },
            "required": ["current_daily", "proposed_daily"],
        },
    },
    {
        "name": "tyrion_brain_search",
        "description": "Search Tyrion's 100 atomic knowledge notes and 9 niche playbooks in 0 tokens.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
            },
            "required": ["query"],
        },
    },
]


def call_tool(name: str, args: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(args, dict):
        raise ValueError("Tool arguments must be a JSON object")

    if name == "tyrion_universal_router":
        ss = importlib.import_module("skill-search")
        q = str(args.get("query", "")).strip()
        if not q:
            raise ValueError("'query' bo'sh bo'lishi mumkin emas")
        plan = ss.route_task(
            query=q,
            agent_hint=str(args.get("agent_hint", "")),
            load=bool(args.get("load", True)),
            mutation_approved=bool(args.get("mutation_approved", False)),
        )
        reroute_q = str(args.get("reroute_with", "")).strip()
        if reroute_q:
            plan = ss.reroute_task(
                current_plan=plan,
                emergent_requirement=reroute_q,
                load=bool(args.get("load", True)),
            )
        return plan
    if name == "tyrion_meta_detailed_targeting":
        mte = importlib.import_module("meta-targeting-engine")
        raw_queries = args.get("queries")
        q_list = [str(x) for x in raw_queries] if isinstance(raw_queries, list) else None
        return mte.search_and_validate_targeting(
            product=str(args.get("product", "")),
            niche=str(args.get("niche", "ecom")),
            customer_profile=str(args.get("customer_profile", "")),
            objective=str(args.get("objective", "SALES")),
            country=str(args.get("country", "UZ")),
            language=str(args.get("language", "auto")),
            queries=q_list,
            ad_account_id=str(args.get("ad_account_id", "")),
            special_ad_category=str(args.get("special_ad_category", "NONE")),
            include_suggestions=bool(args.get("include_suggestions", False)),
            validate_results=bool(args.get("validate_results", True)),
        )
    if name == "tyrion_meta_audience":
        ma = importlib.import_module("meta-audience")
        budget = tcore.safe_float(args.get("daily_budget", 100.0), min_val=1.0, max_val=1_000_000.0, field_name="daily_budget")
        target_cpa = tcore.safe_float(args["target_cpa"], min_val=0.01, field_name="target_cpa") if args.get("target_cpa") is not None else None
        measured_cpa = tcore.safe_float(args["measured_cpa"], min_val=0.01, field_name="measured_cpa") if args.get("measured_cpa") is not None else None
        aov = tcore.safe_float(args["aov"], min_val=0.01, field_name="aov") if args.get("aov") is not None else None
        margin_pct = tcore.safe_float(args["margin_pct"], min_val=0.01, max_val=100.0, field_name="margin_pct") if args.get("margin_pct") is not None else None
        cvr = tcore.safe_float(args["lead_to_sale_cvr"], min_val=0.01, max_val=100.0, field_name="lead_to_sale_cvr") if args.get("lead_to_sale_cvr") is not None else None
        return ma.build_architecture(
            niche=str(args.get("niche", "ecom")),
            daily_budget=budget,
            geo=str(args.get("geo", "tashkent")),
            target_cpa=target_cpa,
            measured_cpa=measured_cpa,
            aov=aov,
            margin_pct=margin_pct,
            lead_to_sale_cvr=cvr,
        )
    if name == "tyrion_meta_live_insights":
        mis = importlib.import_module("meta-insights-sync")
        raw_json_arg = str(args.get("from_raw_json", "")).strip()
        raw_path: Path | None = None
        if raw_json_arg:
            candidate = (VAULT / raw_json_arg) if not Path(raw_json_arg).is_absolute() else Path(raw_json_arg)
            raw_path = tcore.validate_safe_path(candidate, allowed_root=VAULT)
        return mis.sync_and_analyze(
            account_id=str(args.get("account_id", "")),
            level=str(args.get("level", "adset")),
            date_preset=str(args.get("date_preset", "last_7d")),
            target_cpa=tcore.safe_float(args.get("target_cpa", 15.0), min_val=0.01, field_name="target_cpa"),
            breakeven_roas=tcore.safe_float(args.get("breakeven_roas", 2.0), min_val=0.01, field_name="breakeven_roas"),
            primary_conversion=str(args.get("primary_conversion", "auto")),
            currency_override=str(args.get("currency", "")),
            max_pages=tcore.safe_int(args.get("max_pages", 20), default=20, min_val=1, max_val=100, field_name="max_pages"),
            from_raw_json=raw_path,
        )
    if name == "tyrion_breakdown_effect":
        ae = importlib.import_module("ad-export-analyzer")
        return ae.analyze_breakdown_effect(
            str(args["seg_a_name"]),
            tcore.safe_float(args["seg_a_spend"], min_val=0.0, field_name="seg_a_spend"),
            tcore.safe_int(args["seg_a_conv"], min_val=0, field_name="seg_a_conv"),
            str(args["seg_b_name"]),
            tcore.safe_float(args["seg_b_spend"], min_val=0.0, field_name="seg_b_spend"),
            tcore.safe_int(args["seg_b_conv"], min_val=0, field_name="seg_b_conv"),
        )
    if name == "tyrion_creative_matrix":
        cm = importlib.import_module("creative-matrix")
        product = str(args.get("product", "")).strip()
        if not product:
            raise ValueError("'product' bo'sh bo'lishi mumkin emas")
        price = tcore.safe_float(args.get("price", 100.0), min_val=0.0, field_name="price")
        return cm.build_matrix(str(args.get("niche", "ecom")), product, price)
    if name == "tyrion_capi_utm":
        cu = importlib.import_module("capi-utm-builder")
        return cu.build_utm_links(
            str(args.get("url", "https://brand.uz")),
            str(args.get("platform", "meta")),
            str(args.get("campaign", "launch")),
            str(args.get("bot", "")),
        )
    if name == "tyrion_media_calculator":
        calc = importlib.import_module("calculator")
        price = tcore.safe_float(args.get("price"), min_val=0.01, field_name="price")
        cogs = tcore.safe_float(args.get("cogs"), min_val=0.0, field_name="cogs")
        shipping = tcore.safe_float(args.get("shipping", 0.0), min_val=0.0, field_name="shipping")
        return calc.calc_breakeven(price, cogs, shipping)
    if name == "tyrion_spend_guard":
        sg = importlib.import_module("spend-guard")
        curr = tcore.safe_float(args.get("current_daily"), min_val=0.01, field_name="current_daily")
        prop = tcore.safe_float(args.get("proposed_daily"), min_val=0.01, field_name="proposed_daily")
        cap = tcore.safe_float(args.get("max_daily_cap", 500.0), min_val=0.01, field_name="max_daily_cap")
        return sg.check_budget_change(curr, prop, cap)
    if name == "tyrion_brain_search":
        q = str(args.get("query", "")).strip()[:200]
        if not q:
            raise ValueError("'query' bo'sh bo'lishi mumkin emas")
        proc = subprocess.run(
            [sys.executable, str(TOOLS / "brain-search.py"), "search", q, "--top", "5"],
            capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=15,
        )
        return {"output": proc.stdout.strip()}
    raise KeyError(f"Unknown MCP tool: {name}")


def handle_request(req: Any) -> dict[str, Any] | None:
    if not isinstance(req, dict):
        return {"jsonrpc": "2.0", "id": None, "error": {"code": -32600, "message": "Invalid Request"}}
    method = req.get("method", "")
    req_id = req.get("id")
    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "tyrion-mcp-server", "version": SERVER_VERSION},
            },
        }
    if method in ("notifications/initialized", "initialized"):
        return None
    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": req_id, "result": {"tools": MCP_TOOLS}}
    if method == "tools/call":
        params = req.get("params")
        if not isinstance(params, dict):
            return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32602, "message": "Invalid params"}}
        tname = str(params.get("name", ""))
        targs = params.get("arguments") or {}
        try:
            payload = call_tool(tname, targs)
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {"content": [{"type": "text", "text": json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False)}]},
            }
        except (ValueError, KeyError, TypeError) as exc:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32602, "message": tcore.redact_secrets(str(exc))},
            }
        except Exception as exc:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32000, "message": tcore.redact_secrets(str(exc))},
            }
    if req_id is not None:
        return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": f"Method not found: {method}"}}
    return None


def process_raw_line(raw_line: str) -> dict[str, Any] | None:
    if len(raw_line.encode("utf-8", errors="replace")) > tcore.MAX_RPC_LINE_BYTES:
        return {"jsonrpc": "2.0", "id": None, "error": {"code": -32600, "message": "Payload exceeds 1 MB limit"}}
    try:
        req = json.loads(raw_line)
    except json.JSONDecodeError as exc:
        return {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": f"Parse error: {exc.msg}"}}
    return handle_request(req)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="tyrion-mcp-server.py", description="Tyrion v5.0.0 Native STDIO MCP Server")
    parser.add_argument("--list-tools", action="store_true", help="Mavjud MCP tool'lar ro'yxatini JSON formatda chiqarish")
    args = parser.parse_args(argv)
    if args.list_tools:
        print(json.dumps({"server": "tyrion-mcp-server", "version": SERVER_VERSION, "tools": MCP_TOOLS}, ensure_ascii=False, indent=2))
        return 0
    for line in sys.stdin:
        stripped = line.strip()
        if not stripped:
            continue
        resp = process_raw_line(stripped)
        if resp is not None:
            sys.stdout.write(json.dumps(resp, ensure_ascii=False) + "\n")
            sys.stdout.flush()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
