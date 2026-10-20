#!/usr/bin/env python3
"""Tyrion v5.1 Live Meta Ads Insights Connector — Real reklama akkauntlaridan (act_<id>/insights)
kampaniya, ad set va kreativ ko'rsatkichlarini sahifalab (cursor pagination `paging.next`) tortish,
akkaunt valyutasini (`account_currency`) aniqlash, konversiya turlarini (`PURCHASE`, `LEAD`, `MESSAGING`)
ajratish va auditdan o'tkazish (0 token).

Yangi imkoniyatlar (v5.1 Ikkinchi Audit Yechimlari):
  1. `paging.next` Cursor Pagination + SSRF Host Guard: 50 ta natija bilan cheklanib qolmasdan,
     barcha sahifalarni (`--max-pages`, standart 20 sahifa) avtomatik aylanib chiqadi.
  2. `account_currency` Aniqligi: Meta Insights javobidan `account_currency` (`USD`, `UZS`, `KZT`, `EUR` va b.)
     maydonini oladi va hisobot valyutasini shaffof ko'rsatadi (`currency_source`).
  3. Konversiya Oilalarini Ajratish (`--primary-conversion auto|purchase|lead|messaging`):
     `purchase`, `lead` va `messaging` konversiyalarini har bir satrda alohida hisoblaydi (`conversions_by_family`)
     va turli maqsaddagi kampaniyalarni bitta "blended CPA" ga aralashtirib yubormaydi.
  4. `verify-live`: Haqiqiy `META_ACCESS_TOKEN` va reklama akkauntining valyuta/holatini Graph API v26.0 da tekshirish.

Ishlatish:
  python3 tools/meta-insights-sync.py pull --account-id act_123456789 --level adset --date-preset last_7d --primary-conversion purchase --target-cpa 15
  python3 tools/meta-insights-sync.py pull --from-raw-json examples/demo-brand/assets/meta_graph_insights_raw.json --target-cpa 15
  python3 tools/meta-insights-sync.py verify-live --account-id act_123456789
"""

from __future__ import annotations

import argparse
import importlib
import json
import os
import sys
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

TOOLS = Path(__file__).resolve().parent
VAULT = TOOLS.parent
sys.path.insert(0, str(TOOLS))

import tyrion_core as tcore  # noqa: E402

for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        try:
            _stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:  # pragma: no cover
            pass

DEFAULT_GRAPH_API_VERSION = "v26.0"

CONVERSION_FAMILIES: dict[str, tuple[str, ...]] = {
    "PURCHASE": (
        "purchase",
        "offsite_conversion.fb_pixel_purchase",
        "omni_purchase",
    ),
    "LEAD": (
        "lead",
        "offsite_conversion.fb_pixel_lead",
        "onsite_conversion.lead_grouped",
    ),
    "MESSAGING": (
        "onsite_conversion.messaging_conversation_started_7d",
        "contact_total",
    ),
}

REVENUE_ACTION_PRIORITY = (
    "purchase",
    "offsite_conversion.fb_pixel_purchase",
    "omni_purchase",
)


def get_graph_api_version() -> str:
    ver = os.environ.get("META_GRAPH_API_VERSION", DEFAULT_GRAPH_API_VERSION).strip()
    return ver if ver else DEFAULT_GRAPH_API_VERSION


def normalize_account_id(account_id: str) -> str:
    clean = str(account_id or "").strip()
    if not clean:
        clean = os.environ.get("META_AD_ACCOUNT_ID", "").strip()
    if not clean:
        raise ValueError("Reklama akkaunt ID si berilmadi (`--account-id act_...` yoki `META_AD_ACCOUNT_ID`).")
    if not clean.startswith("act_"):
        clean = f"act_{clean}"
    if not clean[4:].isdigit():
        raise ValueError(f"Noto'g'ri Meta Ad Account ID formati: {clean!r} (namuna: act_1234567890)")
    return clean


def _extract_action_metric(actions: list[dict[str, Any]] | None, priority_keys: tuple[str, ...]) -> tuple[float, str]:
    if not isinstance(actions, list):
        return 0.0, "none"
    by_type: dict[str, float] = {}
    for item in actions:
        if isinstance(item, dict):
            atype = str(item.get("action_type", "")).strip()
            val = tcore.safe_float(item.get("value", 0.0), default=0.0, min_val=0.0)
            if atype:
                by_type[atype] = val
    for key in priority_keys:
        if key in by_type and by_type[key] > 0:
            return by_type[key], key
    return 0.0, "none"


def _extract_all_conversion_families(actions: list[dict[str, Any]] | None) -> tuple[dict[str, int], dict[str, str]]:
    counts: dict[str, int] = {}
    matched_types: dict[str, str] = {}
    for fam, keys in CONVERSION_FAMILIES.items():
        val, mtype = _extract_action_metric(actions, keys)
        counts[fam] = int(round(val))
        matched_types[fam] = mtype
    return counts, matched_types


def normalize_insights_rows(
    raw_rows: list[dict[str, Any]],
    level: str = "adset",
    primary_conversion: str = "auto",
    default_currency: str = "USD",
) -> list[dict[str, Any]]:
    """Meta Graph API `insights` formatidagi xom satrlarni valyuta va konversiya oilalarini ajratgan holda normalizatsiya qiladi."""
    req_conv = str(primary_conversion or "auto").strip().lower()
    if req_conv not in ("auto", "purchase", "lead", "messaging"):
        raise ValueError(f"Noto'g'ri primary_conversion: {primary_conversion!r} (auto|purchase|lead|messaging)")

    normalized: list[dict[str, Any]] = []
    for idx, row in enumerate(raw_rows, 1):
        if not isinstance(row, dict):
            continue
        name = (
            row.get("ad_name")
            or row.get("adset_name")
            or row.get("campaign_name")
            or row.get("name")
            or f"{level}_{idx}"
        )
        row_currency = str(
            row.get("account_currency") or row.get("currency") or default_currency or "USD"
        ).strip().upper() or "USD"

        spend = tcore.safe_float(row.get("spend", 0.0), default=0.0, min_val=0.0)
        impressions = tcore.safe_int(row.get("impressions", 0), default=0, min_val=0)
        reach = tcore.safe_int(row.get("reach", 0), default=0, min_val=0)
        frequency = tcore.safe_float(row.get("frequency", 0.0), default=0.0, min_val=0.0)
        if frequency <= 0 and reach > 0 and impressions > 0:
            frequency = round(impressions / reach, 2)

        clicks = tcore.safe_int(row.get("inline_link_clicks") or row.get("clicks") or 0, default=0, min_val=0)
        if clicks == 0 and isinstance(row.get("actions"), list):
            lk, _ = _extract_action_metric(row.get("actions"), ("link_click",))
            clicks = int(lk)

        fam_counts, fam_types = _extract_all_conversion_families(row.get("actions"))
        if sum(fam_counts.values()) == 0 and "conversions" in row:
            direct_c = int(round(tcore.safe_float(row.get("conversions", 0), default=0.0, min_val=0.0)))
            direct_fam = str(row.get("conversion_family", "UNSPECIFIED")).strip().upper() or "UNSPECIFIED"
            fam_counts[direct_fam] = direct_c
            fam_types[direct_fam] = "direct_field"

        if req_conv in ("purchase", "lead", "messaging"):
            chosen_fam = req_conv.upper()
            conversions = fam_counts.get(chosen_fam, 0)
            conv_type = fam_types.get(chosen_fam, "none") if conversions > 0 else "none"
            if conversions == 0:
                chosen_fam = "NONE"
        else:
            # In auto mode, pick the primary active family for this row, while preserving conversions_by_family
            chosen_fam = "NONE"
            conversions = 0
            conv_type = "none"
            for candidate_fam in ("PURCHASE", "LEAD", "MESSAGING", "UNSPECIFIED"):
                if fam_counts.get(candidate_fam, 0) > 0:
                    chosen_fam = candidate_fam
                    conversions = fam_counts[candidate_fam]
                    conv_type = fam_types.get(candidate_fam, "direct_field")
                    break

        revenue, rev_type = _extract_action_metric(row.get("action_values"), REVENUE_ACTION_PRIORITY)
        if revenue == 0.0 and "revenue" in row:
            revenue = tcore.safe_float(row.get("revenue", 0.0), default=0.0, min_val=0.0)
            rev_type = "direct_field"

        normalized.append({
            "id": str(row.get("ad_id") or row.get("adset_id") or row.get("campaign_id") or f"id_{idx}"),
            "name": str(name),
            "account_currency": row_currency,
            "spend": round(spend, 2),
            "impressions": impressions,
            "reach": reach,
            "frequency": round(frequency, 2),
            "clicks": clicks,
            "conversions": conversions,
            "conversion_family": chosen_fam,
            "conversion_action_type": conv_type,
            "conversions_by_family": fam_counts,
            "revenue": round(revenue, 2),
            "revenue_action_type": rev_type,
            "date_start": str(row.get("date_start", "")),
            "date_stop": str(row.get("date_stop", "")),
        })
    return normalized


def _validate_same_origin(next_url: str, base_url: str) -> str:
    """`paging.next` URL manzilining aynan `META_GRAPH_API_BASE_URL` domeniga tegishli ekanini tekshiradi (SSRF himoyasi)."""
    clean_next = tcore.sanitize_url(next_url)
    p_next = urllib.parse.urlparse(clean_next)
    p_base = urllib.parse.urlparse(base_url)
    if p_next.scheme.lower() != p_base.scheme.lower() or p_next.netloc.lower() != p_base.netloc.lower():
        raise PermissionError(
            f"Xavfsizlik xatosi: paging.next URL manzili ({p_next.netloc}) asosiy Graph API domeniga ({p_base.netloc}) mos emas!"
        )
    return clean_next


def fetch_live_meta_insights(
    account_id: str,
    level: str = "adset",
    date_preset: str = "last_7d",
    limit: int = 100,
    max_pages: int = 20,
) -> dict[str, Any]:
    """Meta Graph API v26.0 `/act_<id>/insights` endpointidan barcha sahifalarni (`paging.next`) aylanib tortadi."""
    acct = normalize_account_id(account_id)
    token = os.environ.get("META_ACCESS_TOKEN", "").strip()
    if not token or token == "your_meta_access_token_here":
        raise PermissionError(
            "META_ACCESS_TOKEN topilmadi. Jonli Meta Ads ma'lumotlarini tortish uchun `.env` fayliga "
            "haqiqiy `META_ACCESS_TOKEN` qo'ying yoki `--from-raw-json` orqali eksport faylini bering."
        )

    api_version = get_graph_api_version()
    base = os.environ.get("META_GRAPH_API_BASE_URL", "https://graph.facebook.com").strip().rstrip("/")
    safe_limit = tcore.safe_int(limit, default=100, min_val=1, max_val=500, field_name="limit")
    safe_max_pages = tcore.safe_int(max_pages, default=20, min_val=1, max_val=100, field_name="max_pages")

    fields = ",".join([
        "campaign_id", "campaign_name", "adset_id", "adset_name", "ad_id", "ad_name",
        "account_currency", "spend", "impressions", "reach", "frequency", "cpm", "ctr", "cpc",
        "inline_link_clicks", "actions", "action_values", "date_start", "date_stop",
    ])
    params = urllib.parse.urlencode({
        "level": level,
        "date_preset": date_preset,
        "fields": fields,
        "limit": str(safe_limit),
    })
    current_url: str | None = f"{base}/{api_version}/{acct}/insights?{params}"
    headers = {"Authorization": f"Bearer {token}"}

    all_rows: list[dict[str, Any]] = []
    pages_fetched = 0

    while current_url and pages_fetched < safe_max_pages:
        payload = tcore.http_get_json_with_backoff(current_url, headers=headers, timeout=15.0, max_retries=3)
        if "error" in payload:
            raise RuntimeError(f"Meta Graph API Insights xatosi: {tcore.redact_secrets(str(payload['error']))}")
        data = payload.get("data", [])
        if not isinstance(data, list):
            raise ValueError("Meta Graph API noto'g'ri javob formati qaytardi (`data` ro'yxat emas).")
        all_rows.extend(data)
        pages_fetched += 1

        paging = payload.get("paging")
        next_raw = paging.get("next") if isinstance(paging, dict) else None
        if next_raw and isinstance(next_raw, str) and next_raw.strip():
            current_url = _validate_same_origin(next_raw.strip(), base)
        else:
            current_url = None

    is_truncated = current_url is not None
    detected_currencies = sorted({
        str(r.get("account_currency", "")).strip().upper()
        for r in all_rows
        if isinstance(r, dict) and str(r.get("account_currency", "")).strip()
    })

    return {
        "account_id": acct,
        "graph_api_version": api_version,
        "level": level,
        "date_preset": date_preset,
        "pages_fetched": pages_fetched,
        "is_truncated": is_truncated,
        "account_currency": detected_currencies[0] if len(detected_currencies) == 1 else (detected_currencies[0] if detected_currencies else None),
        "raw_rows": all_rows,
        "data_source_type": "LIVE_META_GRAPH_API",
    }


def verify_live_connection(account_id: str = "") -> dict[str, Any]:
    """Haqiqiy META_ACCESS_TOKEN va reklama akkaunti valyutasi/holatini Graph API v26.0 da tekshiradi."""
    acct = normalize_account_id(account_id)
    token = os.environ.get("META_ACCESS_TOKEN", "").strip()
    if not token or token == "your_meta_access_token_here":
        raise PermissionError("META_ACCESS_TOKEN o'rnatilmagan (.env faylini tekshiring).")
    api_version = get_graph_api_version()
    base = os.environ.get("META_GRAPH_API_BASE_URL", "https://graph.facebook.com").strip().rstrip("/")
    params = urllib.parse.urlencode({"fields": "id,name,account_status,currency,timezone_name,amount_spent"})
    url = f"{base}/{api_version}/{acct}?{params}"
    headers = {"Authorization": f"Bearer {token}"}
    payload = tcore.http_get_json_with_backoff(url, headers=headers, timeout=10.0, max_retries=2)
    if "error" in payload:
        raise RuntimeError(f"Meta Graph API autentifikatsiya xatosi: {tcore.redact_secrets(str(payload['error']))}")
    return {
        "authenticated": True,
        "graph_api_version": api_version,
        "account_id": payload.get("id", acct),
        "account_name": payload.get("name", ""),
        "account_currency": payload.get("currency", "USD"),
        "account_status": payload.get("account_status"),
        "timezone_name": payload.get("timezone_name", ""),
    }


def sync_and_analyze(
    account_id: str = "",
    level: str = "adset",
    date_preset: str = "last_7d",
    target_cpa: float = 15.0,
    breakeven_roas: float = 2.0,
    primary_conversion: str = "auto",
    currency_override: str = "",
    limit: int = 100,
    max_pages: int = 20,
    from_raw_json: Path | None = None,
    save_out: Path | None = None,
) -> dict[str, Any]:
    """Jonli Graph API (sahifalash bilan) yoki xom Graph API JSON faylidan ma'lumot olib, valyuta va konversiya turlarini ajratib tahlil qiladi."""
    api_version = get_graph_api_version()
    if from_raw_json is not None:
        if not from_raw_json.is_file():
            raise FileNotFoundError(f"Fayl topilmadi: {from_raw_json}")
        raw_payload = json.loads(from_raw_json.read_text(encoding="utf-8-sig"))
        raw_rows = raw_payload.get("data", raw_payload) if isinstance(raw_payload, dict) else raw_payload
        if not isinstance(raw_rows, list):
            raise ValueError("JSON faylda `data` ro'yxati topilmadi.")
        acct = str(raw_payload.get("account_id", account_id or "act_offline_import")) if isinstance(raw_payload, dict) else (account_id or "act_offline_import")
        payload_currency = str(raw_payload.get("account_currency", "")).strip().upper() if isinstance(raw_payload, dict) else ""
        pages_fetched = 1
        is_truncated = bool(raw_payload.get("paging", {}).get("next")) if isinstance(raw_payload, dict) and isinstance(raw_payload.get("paging"), dict) else False
        source_type = "IMPORTED_GRAPH_API_JSON"
    else:
        fetched = fetch_live_meta_insights(
            account_id=account_id,
            level=level,
            date_preset=date_preset,
            limit=limit,
            max_pages=max_pages,
        )
        raw_rows = fetched["raw_rows"]
        acct = fetched["account_id"]
        payload_currency = str(fetched.get("account_currency") or "").strip().upper()
        pages_fetched = fetched["pages_fetched"]
        is_truncated = fetched["is_truncated"]
        source_type = fetched["data_source_type"]

    row_currencies = sorted({
        str(r.get("account_currency") or r.get("currency") or "").strip().upper()
        for r in raw_rows
        if isinstance(r, dict) and str(r.get("account_currency") or r.get("currency") or "").strip()
    })

    if currency_override.strip():
        effective_currency = currency_override.strip().upper()
        currency_source = "USER_OVERRIDE"
    elif row_currencies:
        effective_currency = row_currencies[0]
        currency_source = "META_ACCOUNT_CURRENCY"
    elif payload_currency:
        effective_currency = payload_currency
        currency_source = "META_ACCOUNT_CURRENCY"
    else:
        effective_currency = "USD"
        currency_source = "DEFAULT_USD_FALLBACK"

    normalized_rows = normalize_insights_rows(
        raw_rows,
        level=level,
        primary_conversion=primary_conversion,
        default_currency=effective_currency,
    )
    if not normalized_rows:
        raise ValueError("Tahlil qilish uchun hech qanday kampaniya/adset satri topilmadi.")

    ae = importlib.import_module("ad-export-analyzer")
    import tempfile
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".json", delete=False) as tmp:
        json.dump(normalized_rows, tmp, ensure_ascii=False)
        tmp_path = Path(tmp.name)
    try:
        analysis = ae.analyze_export(
            tmp_path,
            target_cpa=target_cpa,
            breakeven_roas=breakeven_roas,
            primary_conversion=primary_conversion,
            default_currency=effective_currency,
        )
    finally:
        tmp_path.unlink(missing_ok=True)

    result = {
        "schema": "tyrion.meta_insights_sync/v5.1",
        "synced_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "account_id": acct,
        "account_currency": effective_currency,
        "currency_source": currency_source,
        "graph_api_version": api_version,
        "data_source_type": source_type,
        "level": level,
        "date_preset": date_preset,
        "primary_conversion_filter": primary_conversion,
        "pagination": {
            "pages_fetched": pages_fetched,
            "is_truncated": is_truncated,
            "max_pages_limit": max_pages,
        },
        "normalized_rows_count": len(normalized_rows),
        "normalized_rows": normalized_rows,
        "audit_report": analysis,
    }
    if save_out is not None:
        tcore.atomic_write_json(save_out, result)
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="meta-insights-sync.py",
        description="Tyrion v5.1 Live Meta Ads Graph API v26.0 Insights Connector (Cursor Pagination + Currency + Conversion Separation)",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_pull = sub.add_parser("pull", help="Meta Ads akkauntidan (yoki Graph API JSON eksportidan) statistikalarni tortish va tahlil qilish")
    p_pull.add_argument("--account-id", default="", help="Meta Ad Account ID (masalan: act_1234567890)")
    p_pull.add_argument("--level", default="adset", choices=["campaign", "adset", "ad"])
    p_pull.add_argument("--date-preset", default="last_7d", choices=["today", "yesterday", "last_7d", "last_14d", "last_30d", "maximum"])
    p_pull.add_argument("--target-cpa", type=float, default=15.0)
    p_pull.add_argument("--breakeven-roas", type=float, default=2.0)
    p_pull.add_argument(
        "--primary-conversion",
        default="auto",
        choices=["auto", "purchase", "lead", "messaging"],
        help="Qaysi konversiya oilasi bo'yicha CPA hisoblansin (auto|purchase|lead|messaging)",
    )
    p_pull.add_argument("--currency", default="", help="Valyuta kodini majburiy belgilash (masalan: UZS, USD, KZT)")
    p_pull.add_argument("--limit", type=int, default=100, help="Har bir Graph API sahifasidagi satrlar soni (1..500)")
    p_pull.add_argument("--max-pages", type=int, default=20, help="Maksimal cursor pagination sahifalar soni")
    p_pull.add_argument("--from-raw-json", default="", help="Offline tekshirish uchun Meta Graph API insights JSON fayli")
    p_pull.add_argument("--out", default="", help="Natijani JSON faylga atomik saqlash yo'li")
    p_pull.add_argument("--json", action="store_true")

    p_ver = sub.add_parser("verify-live", help="Haqiqiy META_ACCESS_TOKEN va reklama akkaunti valyutasi/holatini tekshirish")
    p_ver.add_argument("--account-id", default="", help="Meta Ad Account ID (masalan: act_1234567890)")
    p_ver.add_argument("--json", action="store_true")

    args = parser.parse_args(argv)
    try:
        if args.command == "verify-live":
            res = verify_live_connection(account_id=args.account_id)
            if getattr(args, "json", False):
                print(json.dumps(res, ensure_ascii=False, indent=2))
            else:
                print(f"✓ Meta Graph API {res['graph_api_version']} ulandi: {res['account_id']} ({res['account_name']}) | Valyuta: {res['account_currency']}")
            return 0

        raw_path = Path(args.from_raw_json) if args.from_raw_json else None
        out_path = Path(args.out) if args.out else None
        res = sync_and_analyze(
            account_id=args.account_id,
            level=args.level,
            date_preset=args.date_preset,
            target_cpa=args.target_cpa,
            breakeven_roas=args.breakeven_roas,
            primary_conversion=args.primary_conversion,
            currency_override=args.currency,
            limit=args.limit,
            max_pages=args.max_pages,
            from_raw_json=raw_path,
            save_out=out_path,
        )
    except Exception as exc:
        print(f"Xato: {tcore.redact_secrets(str(exc))}", file=sys.stderr)
        return 2

    if getattr(args, "json", False):
        print(json.dumps(res, ensure_ascii=False, indent=2))
        return 0

    rep = res["audit_report"]
    s = rep["summary"]
    curr = res["account_currency"]
    print("=" * 76)
    print(f"  🔄 TYRION v5.1 META INSIGHTS SYNC — {res['account_id']} ({res['data_source_type']})")
    print("=" * 76)
    print(f"  Graph API Versiyasi : {res['graph_api_version']} | Daraja: {res['level']} | Davr: {res['date_preset']} | Sahifalar: {res['pagination']['pages_fetched']}")
    print(f"  Akkaunt Valyutasi   : {curr} ({res['currency_source']}) | Konversiya filtri: {res['primary_conversion_filter']}")
    print(f"  Jami Xarajat (Spend): {s['total_spend']} {curr} | Konversiyalar: {s['total_conversions']} | Blended CPA: {s['blended_cpa']} {curr}")
    if rep.get("mixed_conversion_warning"):
        print(f"  ⚠ {rep['mixed_conversion_warning']}")
    print("-" * 76)
    for d in rep["decisions"]:
        print(f"  • [{d['verdict']}] {d['name']} ({d['conversion_family']}) — Spend: {d['spend']} {curr}, Conv: {d['conversions']}, CPA: {d['cpa']} {curr}, Freq: {d['frequency']}")
        print(f"      Amal: {d['action']}")
    print("=" * 76)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
