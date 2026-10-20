#!/usr/bin/env python3
"""Tyrion Creative Matrix & Hook Engine — Meta Andromeda 2 3x3 Matritsa, 3 Tilli Hook va Charchoq Radari (0 token).

Buyruqlar:
  python3 tools/creative-matrix.py matrix --niche ecom --product "Klassik kostyum" --price 150 [--json]
  python3 tools/creative-matrix.py hooks --niche edtech --offer "IELTS 7.0 3 oyda" [--json]
  python3 tools/creative-matrix.py fatigue --hook-rate 22.0 --hold-rate 9.5 --ctr-drop-pct 35.0 --frequency 2.9 --ftir 52.0 [--json]
"""

from __future__ import annotations

import argparse
import json
import sys

for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        try:
            _stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:  # pragma: no cover
            pass

ANGLES = [
    ("A1: PAIN & MISTAKE (Og'riq / Xato)", "Mijozning eng katta qo'rquvi yoki 90% odam qiladigan xatosini birinchi 3 soniyada fosh qilish"),
    ("A2: SOCIAL PROOF & CASE (Isbot / Keys)", "Aniq raqamli natija, real mijoz hikoyasi yoki Oldin/Keyin (Before/After) isboti"),
    ("A3: MECHANISM & BNPL OFFER (Noyob Mexanizm / Nasiya)", "Mahsulot nega tez va oson ishlashini jonli ko'rsatish + Uzum/Alif Nasiya oyiga to'lov"),
]

FORMATS = [
    ("F1: Founder / Expert Face-to-Camera (9:16 Reels)", "Ishonch uyg'otuvchi jonli muloqot + dinamik B-roll va subtitr"),
    ("F2: Extreme Demo / UGC Test (9:16 Reels)", "Mahsulotni noodatiy sinovdan o'tkazish yoki mijoz nuqtai nazaridan (POV) ko'rsatish"),
    ("F3: Us vs Them / Offer Breakdown (4:5 Static / Carousel)", "Eski usul vs Sizning yechimingiz + aniq narx/nasiya va kafolat"),
]


def build_matrix(niche: str, product: str, price: float = 100.0) -> dict:
    installment_uzs = int((price * 12800) / 12)
    cells: list[dict] = []
    idx = 1
    for a_code, a_desc in ANGLES:
        for f_code, f_desc in FORMATS:
            cells.append({
                "cell_id": f"C{idx:02d}",
                "angle": a_code,
                "format": f_code,
                "concept": f"{product}: {a_desc} ({f_desc})",
                "cta": "Telegram Bot / Instagram DM ('+ ' yoki kalit so'z)" if price >= 50 else "Darhol buyurtma (eshik oldida to'lov)",
                "bnpl_anchor": f"Oyiga ~{installment_uzs:,} so'mdan (12 oy muddatli to'lov)" if price >= 50 else "Tezkor yetkazib berish",
            })
            idx += 1
    return {
        "niche": niche,
        "product": product,
        "price_usd": price,
        "andromeda_rule": "Har bir Ad Setga kamida 3 xil Angle x 2 xil Format joylang (bir xil videoning 3 xil kesimi EMAS!)",
        "matrix_3x3": cells,
    }


def generate_hooks(niche: str, offer: str) -> dict:
    return {
        "niche": niche,
        "offer": offer,
        "hooks_by_language": {
            "uz_latin": [
                f"[Qiziqish/Bo'shliq] {offer} haqida 90% odam bilmaydigan 1 ta haqiqat...",
                f"[Xato/Og'riq] Agar hali ham eski usulda harakat qilayotgan bo'lsangiz, pulingizni havoga sovuryapsiz: {offer}",
                f"[Aniq Raqam/Isbot] Qanday qilib 14 kun ichida ortiqcha xarajatsiz natijaga chiqish mumkin? ({offer})",
                f"[Filtr-Hook] Diqqat: bu video faqat haqiqiy sifat va kafolat izlayotganlar uchun — {offer}",
            ],
            "uz_cyrillic": [
                f"[Қизиқиш] {offer} ҳақида 90% одам билмайдиган 1 та сир...",
                f"[Хато/Оғриқ] Пулингизни бефойда тажрибаларга сарфлашни тўхтатинг: {offer}",
                f"[Исбот] Натижа бўлмаса — пулингизни қайтарамиз: {offer}",
            ],
            "ru": [
                f"[Проблема/Ошибка] 3 главные ошибки при выборе, из-за которых вы теряете время и бюджет ({offer})",
                f"[Цифры/Кейс] Как получить результат за 14 дней с гарантией по договору: {offer}",
                f"[Фильтр-Хук] Только для тех, кто ценит твердый результат и прозрачные условия: {offer}",
            ],
        },
    }


def analyze_fatigue(
    hook_rate: float,
    hold_rate: float,
    ctr_drop_pct: float,
    frequency: float,
    ftir: float,
) -> dict:
    actions: list[str] = []
    status = "HEALTHY_CREATIVE"

    if hook_rate < 25.0:
        status = "WEAK_3S_HOOK"
        actions.append(f"Hook Rate past ({hook_rate:.1f}% < 25%): Videoning qolgan qismiga tegmang, faqat birinchi 3 soniyasiga 3 xil yangi vizual va tekst Hook ulang.")
    if hold_rate < 12.0:
        if status == "HEALTHY_CREATIVE":
            status = "WEAK_BODY_RETENTION"
        actions.append(f"Hold Rate past ({hold_rate:.1f}% < 12%): 4–10 soniyalar orasidagi suv (kirish salomlashish)ni kesib tashlang, har 2.5 soniyada kadr almashsin.")
    if ctr_drop_pct >= 25.0 or frequency >= 2.8 or ftir < 55.0:
        status = "CREATIVE_FATIGUED"
        actions.append(
            f"Kreativ charchagan (CTR tushishi={ctr_drop_pct:.1f}%, Frequency={frequency:.2f}, FTIR={ftir:.1f}%): "
            "Yangi psixologik burchak (Angle A2/A3) va yangi spiker/lokatsiya bilan almashtiring."
        )
    if not actions:
        actions.append("Kreativ ko'rsatkichlari a'lo (Hook >=25%, Hold >=12%, FTIR >=55%) — 'More/Better' qoidasi bo'yicha gorizontal scaling qiling.")

    return {
        "status": status,
        "metrics": {
            "hook_rate_pct": hook_rate,
            "hold_rate_pct": hold_rate,
            "ctr_drop_pct": ctr_drop_pct,
            "frequency": frequency,
            "ftir_pct": ftir,
        },
        "prescribed_actions": actions,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="creative-matrix.py", description="Andromeda 2 Creative Matrix & Hook Engine")
    sub = parser.add_subparsers(dest="command", required=True)

    p_mat = sub.add_parser("matrix", help="3x3 Angle x Format kreativ sinov matritsasi")
    p_mat.add_argument("--niche", default="ecom")
    p_mat.add_argument("--product", required=True)
    p_mat.add_argument("--price", type=float, default=100.0)
    p_mat.add_argument("--json", action="store_true")

    p_hk = sub.add_parser("hooks", help="3 tilli (UZ Lotin / Kirill / RU) 3 soniyalik Hook generatori")
    p_hk.add_argument("--niche", default="ecom")
    p_hk.add_argument("--offer", required=True)
    p_hk.add_argument("--json", action="store_true")

    p_fat = sub.add_parser("fatigue", help="Hook Rate, Hold Rate va FTIR bo'yicha kreativ charchoq diagnostikasi")
    p_fat.add_argument("--hook-rate", type=float, required=True)
    p_fat.add_argument("--hold-rate", type=float, required=True)
    p_fat.add_argument("--ctr-drop-pct", type=float, default=0.0)
    p_fat.add_argument("--frequency", type=float, default=1.5)
    p_fat.add_argument("--ftir", type=float, default=70.0)
    p_fat.add_argument("--json", action="store_true")

    args = parser.parse_args(argv)
    if args.command == "matrix":
        res = build_matrix(args.niche, args.product, args.price)
    elif args.command == "hooks":
        res = generate_hooks(args.niche, args.offer)
    elif args.command == "fatigue":
        res = analyze_fatigue(args.hook_rate, args.hold_rate, args.ctr_drop_pct, args.frequency, args.ftir)
    else:
        return 2

    if getattr(args, "json", False):
        print(json.dumps(res, ensure_ascii=False, indent=2))
        return 0

    print("=" * 66)
    print(f"  🎨 TYRION CREATIVE STUDIO — {args.command.upper()}")
    print("=" * 66)
    print(json.dumps(res, ensure_ascii=False, indent=2))
    print("=" * 66)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
