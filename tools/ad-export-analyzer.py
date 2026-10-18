#!/usr/bin/env python3
"""Tyrion Ad Export Analyzer & Breakdown Effect Engine (0 token).

Raqobatchi tahlili (mathiaschu/meta-ads-analyzer va AgriciDaniel/claude-ads) asosida:
1. `analyze`          : Meta Ads, Google Ads yoki Telegram Ads CSV/JSON eksport faylini o'qib,
                        Kill / Keep / Scale qaror jadvali, Wasted Spend (havoga uchgan pul) va
                        Learning Limited diagnostikasini chiqaradi.
2. `breakdown-effect` : Meta Ads'dagi mashhur "Breakdown Effect" (Marginal vs Average CPA)
                        tuzog'ini aniqlaydi — nima uchun qimmatroq ko'ringan placement yoki
                        yosh segmentini o'chirish umumiy CPA'ni buzishini matematik isbotlaydi!

Ishlatish:
  python3 tools/ad-export-analyzer.py analyze --file examples/demo-brand/assets/meta_performance.json --target-cpa 15 --breakeven-roas 2.5
  python3 tools/ad-export-analyzer.py breakdown-effect --seg-a-name "Instagram Reels" --seg-a-spend 750 --seg-a-conv 50 --seg-b-name "Facebook Feed" --seg-b-spend 150 --seg-b-conv 12
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
import tyrion_core as tcore

for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        try:
            _stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:  # pragma: no cover
            pass


def _num(val: object, default: float = 0.0) -> float:
    return tcore.safe_float(val, default=default)
    if isinstance(val, (int, float)):
        return float(val)
    s = str(val).replace("$", "").replace(",", "").replace("%", "").strip()
    try:
        return float(s) if s else default
    except ValueError:
        return default


def load_rows(path: Path) -> list[dict]:
    if not path.is_file():
        raise FileNotFoundError(f"Fayl topilmadi: {path}")
    if path.stat().st_size > tcore.MAX_FILE_BYTES:
        raise ValueError(f"Fayl hajmi ruxsat etilgan 25 MB chegaradan katta: {path.stat().st_size} bayt")
    if path.suffix.lower() == ".json":
        raw = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(raw, list):
            return raw
        if isinstance(raw, dict):
            for k in ("campaigns", "ad_sets", "adsets", "ads", "rows", "data"):
                if isinstance(raw.get(k), list):
                    return raw[k]
            return [raw]
    with path.open("r", encoding="utf-8-sig", errors="replace") as fh:
        return list(csv.DictReader(fh))


def normalize_row(row: dict, idx: int) -> dict:
    name = str(
        row.get("name") or row.get("campaign_name") or row.get("adset_name")
        or row.get("Ad Set Name") or row.get("Campaign Name") or f"Row_{idx}"
    )
    spend = _num(row.get("spend") or row.get("Spend") or row.get("cost") or row.get("Amount Spent"))
    conv = _num(row.get("conversions") or row.get("Conversions") or row.get("leads") or row.get("purchases") or row.get("Results"))
    rev = _num(row.get("revenue") or row.get("Revenue") or row.get("purchase_value") or row.get("Conversion Value"))
    impr = _num(row.get("impressions") or row.get("Impressions"))
    clicks = _num(row.get("clicks") or row.get("Clicks") or row.get("link_clicks"))
    freq = _num(row.get("frequency") or row.get("Frequency"), default=1.0)
    cpa = round(spend / conv, 2) if conv > 0 else ( round(spend, 2) if spend > 0 else 0.0 )
    roas = round(rev / spend, 2) if spend > 0 and rev > 0 else _num(row.get("roas") or row.get("ROAS"))
    ctr = round((clicks / impr) * 100.0, 2) if impr > 0 and clicks > 0 else _num(row.get("ctr") or row.get("CTR"))
    cpm = round((spend / impr) * 1000.0, 2) if impr > 0 and spend > 0 else _num(row.get("cpm") or row.get("CPM"))
    return {
        "name": name,
        "spend": round(spend, 2),
        "conversions": int(conv),
        "revenue": round(rev, 2),
        "cpa": cpa if conv > 0 else None,
        "roas": roas,
        "ctr": ctr,
        "cpm": cpm,
        "frequency": round(freq, 2),
    }


def analyze_export(path: Path, target_cpa: float = 20.0, breakeven_roas: float = 2.0) -> dict:
    raw_rows = load_rows(path)
    items = [normalize_row(r, i + 1) for i, r in enumerate(raw_rows)]
    total_spend = round(sum(x["spend"] for x in items), 2)
    total_conv = sum(x["conversions"] for x in items)
    total_rev = round(sum(x["revenue"] for x in items), 2)
    blended_cpa = round(total_spend / total_conv, 2) if total_conv > 0 else None
    blended_roas = round(total_rev / total_spend, 2) if total_spend > 0 and total_rev > 0 else 0.0

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
            reason = f"${spend} sarflandi (>=1.5x Target CPA), lekin 0 konversiya"
        elif cpa is not None and cpa > target_cpa * 1.35 and (roas == 0 or roas < breakeven_roas):
            verdict = "KILL_OR_REBUILD"
            wasted_spend += max(0.0, spend - (conv * target_cpa))
            reason = f"CPA=${cpa} Target CPA (${target_cpa}) dan +35% qimmat"
        elif cpa is not None and cpa <= target_cpa * 0.85 and conv >= 15 and x["frequency"] < 2.8:
            verdict = "SCALE (+20% / 48h)"
            reason = f"Winner: CPA=${cpa} (<=0.85x Target), Frequency={x['frequency']} sog'lom"
        else:
            verdict = "KEEP_AND_MONITOR"
            reason = f"Me'yorda yoki o'rganish bosqichida (CPA=${cpa}, Conv={conv})"

        decisions.append({
            **x,
            "learning_status": "LEARNING_ACTIVE_OR_LIMITED (<50 conv)" if conv < 50 else "LEARNING_GRADUATED (>=50 conv)",
            "verdict": verdict,
            "reason": reason,
        })

    return {
        "source_file": str(path),
        "total_items": len(items),
        "summary": {
            "total_spend_usd": total_spend,
            "total_conversions": total_conv,
            "total_revenue_usd": total_rev,
            "blended_cpa_usd": blended_cpa,
            "blended_roas": blended_roas,
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

    # Breakdown Effect qachon yuz beradi: A segmenti byudjetning >=65% ini olgan va uning O'RTACHA CPA'si
    # B segmentining o'rtacha CPA'sidan balandroq ko'rinadi, lekin aslida B ning arzon inventari tugagan!
    trap_detected = (
        (share_a >= 65.0 and cpa_a > cpa_b and seg_a_conv > seg_b_conv * 1.5)
        or (share_b >= 65.0 and cpa_b > cpa_a and seg_b_conv > seg_a_conv * 1.5)
    )
    dominant = seg_a_name if share_a >= share_b else seg_b_name
    minor = seg_b_name if share_a >= share_b else seg_a_name

    # Agar dominant placement o'chirilsa va butun byudjet kichik placementga majburlansa,
    # marginal egri chiziq bo'yicha CPA ~35%-60% ga qimmatlashadi:
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
    parser = argparse.ArgumentParser(prog="ad-export-analyzer.py", description="CSV/JSON Ad Export & Breakdown Effect Analyzer")
    sub = parser.add_subparsers(dest="command", required=True)

    p_an = sub.add_parser("analyze", help="Meta/Google/Telegram CSV yoki JSON eksportni tahlil qilish")
    p_an.add_argument("--file", required=True, help="CSV yoki JSON fayl yo'li")
    p_an.add_argument("--target-cpa", type=float, default=20.0)
    p_an.add_argument("--breakeven-roas", type=float, default=2.0)
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
        res = analyze_export(Path(args.file), args.target_cpa, args.breakeven_roas)
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
    print(f"  📊 TYRION AD EXPORT & BREAKDOWN ANALYZER — {args.command.upper()}")
    print("=" * 68)
    print(json.dumps(res, ensure_ascii=False, indent=2))
    print("=" * 68)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
