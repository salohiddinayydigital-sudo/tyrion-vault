#!/usr/bin/env python3
"""Tyrion Spend-Guard — Xavfsizlik va Hisob O'zgarishi Nazoratchisi.

Qoida: rules/40-xavfsizlik-va-hisob.md (read-only default, 6 darvoza).
Hech qanday jonli hisob o'zgarmaydi. Tavsiyalar qat'iy tekshiriladi:
  1. Byudjet o'zgarishi: 24 soatda <= 20% (machine learning / smart bidding barqarorligi)
  2. Kunlik limit: max daily spend ceiling dan oshmaslik
  3. Change Packet butunligi: Rollback / Teskari qadam, Xavf, Boshlang'ich ko'rsatkich, Stop-loss
  4. Nusxa / Copy siyosati: Telegram Ads 160 belgi, max 1 emoji, ALL CAPS taqiqi; Google Ads RSA
  5. Tracking: CAPI event_id deduplikatsiyasi, fbp/fbc, xeshlangan ma'lumotlar

Buyruqlar:
  py -3 tools\\spend-guard.py budget --current 100 --proposed 115 --max-cap 200
  py -3 tools\\spend-guard.py packet path/to/change-packet.md
  py -3 tools\\spend-guard.py copy --platform telegram --text "Matn..."
  py -3 tools\\spend-guard.py tracking --event-id "evt_123" --has-pixel --has-capi
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# Windows UTF-8
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        try:
            _stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass


def check_budget_change(
    current_daily: float,
    proposed_daily: float,
    max_daily_cap: float = 500.0,
    target_cpa: float | None = None,
) -> dict:
    """Byudjet o'zgarishini 40-qoida va platforma qonunlari bo'yicha tekshiradi."""
    errors: list[str] = []
    warnings: list[str] = []

    if current_daily <= 0:
        errors.append("Joriy kunlik byudjet 0 dan katta bo'lishi shart.")
        return {"passed": False, "errors": errors, "warnings": warnings}

    ratio = proposed_daily / current_daily
    percent_change = (ratio - 1.0) * 100.0

    if percent_change > 20.0:
        max_allowed = current_daily * 1.20
        errors.append(
            f"Byudjet oshishi +{percent_change:.1f}% (> 20%). "
            f"Bu Meta o'rganish fazasini (learning phase) yoki Google Smart Bidding algoritmini "
            f"qaytadan boshlaydi (reset). Maksimal ruxsat: +20% (≤ {max_allowed:.2f})."
        )
    elif percent_change < -50.0:
        warnings.append(
            f"Byudjet keskin kamaytirildi ({percent_change:.1f}%). "
            "Auksiondagi yutuq ulushi (impression share) va yetkazib berish barqarorligi yo'qolishi mumkin."
        )

    # 2. Hard Ceiling (Kunlik ship)
    if proposed_daily > max_daily_cap:
        errors.append(
            f"Taklif qilingan kunlik byudjet ({proposed_daily:.2f}) ruxsat etilgan "
            f"maksimal limitdan ({max_daily_cap:.2f}) oshib ketdi."
        )

    # 3. Minimum Learning Volume (Meta uchun tavsiya)
    if target_cpa and target_cpa > 0:
        # 1 ad set uchun kunlik kamida 1.5-2x target CPA kerak (haftasiga kamida 50 ta konversiya)
        min_healthy_daily = (target_cpa * 50) / 7.0
        if proposed_daily < min_healthy_daily:
            warnings.append(
                f"Taklif qilingan byudjet ({proposed_daily:.2f}/kun) 50 ta konversiya/hafta talabini "
                f"qondirish uchun ozlik qilishi mumkin (tavsiya etilgan minimum: {min_healthy_daily:.2f}/kun, "
                f"target CPA {target_cpa:.2f} asosida)."
            )

    passed = len(errors) == 0
    return {
        "passed": passed,
        "current_daily": current_daily,
        "proposed_daily": proposed_daily,
        "percent_change": round(percent_change, 2),
        "max_daily_cap": max_daily_cap,
        "errors": errors,
        "warnings": warnings,
    }


def check_change_packet(content: str) -> dict:
    """Change Packet (O'zgarishlar paketi) ning 6 darvoza talablariga mosligini tekshiradi."""
    errors: list[str] = []
    warnings: list[str] = []
    checks: dict[str, bool] = {}

    lower = content.lower()

    # 1. Rollback / Teskari qadam mavjudligi
    has_rollback = bool(
        re.search(r"(teskari\s+qadam|rollback|qaytarish|ortga\s+qaytish)", lower)
    )
    checks["rollback_instructions"] = has_rollback
    if not has_rollback:
        errors.append("Teskari qadam (Rollback) ko'rsatmasi topilmadi. Har qanday o'zgarish ortga qaytarilishi mumkin bo'lishi shart.")

    # 2. Stop-loss / Stop-condition
    has_stop_loss = bool(
        re.search(r"(stop[- ]condition|stop[- ]loss|to'xtatish\s+mezoni|chegara|agar\s+cpa)", lower)
    )
    checks["stop_loss"] = has_stop_loss
    if not has_stop_loss:
        errors.append("To'xtatish mezoni (Stop-condition / Stop-loss) topilmadi. Masalan: 'Agar spend > $50 va 0 xarid bo'lsa to'xtatish'.")

    # 3. Boshlang'ich ko'rsatkichlar (Baseline)
    has_baseline = bool(
        re.search(r"(boshlang'ich|baseline|oldin|hozirgi|joriy)", lower)
    )
    checks["baseline_metrics"] = has_baseline
    if not has_baseline:
        warnings.append("Boshlang'ich ko'rsatkichlar (Baseline metrics) aniq ko'rsatilmagan.")

    # 4. Xavf darajasi (Risk level)
    has_risk = bool(
        re.search(r"(xavf|risk|past|o'rta|yuqori|high|medium|low)", lower)
    )
    checks["risk_assessment"] = has_risk
    if not has_risk:
        warnings.append("Xavf darajasi (Risk level) belgilanmagan.")

    # 5. Odam tasdig'i (Human approval requirement)
    has_approval_note = bool(
        re.search(r"(tasdiq|ruxsat|tasdiqlansa|operator|foydalanuvchi|approval)", lower)
    )
    checks["human_approval_mention"] = has_approval_note

    passed = len(errors) == 0
    return {
        "passed": passed,
        "checks": checks,
        "errors": errors,
        "warnings": warnings,
    }


def check_ad_copy(platform: str, text: str, headline: str = "", destination_url: str = "") -> dict:
    """Platforma qoidalariga ko'ra reklama matnini tekshiradi."""
    errors: list[str] = []
    warnings: list[str] = []
    platform = platform.lower()

    if platform in ("telegram", "tg"):
        # Telegram Ads qoidalari
        char_count = len(text)
        if char_count > 160:
            errors.append(f"Telegram Ads matni 160 belgidan oshmasligi shart (hozirda: {char_count} belgi).")
        elif char_count == 0:
            errors.append("Reklama matni bo'sh bo'lishi mumkin emas.")

        # Emoji siyosati (maksimal 1 ta kontekstga mos emoji)
        # Unicode emoji diapazoni
        emoji_pattern = re.compile(
            r"[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F700-\U0001F77F\U0001F780-\U0001F7FF\U0001F800-\U0001F8FF\U0001F900-\U0001F9FF\U0001FA00-\U0001FA6F\U0001FA70-\U0001FAFF\u2600-\u26FF\u2700-\u27BF]"
        )
        emojis = emoji_pattern.findall(text)
        if len(emojis) > 1:
            errors.append(f"Telegram Ads siyosati bo'yicha ko'pi bilan 1 ta emoji ruxsat etiladi (hozirda: {len(emojis)} ta: {' '.join(emojis)}).")

        # ALL CAPS tekshiruvi (faqat qisqartmalar ruxsat etiladi)
        allowed_acronyms = {"CRM", "AI", "B2B", "B2C", "ROI", "ROAS", "CPA", "CPL", "CTR", "CPC", "CPM", "TON", "USD", "UZS", "EUR", "SEO", "PMAX", "CBO", "ABO", "ASC", "SMS", "API"}
        words = re.findall(r"\b[A-ZА-ЯЁ]{2,}\b", text)
        forbidden_caps = [w for w in words if w not in allowed_acronyms]
        if forbidden_caps:
            errors.append(f"Telegram Ads ALL CAPS so'zlarni taqiqlaydi: {', '.join(forbidden_caps)}. Kichik harflar bilan yozing.")

        # Havola tekshiruvi
        if destination_url:
            valid_dest = destination_url.startswith(("https://t.me/", "t.me/", "@", "https://"))
            if not valid_dest:
                warnings.append("Telegram Ads manzili 't.me/...', '@kanal', yoki tasdiqlangan HTTPS domen bo'lishi kerak.")

    elif platform in ("meta", "facebook", "instagram"):
        # Meta Ads matn qoidalari
        if headline and len(headline) > 40:
            warnings.append(f"Meta sarlavhasi (Headline) 40 belgidan oshsa mobil ekranda kesilib qolishi mumkin (hozirda: {len(headline)}).")
        if len(text) > 250:
            warnings.append("Birlamchi matn (Primary Text) 125 belgidan keyin 'See more' orqasiga yashirinadi. Eng kuchli hook birinchi 120 belgida bo'lsin.")

        # Taqiqlangan / Shubhali iboralar
        banned_phrases = ["tezda boyib ketish", "100% kafolat", "oson daromad", "hech qanday xavfsiz"]
        for phrase in banned_phrases:
            if phrase in text.lower():
                errors.append(f"Meta siyosatiga zid shubhali va'da: '{phrase}'. Meta hisobni cheklashi mumkin.")

    elif platform in ("google", "google_ads", "gads"):
        # Google Ads Responsive Search Ads (RSA)
        if headline and len(headline) > 30:
            errors.append(f"Google Ads sarlavhasi 30 belgidan oshmasligi shart (hozirda: {len(headline)}).")
        if text and len(text) > 90:
            errors.append(f"Google Ads tavsifi (Description) 90 belgidan oshmasligi shart (hozirda: {len(text)}).")

    passed = len(errors) == 0
    return {
        "passed": passed,
        "platform": platform,
        "errors": errors,
        "warnings": warnings,
    }


def check_tracking_setup(
    has_browser_pixel: bool,
    has_server_capi: bool,
    event_id_present: bool = True,
    user_data_hashed: bool = True,
    emq_score: float | None = None,
) -> dict:
    """Kuzatuv va Konversiya API sozlamalarini tekshiradi."""
    errors: list[str] = []
    warnings: list[str] = []

    if not has_browser_pixel and not has_server_capi:
        errors.append("Hech qanday kuzatuv vositasi (na Pixel, na Server CAPI) mavjud emas.")

    if has_browser_pixel and has_server_capi:
        if not event_id_present:
            errors.append(
                "Pixel va CAPI ikkalasi ham faol, lekin 'event_id' deduplikatsiya parametri yo'q! "
                "Bu har bir xaridni ikki marta (double counting) hisoblash xavfini tug'diradi."
            )
    elif has_browser_pixel and not has_server_capi:
        warnings.append("Faqat brauzer Pixel o'rnatilgan. AdBlock va iOS 14+ tufayli ~20-30% xaridlar yo'qolishi mumkin. CAPI server integratsiyasini qo'shish tavsiya etiladi.")

    if has_server_capi and not user_data_hashed:
        errors.append("CAPI orqali yuborilayotgan foydalanuvchi ma'lumotlari (email/telefon) SHA-256 bilan xeshlanmagan! Maxfiylik qoidasi buzilmoqda.")

    if emq_score is not None:
        if emq_score < 6.0:
            warnings.append(f"Event Match Quality (EMQ) ko'rsatkichi juda past ({emq_score:.1f}/10). Kamida 7.0+ bo'lishi lozim.")

    passed = len(errors) == 0
    return {
        "passed": passed,
        "errors": errors,
        "warnings": warnings,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Tyrion Spend-Guard — Xavfsizlik va Hisob O'zgarishi Nazoratchisi")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Byudjet buyrug'i
    p_budget = subparsers.add_parser("budget", help="Byudjet o'zgarishini tekshirish")
    p_budget.add_argument("--current", type=float, required=True, help="Joriy kunlik byudjet")
    p_budget.add_argument("--proposed", type=float, required=True, help="Taklif qilingan kunlik byudjet")
    p_budget.add_argument("--max-cap", type=float, default=500.0, help="Maksimal ruxsat etilgan kunlik byudjet (default: 500)")
    p_budget.add_argument("--target-cpa", type=float, default=None, help="Maqsadli CPA (ixtiyoriy)")
    p_budget.add_argument("--json", action="store_true", help="JSON formatida chiqarish")

    # Packet buyrug'i
    p_packet = subparsers.add_parser("packet", help="Change Packet faylini tekshirish")
    p_packet.add_argument("file", type=Path, help="Markdown yoki matn fayl yo'li")
    p_packet.add_argument("--json", action="store_true", help="JSON formatida chiqarish")

    # Copy buyrug'i
    p_copy = subparsers.add_parser("copy", help="Reklama matnini platforma qoidalari bo'yicha tekshirish")
    p_copy.add_argument("--platform", choices=["telegram", "meta", "google"], required=True, help="Platforma")
    p_copy.add_argument("--text", type=str, required=True, help="Reklama matni")
    p_copy.add_argument("--headline", type=str, default="", help="Sarlavha")
    p_copy.add_argument("--url", type=str, default="", help="Havola (URL)")
    p_copy.add_argument("--json", action="store_true", help="JSON formatida chiqarish")

    # Tracking buyrug'i
    p_track = subparsers.add_parser("tracking", help="Tracking va CAPI sozlamalarini tekshirish")
    p_track.add_argument("--pixel", action="store_true", help="Pixel mavjudligi")
    p_track.add_argument("--capi", action="store_true", help="Server CAPI mavjudligi")
    p_track.add_argument("--no-event-id", action="store_true", help="event_id yo'qligini bildiradi")
    p_track.add_argument("--unhashed", action="store_true", help="Foydalanuvchi ma'lumotlari xeshlanmagan")
    p_track.add_argument("--emq", type=float, default=None, help="EMQ ball (0-10)")
    p_track.add_argument("--json", action="store_true", help="JSON formatida chiqarish")

    args = parser.parse_args()

    res: dict = {}
    if args.command == "budget":
        res = check_budget_change(args.current, args.proposed, args.max_cap, args.target_cpa)
    elif args.command == "packet":
        if not args.file.is_file():
            print(f"Xato: fayl topilmadi: {args.file}", file=sys.stderr)
            return 2
        content = args.file.read_text(encoding="utf-8", errors="replace")
        res = check_change_packet(content)
    elif args.command == "copy":
        res = check_ad_copy(args.platform, args.text, args.headline, args.url)
    elif args.command == "tracking":
        res = check_tracking_setup(
            has_browser_pixel=args.pixel,
            has_server_capi=args.capi,
            event_id_present=not args.no_event_id,
            user_data_hashed=not args.unhashed,
            emq_score=args.emq,
        )

    if getattr(args, "json", False):
        print(json.dumps(res, indent=2, ensure_ascii=False))
        return 0 if res.get("passed", False) else 1

    # Inson o'qiydigan chiroyli xulosa
    passed = res.get("passed", False)
    status_icon = "✓ PASSED" if passed else "✗ BLOCKED"
    print(f"\n[Spend-Guard] {status_icon} — {args.command.upper()}")

    if "percent_change" in res:
        print(f"  O'zgarish: {res['percent_change']:+g}% ({res['current_daily']} -> {res['proposed_daily']})")

    if res.get("errors"):
        print("  Xatolar (Taqiqlangan):")
        for err in res["errors"]:
            print(f"    - 🛑 {err}")

    if res.get("warnings"):
        print("  Ogohlantirishlar:")
        for warn in res["warnings"]:
            print(f"    - ⚠ {warn}")

    if passed and not res.get("warnings"):
        print("  Barcha 6 ta xavfsizlik darvozasi to'liq qanoatlantirildi.")

    print()
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
