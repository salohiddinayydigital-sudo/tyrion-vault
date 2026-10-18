#!/usr/bin/env python3
"""Tyrion CAPI & UTM Builder — Meta CAPI v22.0 SHA-256 PII Normalizer, EMQ Scorer va Telegram Bot UTM Generator (0 token).

Buyruqlar:
  python3 tools/capi-utm-builder.py utm --url "https://brand.uz/offer" --platform meta --campaign "real_estate_q4" --bot "brand_uz_bot"
  python3 tools/capi-utm-builder.py capi-payload --event "Lead" --phone "+998 (90) 123-45-67" --email "Ali@Mail.uz" --city "Tashkent" --value 150 --currency USD --order-id "CRM_901"
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import time
from urllib.parse import urlencode
import tyrion_core as tcore

for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        try:
            _stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:  # pragma: no cover
            pass


def sha256_norm(val: str) -> str:
    return hashlib.sha256(val.strip().lower().encode("utf-8")).hexdigest()


def normalize_phone(phone: str) -> str:
    digits = re.sub(r"\D+", "", phone)
    if len(digits) == 9 and digits.startswith(("9", "8", "7", "3", "5")):
        digits = "998" + digits
    return digits


def build_utm_links(base_url: str, platform: str, campaign: str, bot_username: str = "") -> dict:
    base_url = tcore.sanitize_url(base_url)
    clean_camp = re.sub(r"[^a-zA-Z0-9_\-]+", "_", campaign.strip().lower()).strip("_")[:24]
    if platform == "meta":
        params = {
            "utm_source": "ig_fb",
            "utm_medium": "paid_social",
            "utm_campaign": "{{campaign.name}}",
            "utm_content": "{{adset.name}}__{{ad.name}}",
            "utm_term": "{{placement}}",
        }
    elif platform == "google":
        params = {
            "utm_source": "google",
            "utm_medium": "cpc",
            "utm_campaign": "{campaignid}",
            "utm_content": "{adgroupid}__{creative}",
            "utm_term": "{keyword}",
        }
    else:
        params = {
            "utm_source": "telegram",
            "utm_medium": "sponsored_msg",
            "utm_campaign": clean_camp,
            "utm_content": "ch_seed_01",
        }

    sep = "&" if "?" in base_url else "?"
    # Keep dynamic braces unescaped for Meta/Google macros
    query_str = "&".join(f"{k}={v}" for k, v in params.items())
    full_url = f"{base_url}{sep}{query_str}"

    tg_links = {}
    if bot_username:
        bot = bot_username.lstrip("@").strip()
        # Telegram Bot API limit: ?start= payload MUST be <= 64 chars (A-Za-z0-9_-)
        start_payload = f"{platform[:2]}_{clean_camp}_ad01"[:64]
        tg_links = {
            "telegram_bot_deeplink": f"https://t.me/{bot}?start={start_payload}",
            "start_payload": start_payload,
            "payload_length": len(start_payload),
            "within_64_char_limit": len(start_payload) <= 64,
        }

    return {
        "platform": platform,
        "base_url": base_url,
        "full_tracked_url": full_url,
        "utm_parameters": params,
        "telegram_bot_tracking": tg_links,
    }


def build_capi_payload(
    event_name: str,
    phone: str = "",
    email: str = "",
    first_name: str = "",
    city: str = "tashkent",
    country: str = "uz",
    fbp: str = "fb.1.1729200000.123456789",
    fbc: str = "fb.1.1729200000.IwAR0xyz",
    value: float = 0.0,
    currency: str = "USD",
    order_id: str = "LEAD_001",
    event_source_url: str = "https://brand.uz/",
) -> dict:
    user_data: dict[str, object] = {
        "country": [sha256_norm(country)],
    }
    emq_points = 1.5  # country + base

    if phone:
        norm_ph = normalize_phone(phone)
        user_data["ph"] = [sha256_norm(norm_ph)]
        emq_points += 3.2
    if email:
        user_data["em"] = [sha256_norm(email)]
        emq_points += 2.2
    if first_name:
        user_data["fn"] = [sha256_norm(first_name)]
        emq_points += 0.6
    if city:
        user_data["ct"] = [sha256_norm(city)]
        emq_points += 0.4
    if fbp:
        user_data["fbp"] = fbp
        emq_points += 1.0
    if fbc:
        user_data["fbc"] = fbc
        emq_points += 1.1

    emq_score = round(min(10.0, emq_points), 1)
    # Deterministic event_id so Browser Pixel and Server CAPI deduplicate 100%
    event_id = f"evt_{event_name.lower()}_{re.sub(r'[^a-zA-Z0-9]+', '', order_id)}"

    payload = {
        "data": [
            {
                "event_name": event_name,
                "event_time": int(time.time()),
                "action_source": "website",
                "event_id": event_id,
                "event_source_url": event_source_url,
                "user_data": user_data,
                "custom_data": {
                    "currency": currency.upper(),
                    "value": round(tcore.safe_float(value, default=0.0, min_val=0.0, field_name="value"), 2),
                    "order_id": order_id,
                },
            }
        ]
    }
    return {
        "estimated_emq_score_10": emq_score,
        "emq_status": "EXCELLENT (>=8.0)" if emq_score >= 8.0 else ("GOOD (6.5-7.9)" if emq_score >= 6.5 else "WEAK (<6.5 — telefon va fbc/fbp qo'shing!)"),
        "deduplication_instruction": f"Browser Pixel da `fbq('track', '{event_name}', {{...}}, {{eventID: '{event_id}'}})` chaqirilishi SHART!",
        "capi_v22_payload": payload,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="capi-utm-builder.py", description="Meta CAPI v22 Payload & Telegram/Ads UTM Builder")
    sub = parser.add_subparsers(dest="command", required=True)

    p_utm = sub.add_parser("utm", help="Meta/Google dinamik UTM va Telegram Bot <=64 belgi deep-link yaratish")
    p_utm.add_argument("--url", required=True)
    p_utm.add_argument("--platform", default="meta", choices=["meta", "google", "telegram"])
    p_utm.add_argument("--campaign", default="uz_launch")
    p_utm.add_argument("--bot", default="", help="Telegram bot username (masalan: brand_bot)")
    p_utm.add_argument("--json", action="store_true")

    p_capi = sub.add_parser("capi-payload", help="Meta CAPI v22.0 SHA-256 xeshlangan payload va EMQ ballini hisoblash")
    p_capi.add_argument("--event", default="Lead")
    p_capi.add_argument("--phone", default="")
    p_capi.add_argument("--email", default="")
    p_capi.add_argument("--first-name", default="")
    p_capi.add_argument("--city", default="tashkent")
    p_capi.add_argument("--value", type=float, default=0.0)
    p_capi.add_argument("--currency", default="USD")
    p_capi.add_argument("--order-id", default="CRM_1001")
    p_capi.add_argument("--json", action="store_true")

    args = parser.parse_args(argv)
    if args.command == "utm":
        res = build_utm_links(args.url, args.platform, args.campaign, args.bot)
    elif args.command == "capi-payload":
        res = build_capi_payload(
            event_name=args.event, phone=args.phone, email=args.email,
            first_name=args.first_name, city=args.city, value=args.value,
            currency=args.currency, order_id=args.order_id,
        )
    else:
        return 2

    if getattr(args, "json", False):
        print(json.dumps(res, ensure_ascii=False, indent=2))
        return 0

    print("=" * 68)
    print(f"  📡 TYRION CAPI & UTM BUILDER — {args.command.upper()}")
    print("=" * 68)
    print(json.dumps(res, ensure_ascii=False, indent=2))
    print("=" * 68)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
