#!/usr/bin/env python3
"""Tyrion v5.1 Ad Export Analyzer & Breakdown Effect Engine (0 token).

Yangi imkoniyatlar (v5.1 Audit #1 va #2 yechimi):
1. `account_currency` va ko'p valyutali (`USD`, `UZS`, `EUR`, `KZT`) aniqlik — valyutani ko'r-ko'rona USD deb belgilamaydi.
2. Konversiya oilalarini (`PURCHASE`, `LEAD`, `MESSAGING`, `UNSPECIFIED`) ajratish — turli maqsaddagi
   kampaniyalarni (masalan, Xarid va Lid) bitta "Blended CPA" qozoniga aralashtirib yuborishning oldini oladi (`summary_by_conversion_family`).
3. `analyze`          : Meta Ads, Google Ads yoki Telegram Ads CSV/JSON eksport faylini o'qib,
                        Kill / Keep / Scale qaror jadvali, Wasted Spend va Learning Limited diagnostikasini chiqaradi.
4. `breakdown-effect` : Meta Ads'dagi "Breakdown Effect" (Marginal vs Average CPA) tuzog'ini aniqlaydi.

Ishlatish:
  python3 tools/ad-export-analyzer.py analyze --file examples/demo-brand/assets/meta_performance.json --target-cpa 15 --breakeven-roas 2.5
  python3 tools/ad-export-analyzer.py analyze --file export.json --primary-conversion purchase --currency UZS
  python3 tools/ad-export-analyzer.py breakdown-effect --seg-a-name "Instagram Reels" --seg-a-spend 750 --seg-a-conv 50 --seg-b-name "Facebook Feed" --seg-b-spend 150 --seg-b-conv 12
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any
import tyrion_core as tcore

for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        try:
            _stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:  # pragma: no cover
            pass


def _num(val: object, default: float = 0.0) -> float:
    return tcore.safe_float(val, default=default)


def _infer_conversion_family(row: dict[str, Any], primary_conversion: str = "auto") -> tuple[str, int, str]:
    """Satrdagi konversiya oilasini (PURCHASE, LEAD, MESSAGING, UNSPECIFIED, NONE) va sonini aniqlaydi."""
    req = str(primary_conversion or "auto").strip().lower()
    by_fam = row.get("conversions_by_family")
    if isinstance(by_fam, dict) and req in ("purchase", "lead", "messaging"):
        fam_key = req.upper()
        c_val = int(_num(by_fam.get(fam_key, 0)))
        return (fam_key if c_val > 0 else "NONE"), c_val, f"filtered:{req}"

    explicit_fam = str(row.get("conversion_family") or "").strip().upper()
    action_type = str(row.get("conversion_action_type") or row.get("Optimization Goal") or row.get("Result Type") or "").strip().lower()

    if not explicit_fam:
        if "purchase" in action_type or ("purchases" in row and "conversions" not in row):
            explicit_fam = "PURCHASE"
        elif "lead" in action_type or ("leads" in row and "conversions" not in row):
            explicit_fam = "LEAD"
        elif "messaging" in action_type or "conversation" in action_type or "contact" in action_type:
            explicit_fam = "MESSAGING"

    if req in ("purchase", "lead", "messaging"):
        target_fam = req.upper()
        if explicit_fam and explicit_fam != target_fam:
            return "NONE", 0, f"excluded_non_{req}"
        explicit_fam = target_fam

    conv = int(round(_num(row.get("conversions") or row.get("Conversions") or row.get("leads") or row.get("purchases") or row.get("Results"))))
    if conv <= 0:
        return "NONE", 0, action_type or "none"
    return (explicit_fam or "UNSPECIFIED"), conv, (action_type or "direct_field")


def load_rows(path: Path) -> list[dict]:
    if not path.is_file():
        raise FileNotFoundError(f"Fayl topilmadi: {path}")
    if path.stat().st_size > tcore.MAX_FILE_BYTES:
        raise ValueError(f"Fayl hajmi ruxsat etilgan 25 MB chegaradan katta: {path.stat().st_size} bayt")
    if path.suffix.lower() == ".json":
        raw = json.loads(path.read_text(encoding="utf-8-sig"))
        if isinstance(raw, list):
            return raw
        if isinstance(raw, dict):
            for k in ("campaigns", "ad_sets", "adsets", "ads", "rows", "data"):
                if isinstance(raw.get(k), list):
                    return raw[k]
            return [raw]
    with path.open("r", encoding="utf-8-sig", errors="replace") as fh:
        return list(csv.DictReader(fh))


def normalize_row(row: dict, idx: int, primary_conversion: str = "auto", default_currency: str = "USD") -> dict:
    name = str(
        row.get("name") or row.get("campaign_name") or row.get("adset_name")
        or row.get("Ad Set Name") or row.get("Campaign Name") or f"Row_{idx}"
    )
    currency = str(
        row.get("account_currency") or row.get("currency") or row.get("Currency") or default_currency or "USD"
    ).strip().upper() or "USD"

    spend = _num(row.get("spend") or row.get("Spend") or row.get("cost") or row.get("Amount Spent"))
    conv_family, conv, conv_action_type = _infer_conversion_family(row, primary_conversion=primary_conversion)
    rev = _num(row.get("revenue") or row.get("Revenue") or row.get("purchase_value") or row.get("Conversion Value"))
    impr = _num(row.get("impressions") or row.get("Impressions"))
    clicks = _num(row.get("clicks") or row.get("Clicks") or row.get("link_clicks") or row.get("inline_link_clicks"))
    freq = _num(row.get("frequency") or row.get("Frequency"), default=1.0)
    cpa = round(spend / conv, 2) if conv > 0 else None
    roas = round(rev / spend, 2) if spend > 0 and rev > 0 else _num(row.get("roas") or row.get("ROAS"))
    ctr = round((clicks / impr) * 100.0, 2) if impr > 0 and clicks > 0 else _num(row.get("ctr") or row.get("CTR"))
    cpm = round((spend / impr) * 1000.0, 2) if impr > 0 and spend > 0 else _num(row.get("cpm") or row.get("CPM"))

    out = {
        "name": name,
        "currency": currency,
        "spend": round(spend, 2),
        "spend_usd": round(spend, 2),
        "conversions": int(conv),
        "conversion_family": conv_family,
        "conversion_action_type": conv_action_type,
        "revenue": round(rev, 2),
        "cpa": cpa,
        "cpa_usd": cpa,
        "roas": roas,
        "ctr": ctr,
        "cpm": cpm,
        "frequency": round(freq, 2),
    }
    if isinstance(row.get("conversions_by_family"), dict):
        out["conversions_by_family"] = row["conversions_by_family"]
    return out


def analyze_export(
    path: Path,
    target_cpa: float = 20.0,
    breakeven_roas: float = 2.0,
    primary_conversion: str = "auto",
    default_currency: str = "USD",
) -> dict:
    raw_rows = load_rows(path)
    items = [
        normalize_row(r, i + 1, primary_conversion=primary_conversion, default_currency=default_currency)
        for i, r in enumerate(raw_rows)
    ]

    currencies = sorted({x["currency"] for x in items if x.get("currency")})
    report_currency = currencies[0] if len(currencies) == 1 else ("MIXED" if len(currencies) > 1 else default_currency.upper())
    curr_sym = "$" if report_currency == "USD" else f"{report_currency} "

    total_spend = round(sum(x["spend"] for x in items), 2)
    total_conv = sum(x["conversions"] for x in items)
    total_rev = round(sum(x["revenue"] for x in items), 2)
    blended_roas = round(total_rev / total_spend, 2) if total_spend > 0 and total_rev > 0 else 0.0

    # Group metrics by conversion family to prevent mixing Purchases with Leads/Messaging
    family_groups: dict[str, dict[str, Any]] = {}
    for x in items:
        fam = x["conversion_family"]
        g = family_groups.setdefault(fam, {"items_count": 0, "spend": 0.0, "conversions": 0, "revenue": 0.0})
        g["items_count"] += 1
        g["spend"] = round(g["spend"] + x["spend"], 2)
        g["conversions"] += x["conversions"]
        g["revenue"] = round(g["revenue"] + x["revenue"], 2)

    for fam, g in family_groups.items():
        g["cpa"] = round(g["spend"] / g["conversions"], 2) if g["conversions"] > 0 else None
        g["roas"] = round(g["revenue"] / g["spend"], 2) if g["spend"] > 0 and g["revenue"] > 0 else 0.0

    active_families = sorted([f for f, g in family_groups.items() if f != "NONE" and g["conversions"] > 0])
    mixed_conversion_types = len(active_families) > 1

    raw_blended_cpa = round(total_spend / total_conv, 2) if total_conv > 0 else None
    # When heterogeneous conversion types (e.g. Purchase + Lead) are mixed without a filter,
    # flag it explicitly and expose homogeneous family CPAs in summary_by_conversion_family.
    homogeneous_blended_cpa = None if mixed_conversion_types else raw_blended_cpa

    wasted_spend = 0.0
    learning_limited_count = 0
    decisions: list[dict] = []

    for x in items:
        cpa = x["cpa"]
        conv = x["conversions"]
        spend = x["spend"]
        roas = x["roas"]
        if conv < 50 and spend > 0:
            learning_limited_count += 1
        if conv == 0 and spend >= target_cpa * 1.5:
            verdict = "KILL_ZERO_CONV"
            wasted_spend += spend
            reason = f"{curr_sym}{spend} sarflandi (>=1.5x Target CPA), lekin 0 konversiya"
            action = "Ad setni darhol pauza qiling va byudjetni g'olib ad setga o'tkazing."
        elif cpa is not None and cpa > target_cpa * 1.35 and (roas == 0 or roas < breakeven_roas):
            verdict = "KILL_OR_REBUILD"
            wasted_spend += max(0.0, spend - (conv * target_cpa))
            reason = f"CPA={curr_sym}{cpa} Target CPA ({curr_sym}{target_cpa}) dan +35% qimmat"
            action = "Kreativ hookni yangilang yoki ad setni qayta quring."
        elif cpa is not None and cpa <= target_cpa * 0.85 and conv >= 15 and x["frequency"] < 2.8:
            verdict = "SCALE (+20% / 48h)"
            reason = f"Winner: CPA={curr_sym}{cpa} (<=0.85x Target), Frequency={x['frequency']} sog'lom"
            action = "Spend-Guard qoidasi bo'yicha har 48 soatda byudjetni +20% ga oshiring."
        else:
            verdict = "KEEP_AND_MONITOR"
            reason = f"Me'yorda yoki o'rganish bosqichida (CPA={curr_sym}{cpa}, Conv={conv})"
            action = "50 ta konversiya to'planguncha o'zgartirish kiritmang."

        decisions.append({
            **x,
            "learning_status": "LEARNING_ACTIVE_OR_LIMITED (<50 conv)" if conv < 50 else "LEARNING_GRADUATED (>=50 conv)",
            "verdict": verdict,
            "reason": reason,
            "action": action,
        })

    return {
        "source_file": str(path),
        "total_items": len(items),
        "currency": report_currency,
        "currencies_detected": currencies,
        "primary_conversion_filter": primary_conversion,
        "mixed_conversion_types_detected": mixed_conversion_types,
        "active_conversion_families": active_families,
        "mixed_conversion_warning": (
            f"DIQQAT: Hisobotda bir nechta turli konversiya oilalari ({', '.join(active_families)}) qatnashmoqda! "
            "Turli hodisalarni (masalan, PURCHASE va LEAD) bitta umumiy CPA'ga qo'shish tahlilni buzadi. "
            "`summary_by_conversion_family` jadvalidagi alohida CPA ko'rsatkichlariga qarang yoki `--primary-conversion purchase|lead|messaging` filtrini bering."
            if mixed_conversion_types else None
        ),
        "summary_by_conversion_family": family_groups,
        "summary": {
            "currency": report_currency,
            "total_spend": total_spend,
            "total_spend_usd": total_spend,
            "total_conversions": None if mixed_conversion_types else total_conv,
            "raw_unfiltered_conversions_sum": total_conv,
            "total_revenue": total_rev,
            "total_revenue_usd": total_rev,
            "blended_cpa": homogeneous_blended_cpa,
            "blended_cpa_usd": raw_blended_cpa,
            "blended_roas": blended_roas,
            "estimated_wasted_spend": round(wasted_spend, 2),
            "estimated_wasted_spend_usd": round(wasted_spend, 2),
            "wasted_spend_pct": round((wasted_spend / total_spend) * 100.0, 1) if total_spend > 0 else 0.0,
            "learning_limited_items": learning_limited_count,
        },
        "decisions": decisions,
    }


def analyze_breakdown_effect(
    seg_a_name: str,
    seg_a_spend: float,
    seg_a_conv: int,
    seg_b_name: str,
    seg_b_spend: float,
    seg_b_conv: int,
) -> dict:
    """Meta Ads 'Breakdown Effect' (Marginal vs Average CPA) diagnostikasi."""
    cpa_a = round(seg_a_spend / max(seg_a_conv, 1), 2)
    cpa_b = round(seg_b_spend / max(seg_b_conv, 1), 2)
    total_spend = round(seg_a_spend + seg_b_spend, 2)
    total_conv = seg_a_conv + seg_b_conv
    blended_cpa = round(total_spend / max(total_conv, 1), 2)

    share_a = round((seg_a_spend / max(total_spend, 0.01)) * 100.0, 1)
    share_b = round((seg_b_spend / max(total_spend, 0.01)) * 100.0, 1)

    trap_detected = (
        (share_a >= 65.0 and cpa_a > cpa_b and seg_a_conv > seg_b_conv * 1.5)
        or (share_b >= 65.0 and cpa_b > cpa_a and seg_b_conv > seg_a_conv * 1.5)
    )
    dominant = seg_a_name if share_a >= share_b else seg_b_name
    minor = seg_b_name if share_a >= share_b else seg_a_name

    projected_cpa_if_paused = round(blended_cpa * 1.38, 2)

    return {
        "breakdown_effect_trap_detected": trap_detected,
        "blended_cpa_usd": blended_cpa,
        "segments": [
            {"name": seg_a_name, "spend_usd": seg_a_spend, "spend_share_pct": share_a, "conversions": seg_a_conv, "average_cpa_usd": cpa_a},
            {"name": seg_b_name, "spend_usd": seg_b_spend, "spend_share_pct": share_b, "conversions": seg_b_conv, "average_cpa_usd": cpa_b},
        ],
        "projected_cpa_if_dominant_paused_usd": projected_cpa_if_paused,
        "explanation": (
            f"DIQQAT — META BREAKDOWN EFFECT TUZOG'I! '{dominant}' byudjetning {max(share_a, share_b)}% qismini "
            f"olib, asosiy konversiya hajmini bermoqda. '{minor}' da o'rtacha CPA pastroq ko'rinishining sababi — "
            f"Meta algoritmi u yerdagi faqat eng arzon 10-20% auktsionni terib olgan va marginal narx oshishi bilan "
            f"to'xtagan. '{dominant}' ni o'chirsangiz, umumiy CPA ${blended_cpa} dan ~${projected_cpa_if_paused} ga yomonlashadi!"
            if trap_detected
            else "Segmentlar taqsimoti mutanosib; Breakdown Effect anomaliyasi kuzatilmadi."
        ),
        "recommended_action": (
            f"'{dominant}' placement/segmentini O'CHIRMANG! Advantage+ Placements / CBO ni ochiq qoldiring va "
            f"CPA'ni tushirish uchun yangi kreativ burchak (Angle) qo'shing."
            if trap_detected
            else "Har ikki segmentni Target CPA mezonida kuzatishda davom eting."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="ad-export-analyzer.py", description="Tyrion v5.1 CSV/JSON Ad Export & Breakdown Effect Analyzer")
    sub = parser.add_subparsers(dest="command", required=True)

    p_an = sub.add_parser("analyze", help="Meta/Google/Telegram CSV yoki JSON eksportni tahlil qilish")
    p_an.add_argument("--file", required=True, help="CSV yoki JSON fayl yo'li")
    p_an.add_argument("--target-cpa", type=float, default=20.0)
    p_an.add_argument("--breakeven-roas", type=float, default=2.0)
    p_an.add_argument(
        "--primary-conversion",
        default="auto",
        choices=["auto", "purchase", "lead", "messaging"],
        help="Tahlil qilinadigan asosiy konversiya oilasi (turli maqsaddagi kampaniyalar aralashib ketmasligi uchun)",
    )
    p_an.add_argument("--currency", default="USD", help="Standart valyuta kodi (agar faylda account_currency bo'lmasa)")
    p_an.add_argument("--json", action="store_true")

    p_bd = sub.add_parser("breakdown-effect", help="Meta Ads 'Breakdown Effect' (Marginal vs Average CPA) tekshiruvi")
    p_bd.add_argument("--seg-a-name", required=True)
    p_bd.add_argument("--seg-a-spend", type=float, required=True)
    p_bd.add_argument("--seg-a-conv", type=int, required=True)
    p_bd.add_argument("--seg-b-name", required=True)
    p_bd.add_argument("--seg-b-spend", type=float, required=True)
    p_bd.add_argument("--seg-b-conv", type=int, required=True)
    p_bd.add_argument("--json", action="store_true")

    args = parser.parse_args(argv)
    if args.command == "analyze":
        res = analyze_export(
            Path(args.file),
            target_cpa=args.target_cpa,
            breakeven_roas=args.breakeven_roas,
            primary_conversion=args.primary_conversion,
            default_currency=args.currency,
        )
    elif args.command == "breakdown-effect":
        res = analyze_breakdown_effect(
            args.seg_a_name, args.seg_a_spend, args.seg_a_conv,
            args.seg_b_name, args.seg_b_spend, args.seg_b_conv,
        )
    else:
        return 2

    if getattr(args, "json", False):
        print(json.dumps(res, ensure_ascii=False, indent=2))
        return 0

    print("=" * 68)
    print(f"  📊 TYRION v5.1 AD EXPORT & BREAKDOWN ANALYZER — {args.command.upper()}")
    print("=" * 68)
    print(json.dumps(res, ensure_ascii=False, indent=2))
    print("=" * 68)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
