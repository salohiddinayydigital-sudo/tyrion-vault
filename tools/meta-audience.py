#!/usr/bin/env python3
"""Tyrion Meta Ads Audience Engine — Andromeda 2 va O'zbekiston bozori uchun auditoriya arxitektori (0 token).

Muammo: Meta Ads'da (Andromeda 2 davrida) noto'g'ri auditoriya tanlash, ad setlarning ustma-ust
tushishi (Auction Overlap > 20%), sovuq kampaniyadan xaridorlarni istisno qilmaslik (Exclusion yo'qligi),
kichik auditoriyaga katta byudjet berib 3 kunda kuydirish (Saturation) va xom lidlardan Lookalike (LAL)
yasash byudjetning 30-50% isrof bo'lishiga olib keladi.

Yechim: 4 ta deterministik buyruq orqali Meta Ads auditoriya arxitekturasini hisoblash va loyihalash:
  1. architect  : Nisha, kunlik byudjet, geo va mavjud 1P data asosida 4-qatlamli auditoriya rejasi + Exclusion matritsasi
  2. interests  : 8 ta asosiy nisha bo'yicha tasdiqlangan Interest Cluster'lar, to'lov qobiliyati (Solventnost) filtrlari va Graph API so'rovlari
  3. overlap    : Ikki ad set o'rtasidagi ustma-ust tushish (Auction Overlap %) va konsolidatsiya qarori
  4. saturation : Auditoriya hajmi va byudjetga ko'ra Frequency o'sishi, charchash kuni (Fatigue Day) va maksimal xavfsiz byudjet

Buyruqlar:
  py -3 tools/meta-audience.py architect --niche ecom --daily-budget 150 --geo uzbekistan --has-pixel --has-crm
  py -3 tools/meta-audience.py interests --niche edu
  py -3 tools/meta-audience.py overlap --size-a 180000 --size-b 120000 --shared 45000
  py -3 tools/meta-audience.py saturation --audience-size 250000 --daily-budget 80 --cpm 3.2
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.parse
import urllib.request
from pathlib import Path

for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        try:
            _stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:  # pragma: no cover
            pass

# 8 ta asosiy nisha bo'yicha Meta Ads Interest Cluster va Behavior taksonomiyasi
NICHE_TAXONOMY: dict[str, dict] = {
    "ecom": {
        "title": "E-Commerce, Onlayn Do'kon va Chakana Savdo",
        "core_interests": [
            "Online shopping", "Shopping and fashion", "Boutique", "Discount store",
            "Consumer electronics", "Home appliances", "Department store"
        ],
        "behaviors": [
            "Engaged Shoppers (Xarid tugmasini bosgan faol xaridorlar)",
            "Mobile Device User: iPhone 14/15/16 Pro & High-end Android",
        ],
        "creative_angles": [
            "TOF Problem/Solution: Mahsulot muammoni 3 soniyada qanday hal qiladi (UGC unboxing)",
            "TOF Social Proof: Real mijoz sharhlari va yetkazib berish jarayoni",
            "BOF Objection Crusher: Nasiya (Uzum/Payme bo'lib to'lash), kafolat va bepul yetkazish"
        ],
        "recommended_cpa_ratio": 0.08,
    },
    "edu": {
        "title": "Ta'lim, Kurslar, Xususiy Maktab va O'quv Markazlari",
        "core_interests": [
            "Higher education", "Online learning", "Language school", "IELTS",
            "Professional certification", "Career development", "Parenting (K-12 uchun)"
        ],
        "behaviors": [
            "Parents (All) / Parents with teenagers (13-17) / Parents with early school-age children",
            "Frequent Travelers / International education seekers"
        ],
        "creative_angles": [
            "TOF Transformation: O'quvchining oldingi va keyingi natijasi (IELTS 7.5+ / ishga kirish keysi)",
            "TOF Authority/Teacher: Ustoz metodikasi va 1-bepul sinov darsi / diagnostika",
            "BOF Urgency/Guarantee: Guruh to'lishiga 4 ta joy qoldi + shartnoma/natija kafolati"
        ],
        "recommended_cpa_ratio": 0.06,
    },
    "real-estate": {
        "title": "Ko'chmas Mulk (Novostroyka, Tijorat Binolari, Xonadonlar)",
        "core_interests": [
            "Real estate", "Property investment", "Apartment", "Mortgage loan",
            "Luxury real estate", "Interior design", "Architecture"
        ],
        "behaviors": [
            "Frequent International Travelers (yuqori daromad signali)",
            "Business Decision Makers / Small Business Owners",
            "iPhone Pro / Flagship device owners"
        ],
        "creative_angles": [
            "TOF Financial Plan: Boshlang'ich to'lov va 0% muddatli to'lov (rassrochka) hisob-kitobi",
            "TOF Infrastructure/Location: Joylashuv, metro/maktab yaqinligi va qurilish jarayoni (jonli video)",
            "BOF Investor ROI: Kvadrat metr narxi o'sishi va ijara daromadliligi jadvali"
        ],
        "recommended_cpa_ratio": 0.12,
    },
    "medical": {
        "title": "Tibbiyot, Stomatologiya, Estetika va Sog'lomlashtirish Klinikalari",
        "core_interests": [
            "Healthcare", "Dentistry", "Cosmetic dentistry", "Physical therapy",
            "Wellness", "Medical specialty", "Skin care"
        ],
        "behaviors": [
            "Geo-radius targeting (klinika atrofida +5..15 km yoki shahar bo'yicha)",
            "Age-segmented cohorts (30-55 yosh to'lovga qodir qatlam)"
        ],
        "creative_angles": [
            "TOF Doctor Authority: Shifokor tushuntirishi — og'riqsiz va xavfsiz davolash mexanizmi (Policy-safe!)",
            "TOF Patient Story: Mijozning intervyu-fikri (Meta taqiqlagan 'before/after' yaqin plan rasmlarsiz!)",
            "BOF Free Consultation/Diagnostics: Bepul birlamchi ko'rik yoki 3D diagnostika paketi"
        ],
        "recommended_cpa_ratio": 0.07,
    },
    "b2b": {
        "title": "B2B Xizmatlar, SaaS, Ulgurji Savdo va Agentliklar",
        "core_interests": [
            "Small and medium-sized enterprises", "Entrepreneurship", "Business management",
            "Digital marketing", "Customer relationship management (CRM)", "Enterprise software"
        ],
        "behaviors": [
            "Facebook Page Admins (Business Page Admins)",
            "Small Business Owners",
            "Instagram Business Profile Admins"
        ],
        "creative_angles": [
            "TOF Cost of Inaction: Biznesda yo'qotilayotgan pul/vaqt auditi (aniq raqamlar bilan)",
            "TOF Case Study: 'Qanday qilib X kompaniyasi 30 kunda sotuvni +42% oshirdi' tahlili",
            "BOF Risk-Free Audit/Demo: 15 daqiqalik bepul tizim auditi yoki tayyor shablon lead-magnet"
        ],
        "recommended_cpa_ratio": 0.10,
    },
    "beauty": {
        "title": "Go'zallik, Parfyumeriya, Kosmetika va Moda Brendlari",
        "core_interests": [
            "Cosmetics", "Fragrances", "Beauty salon", "Skin care",
            "Luxury goods", "Women's clothing", "Men's fashion"
        ],
        "behaviors": [
            "Engaged Shoppers",
            "Instagram active engagers"
        ],
        "creative_angles": [
            "TOF Sensory/Emotion: Mahsulot teksturasi, qadoqlanishi va komplement olish hissiyoti",
            "TOF Bundle/Tester Offer: Sinov to'plami (Discovery set) yoki '2+1' maxsus taklifi",
            "BOF Fast Delivery: Toshkent bo'ylab 2 soatda yetkazish + original mahsulot kafolati"
        ],
        "recommended_cpa_ratio": 0.06,
    },
    "auto": {
        "title": "Avto-servis, Deteyling, Ehtiyot Qismlar va Avtosalonlar",
        "core_interests": [
            "Automobile", "Car dealership", "Auto detailing", "Vehicle insurance",
            "SUV", "Electric vehicle", "Automotive repair shop"
        ],
        "behaviors": [
            "Men/Women 24-55 in urban centers",
            "Engaged Shoppers"
        ],
        "creative_angles": [
            "TOF Process ASMR/Visual: Avtomobilga xizmat ko'rsatish jarayoni va sifat kafolati",
            "TOF Price Transparency: Aniq paket narxlari va yashirin to'lovlarsiz smeta",
            "BOF Lead Magnet: Bepul diagnostika yoki mavsumiy chek-list"
        ],
        "recommended_cpa_ratio": 0.07,
    },
    "local": {
        "title": "Lokal Xizmatlar, Fitness, Restoran, Mehmonxona va Dam Olish Zonalari",
        "core_interests": [
            "Physical fitness", "Gym", "Restaurants", "Tourism",
            "Resort", "Hotel", "Family entertainment"
        ],
        "behaviors": [
            "People living in or recently in this location (Geo Pin +3..10 km)",
            "Frequent Travelers / Weekend commuters"
        ],
        "creative_angles": [
            "TOF Atmosphere Tour: 15 soniyalik POV video-sayohat va muhit namoyishi",
            "TOF First-Visit Offer: Birinchi tashrif yoki oilaviy paket uchun maxsus bonus",
            "BOF Instant Booking: Telegram bot yoki Direct orqali 1 daqiqada joy band qilish"
        ],
        "recommended_cpa_ratio": 0.05,
    },
}

SOLVENTNOST_FILTERS = [
    "Engaged Shoppers (So'nggi 7 kunda 'Shop Now' bosganlar)",
    "Frequent International Travelers (Chet elga tez-tez chiquvchi to'lov qobiliyati yuqori qatlam)",
    "Mobile Device: iPhone 14 / 15 / 16 Pro & Pro Max (Yuqori chekli mahsulotlar uchun)",
    "Facebook Page Admins & Small Business Owners (B2B va yuqori chekli xizmatlar uchun)",
    "Geo-Tiering: Toshkent shahri alohida kampaniya/ad setda, Viloyatlar alohida ad setda (CPM va to'lov qobiliyati farqi sababli)",
]


def build_architecture(
    niche: str,
    daily_budget: float,
    geo: str = "uzbekistan",
    has_pixel: bool = True,
    has_crm: bool = True,
    ig_followers: int = 5000,
    target_cpa: float | None = None,
) -> dict:
    """Andromeda 2 + O'zbekiston bozori uchun 4-qatlamli Meta Ads auditoriya arxitekturasi."""
    if daily_budget <= 0:
        raise ValueError("Kunlik byudjet 0 dan katta bo'lishi shart.")

    tax = NICHE_TAXONOMY.get(niche, NICHE_TAXONOMY["ecom"])
    est_cpa = target_cpa if (target_cpa and target_cpa > 0) else max(3.0, round(daily_budget * tax["recommended_cpa_ratio"], 2))
    min_daily_per_adset = round((est_cpa * 50.0) / 7.0, 2)
    max_adsets = max(1, min(6, int(daily_budget // max(min_daily_per_adset, 10.0))))

    # Byudjet taqsimoti: Cold Prospecting vs Warm/Hot Retargeting
    if daily_budget < 30:
        cold_pct, warm_pct, hot_pct = 85, 15, 0
        structure_mode = "Konsolidatsiyalangan ABO (1-2 Ad Set: Broad + 1 Interest Stack)"
    elif daily_budget < 150:
        cold_pct, warm_pct, hot_pct = 75, 15, 10
        structure_mode = "Hybrid ABO Sandbox + Warm IG/Web Retargeting (3-4 Ad Set)"
    else:
        cold_pct, warm_pct, hot_pct = 70, 20, 10
        structure_mode = "Andromeda 1-5-5 CBO/ASC + Full-Funnel 1P Retargeting & Value LAL"

    cold_budget = round(daily_budget * (cold_pct / 100.0), 2)
    warm_budget = round(daily_budget * (warm_pct / 100.0), 2)
    hot_budget = round(daily_budget * (hot_pct / 100.0), 2)

    # 4 Qatlamli Auditoriya Dizayni
    layers = [
        {
            "layer": "1-Qatlam: Broad + Creative Signal Steering (TOF)",
            "budget_share_usd": round(cold_budget * 0.55, 2),
            "targeting": f"Geo: {geo.upper()} | Yosh: 22-54 | Ochiq (Broad) — kreativ burchakning o'zi algoritm uchun filtr vazifasini bajaradi.",
            "language_rule": "O'zbek (Lotin/Kirill) va Rus tilidagi kreativlarni bitta ad setga aralashtirmang — til bo'yicha alohida ad set oching.",
            "exclusions": ["Purchase_180d", "CRM_Active_Clients", "LeadForm_Submitted_90d"],
        },
        {
            "layer": "2-Qatlam: Advantage+ Interest Stack & Solventnost (TOF)",
            "budget_share_usd": round(cold_budget * 0.45, 2),
            "targeting": f"Interest Cluster: {', '.join(tax['core_interests'][:5])} + Behavior: {tax['behaviors'][0]}",
            "advantage_plus_mode": "Yuqori chekli/B2B nishada Hard Interest (Advantage+ Audience OFF), ommaviy B2C da Advantage+ Audience ON (Suggestion sifatida).",
            "exclusions": ["Purchase_180d", "CRM_Active_Clients", "LeadForm_Submitted_90d"],
        },
        {
            "layer": "3-Qatlam: First-Party (1P) Warm Retargeting (MOF — IG/Video/Telegram/Web)",
            "budget_share_usd": warm_budget,
            "custom_audiences": [
                "IG_Engaged_30d (Instagram profil, post, saqlash va Direct yozishmalar — O'zbekistonda eng kuchli issiq baza)",
                "Video_Viewers_50pct_14d (Reels/Video reklamani kamida 50% ko'rgan qiziquvchilar)",
                "LeadForm_Opened_Not_Submitted_30d (Lead formani ochib to'ldirmaganlar)",
            ] + (["Web_Visitors_30d & ViewContent_14d (Pixel + CAPI)"] if has_pixel else ["⚠ Pixel yo'q: IG Direct va Lead Form engagement bazasiga tayaning"]),
            "exclusions": ["Purchase_180d", "LeadForm_Submitted_30d", "CRM_Converted_Buyers"],
        },
        {
            "layer": "4-Qatlam: Value Lookalike (LAL) & Hot BOF Closing",
            "budget_share_usd": hot_budget,
            "lal_strategy": (
                "Value-Based LAL 1% va 1-2% — FAQAT CRM/CAPI dagi to'lov qilgan mijozlar (kamida 100-500 ta sifatli lid/xaridor) asosida. Xom, sifatsiz lidlardan LAL qurmang!"
                if has_crm else
                "⚠ CRM bazasi ulanmagan: IG_DM_Messagers_90d yoki Purchase_180d (≥100 hodisa) yig'ilgach 1% LAL yoqing."
            ),
            "bof_closing": "AddToCart_14d + InitiateCheckout_7d + CRM_Unclosed_Leads_14d (E'tirozlarni yopuvchi BOF kreativlar bilan)",
            "exclusions": ["Purchase_30d (So'nggi 30 kunda xarid qilganlar)"],
        },
    ]

    exclusion_matrix = [
        {"stage": "Cold Prospecting (Broad / Interest / LAL)", "include": "Yangi auditoriya", "must_exclude": "Purchase_180d, CRM_Active_Clients, LeadForm_Submitted_90d"},
        {"stage": "Warm Engagement (MOF Retargeting)", "include": "IG_Engaged_30d, Video_50pct_14d, Web_30d", "must_exclude": "Purchase_180d, InitiateCheckout_7d, LeadForm_Submitted_30d"},
        {"stage": "Hot Conversion (BOF Retargeting)", "include": "AddToCart_14d, Checkout_7d, IG_DM_14d, CRM_Warm_Leads", "must_exclude": "Purchase_30d"},
        {"stage": "Advantage+ Shopping (ASC)", "include": "Avtomatik (20-50 xil kreativ)", "must_exclude": "Existing Customer Budget Cap <= 25-30% qilib qulflansin"},
    ]

    return {
        "niche": niche,
        "niche_title": tax["title"],
        "geo": geo,
        "daily_budget_usd": round(daily_budget, 2),
        "estimated_target_cpa_usd": est_cpa,
        "learning_phase_guardrail": {
            "min_daily_budget_per_adset_usd": min_daily_per_adset,
            "recommended_active_adsets": max_adsets,
            "rule": "Har bir ad set haftasiga >=50 konversiya olishi shart; aks holda ad setlarni birlashtiring.",
        },
        "recommended_structure": structure_mode,
        "budget_split_usd": {
            f"cold_prospecting_{cold_pct}pct": cold_budget,
            f"warm_retargeting_{warm_pct}pct": warm_budget,
            f"hot_bof_and_lal_{hot_pct}pct": hot_budget,
        },
        "audience_layers": layers,
        "exclusion_matrix": exclusion_matrix,
        "uzbekistan_solventnost_filters": SOLVENTNOST_FILTERS,
        "recommended_creative_angles": tax["creative_angles"],
    }


def calc_overlap(size_a: int, size_b: int, shared: int) -> dict:
    """Ikki ad set auditoriyasi o'rtasidagi ustma-ust tushishni (Auction Overlap) hisoblaydi."""
    if size_a <= 0 or size_b <= 0 or shared < 0:
        raise ValueError("Auditoriya hajmlari musbat bo'lishi shart.")
    if shared > min(size_a, size_b):
        raise ValueError("Umumiy (shared) auditoriya kichik to'plamdan katta bo'lishi mumkin emas.")

    smaller = min(size_a, size_b)
    larger = max(size_a, size_b)
    union = size_a + size_b - shared

    overlap_of_smaller_pct = round((shared / smaller) * 100.0, 2)
    overlap_of_larger_pct = round((shared / larger) * 100.0, 2)
    jaccard_pct = round((shared / union) * 100.0, 2) if union > 0 else 0.0

    if overlap_of_smaller_pct > 25.0:
        status = "CRITICAL_COLLISION"
        action = (
            f"Kichik ad setning {overlap_of_smaller_pct}% qismi ikkinchi ad set bilan ustma-ust tushmoqda (>25%). "
            "Ikki ad setni BITTA ad setga birlashtiring (konsolidatsiya) yoki kichik auditoriyani kattasidan Exclude qiling!"
        )
    elif overlap_of_smaller_pct > 15.0:
        status = "MODERATE_OVERLAP"
        action = (
            f"Ustma-ust tushish {overlap_of_smaller_pct}% (15-25% oralig'ida). "
            "CPM o'sishini kuzating; o'zaro Exclude qoidasini kiriting."
        )
    else:
        status = "HEALTHY_ISOLATION"
        action = f"Ustma-ust tushish xavfsiz darajada ({overlap_of_smaller_pct}% <= 15%). Ad setlar alohida ishlashi mumkin."

    return {
        "audience_a": size_a,
        "audience_b": size_b,
        "shared_audience": shared,
        "overlap_of_smaller_pct": overlap_of_smaller_pct,
        "overlap_of_larger_pct": overlap_of_larger_pct,
        "jaccard_index_pct": jaccard_pct,
        "status": status,
        "recommendation": action,
    }


def calc_saturation(
    audience_size: int,
    daily_budget: float,
    cpm: float = 3.2,
    days: int = 14,
    active_reach_ratio: float = 0.60,
) -> dict:
    """Auditoriya sig'imi, Frequency o'sishi va kreativ/auditoriya charchash kunini hisoblaydi."""
    if audience_size <= 0 or daily_budget <= 0 or cpm <= 0 or days <= 0:
        raise ValueError("Barcha parametrlar 0 dan katta bo'lishi shart.")

    reachable_pool = max(1, int(audience_size * active_reach_ratio))
    daily_impressions = (daily_budget / cpm) * 1000.0
    total_impressions = daily_impressions * days

    projected_frequency = round(total_impressions / reachable_pool, 2)
    daily_frequency_rate = daily_impressions / reachable_pool

    # Frequency 2.8 ga yetadigan kun (FTIR < 60% charchash chegarasi)
    fatigue_day = round(2.8 / daily_frequency_rate, 1) if daily_frequency_rate > 0 else 999.0
    # 14 kunda Frequency <= 2.5 bo'lishi uchun maksimal xavfsiz kunlik byudjet
    max_safe_daily_budget = round(((reachable_pool * 2.5) / 14.0 / 1000.0) * cpm, 2)

    if projected_frequency > 3.5:
        verdict = "OVERSATURATED_HIGH_RISK"
        advice = (
            f"{days} kunda o'rtacha Frequency {projected_frequency}x ga chiqadi (>{fatigue_day}-kuni charchaydi). "
            f"Bu auditoriya uchun kunlik byudjetni <= ${max_safe_daily_budget} ga tushiring yoki Broad/LAL orqali auditoriyani kengaytiring."
        )
    elif projected_frequency > 2.4:
        verdict = "WATCH_FATIGUE"
        advice = (
            f"{days} kunda Frequency {projected_frequency}x ga yetadi (~{fatigue_day}-kuni yangi kreativ burchak talab qilinadi). "
            "Har 7-10 kunda kamida 3 ta yangi hook kiriting."
        )
    else:
        verdict = "HEALTHY_CAPACITY"
        advice = f"Auditoriya sig'imi yetarli ({days} kunda Frequency {projected_frequency}x). Masshtablash xavfsiz."

    return {
        "total_audience_size": audience_size,
        "estimated_reachable_pool": reachable_pool,
        "daily_budget_usd": round(daily_budget, 2),
        "cpm_usd": round(cpm, 2),
        "daily_impressions": int(daily_impressions),
        "period_days": days,
        "projected_frequency": projected_frequency,
        "estimated_fatigue_day": fatigue_day,
        "max_safe_daily_budget_14d_usd": max_safe_daily_budget,
        "status": verdict,
        "recommendation": advice,
    }


def query_live_graph_api(query: str, limit: int = 15) -> list[dict]:
    """Agar META_ACCESS_TOKEN muhitda mavjud bo'lsa, Meta Graph API dan Authorization Bearer header
    va eksponensial backoff (HTTP 429/5xx) orqali read-only interest qidiradi. Token URL ichiga qo'yilmaydi.
    """
    import tyrion_core as tcore
    token = os.environ.get("META_ACCESS_TOKEN", "").strip()
    if not token or token == "your_meta_access_token_here":
        return []
    version = os.environ.get("META_GRAPH_API_VERSION", "v22.0").strip()
    base = os.environ.get("META_GRAPH_API_BASE_URL", "https://graph.facebook.com").strip().rstrip("/")
    safe_limit = tcore.safe_int(limit, default=15, min_val=1, max_val=100, field_name="limit")
    params = urllib.parse.urlencode({
        "type": "adinterest",
        "q": str(query or "").strip()[:120],
        "limit": str(safe_limit),
        "locale": "en_US",
    })
    url = f"{base}/{version}/search?{params}"
    headers = {"Authorization": f"Bearer {token}"}
    payload = tcore.http_get_json_with_backoff(url, headers=headers, timeout=8.0, max_retries=3)
    if "error" in payload:
        return [{"error": f"Meta Graph API xatosi: {tcore.redact_secrets(str(payload['error']))}"}]
    data = payload.get("data", [])
    return data if isinstance(data, list) else []
    version = os.environ.get("META_GRAPH_API_VERSION", "v22.0").strip()
    base = os.environ.get("META_GRAPH_API_BASE_URL", "https://graph.facebook.com").strip().rstrip("/")
    params = urllib.parse.urlencode({
        "type": "adinterest",
        "q": query,
        "limit": 15,
        "locale": "en_US",
        "access_token": token,
    })
    url = f"{base}/{version}/search?{params}"
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            payload = json.loads(resp.read().decode("utf-8", errors="replace"))
            return payload.get("data", [])
    except Exception:
        return []


def get_interests(niche: str, query: str = "", live: bool = False) -> dict:
    tax = NICHE_TAXONOMY.get(niche, NICHE_TAXONOMY["ecom"])
    q_term = query or tax["core_interests"][0]
    api_results = query_live_graph_api(q_term) if live else []
    return {
        "niche": niche,
        "title": tax["title"],
        "core_interest_clusters": tax["core_interests"],
        "high_intent_behaviors": tax["behaviors"],
        "uzbekistan_solventnost_filters": SOLVENTNOST_FILTERS,
        "creative_angles": tax["creative_angles"],
        "graph_api_readonly_endpoint": f"GET https://graph.facebook.com/v22.0/search?type=adinterest&q={urllib.parse.quote(q_term)}&limit=20",
        "live_api_results": api_results,
    }




def calc_retargeting(
    aov: float = 100.0,
    daily_visitors: int = 300,
    ig_engagers_30d: int = 5000,
    video_viewers_14d: int = 8000,
    has_telegram_bot: bool = True,
) -> dict:
    """Dinamik Retargeting Oynalari (3d/7d/14d/30d/180d) va byudjet sig'imi hisoblagichi."""
    sales_cycle = "LONG_HIGH_TICKET" if aov >= 300 else ("MEDIUM_CONSIDERATION" if aov >= 50 else "FAST_IMPULSE")
    hot_pool = max(int(daily_visitors * 7 * 0.25), 100)
    warm_pool = max(int(video_viewers_14d * 0.6 + ig_engagers_30d * 0.4), 500)
    social_pool = max(ig_engagers_30d, 1000)
    total_retargetable = hot_pool + warm_pool + social_pool
    # Har 1000 kishiga kuniga ~$0.80-$1.20 retargeting byudjeti (Frequency 3.5-5.0 oralig'ida ushlash uchun)
    rec_daily_budget = round(max(2.0, min(150.0, (total_retargetable / 1000.0) * 0.95)), 2)

    windows = [
        {
            "window": "W1: HOT INTENT (0–3 kun / 0–7 kun)",
            "sources": ["AddToCart_7d", "InitiateCheckout_7d", "LeadForm_Opened_Not_Submitted_7d"]
                       + (["Telegram_Bot_Started_No_Contact_7d"] if has_telegram_bot else []),
            "exclusions": ["Purchase_180d", "Qualified_Lead_30d"],
            "estimated_pool": hot_pool,
            "creative_angle": "E'tirozni yopish + Tezkor bonus / Bepul yetkazib berish / Nasiya eslatmasi",
            "target_frequency_7d": "4.0 – 6.0",
        },
        {
            "window": "W2: WARM VIDEO & DM (7–14 kun)",
            "sources": ["Video_Watched_50pct_14d", "IG_DM_Messaged_14d", "Website_Visitors_Top25_Time_14d"],
            "exclusions": ["Purchase_180d", "Qualified_Lead_30d", "W1_Hot_Intent_7d"],
            "estimated_pool": warm_pool,
            "creative_angle": "Mijoz sharhlari (UGC / Case Study) + Jarayon ichidan ko'rsatuv (Behind the scenes)",
            "target_frequency_7d": "2.8 – 4.2",
        },
        {
            "window": "W3: SOCIAL ENGAGERS (15–30 kun)",
            "sources": ["IG_Engagers_30d", "FB_Page_Engagers_30d", "Ad_Savers_Shares_30d"],
            "exclusions": ["Purchase_180d", "Qualified_Lead_30d", "W1_Hot_Intent_7d", "W2_Warm_14d"],
            "estimated_pool": social_pool,
            "creative_angle": "Yangi Offer / Lead Magnet (PDF/Quiz/Diagnostika) orqali voronkaga tortish",
            "target_frequency_7d": "2.0 – 3.0",
        },
        {
            "window": "W4: WINBACK & LTV UPSELL (31–180 kun)",
            "sources": ["Purchase_180d", "CRM_Past_Clients_List"],
            "exclusions": ["Purchase_14d"],
            "estimated_pool": max(int(daily_visitors * 1.5), 200),
            "creative_angle": "VIP mijozlar uchun yangi kolleksiya / Qayta xarid bonusi / Referal taklif",
            "target_frequency_7d": "1.5 – 2.5",
        },
    ]
    return {
        "aov_usd": aov,
        "sales_cycle_type": sales_cycle,
        "total_retargetable_pool": total_retargetable,
        "recommended_retargeting_daily_budget_usd": rec_daily_budget,
        "retargeting_windows": windows,
    }


def calc_lookalike(
    seed_size: int,
    seed_type: str = "purchase_ltv",
    country: str = "UZ",
) -> dict:
    """Lookalike (LAL) manba sifati (Seed Quality Score) va 1%–5% pog'onali hajm hisoblagichi."""
    country_reach = {"UZ": 9_200_000, "KZ": 13_500_000, "GLOBAL": 100_000_000}
    base_pop = country_reach.get(country.upper(), 9_200_000)

    type_weights = {
        "purchase_ltv": (95, "CRM LTV / Yuqori chekli xaridorlar (Value-Based) — ENG KUCHLI SIGNAL"),
        "purchase_all": (85, "Barcha xaridorlar (Pixel + CAPI Purchase)"),
        "qualified_leads": (78, "CRM da tasdiqlangan sifatli lidlar (Qualified Leads)"),
        "raw_leads": (58, "Barcha forma/bot lidlari (ichida sifatsiz lidlar bo'lishi mumkin)"),
        "ig_engagers": (40, "Instagram/Video faollari (xarid niyati past — Broad ko'pincha yaxshiroq)"),
    }
    base_score, type_desc = type_weights.get(seed_type, (65, "Maxsus ro'yxat"))

    if seed_size >= 1000:
        size_bonus = 5
        size_verdict = "IDEAL_SEED_SIZE (>=1,000)"
    elif seed_size >= 300:
        size_bonus = -5
        size_verdict = "ACCEPTABLE_SEED_SIZE (300–999)"
    elif seed_size >= 100:
        size_bonus = -25
        size_verdict = "WEAK_SEED_SIZE (100–299 — algoritm signali zaif)"
    else:
        size_bonus = -50
        size_verdict = "INSUFFICIENT_SEED (<100 — Meta LAL yaratish tavsiya etilmaydi!)"

    quality_score = max(5, min(100, base_score + size_bonus))
    one_pct = int(base_pop * 0.01)

    tiers = [
        {"tier": "LAL 0%–1% (Core Twin)", "estimated_reach": one_pct, "min_daily_budget_usd": 20.0, "priority": "1-o'rinda sinov (Eng yaqin o'xshashlik)"},
        {"tier": "LAL 1%–2% (Expansion)", "estimated_reach": one_pct, "min_daily_budget_usd": 25.0, "priority": "1% isbotlangach scaling uchun"},
        {"tier": "LAL 2%–3% (Mid Scale)", "estimated_reach": one_pct, "min_daily_budget_usd": 30.0, "priority": "Katta byudjetda ($100+/kun) qo'shiladi"},
        {"tier": "LAL 3%–5% (Broad-Like)", "estimated_reach": one_pct * 2, "min_daily_budget_usd": 45.0, "priority": "Faqat yuqori hajmli B2C uchun"},
    ]
    return {
        "country": country.upper(),
        "seed_size": seed_size,
        "seed_type": seed_type,
        "seed_description": type_desc,
        "seed_size_verdict": size_verdict,
        "seed_quality_score_100": quality_score,
        "recommendation": (
            "1% Value-Based LAL ni alohida Ad Setda L1 Broad bilan A/B sinovga qo'ying."
            if quality_score >= 70
            else "Seed hajmi yoki sifati past — LAL o'rniga L1 Broad + L2 Solventnost Stack ishlating va avval 300+ sifatli konversiya yig'ing."
        ),
        "lal_tiers": tiers,
    }


def diagnose_metrics(
    cpm: float,
    ctr: float,
    cpc: float,
    lp_cvr: float,
    lead_to_sale: float = 10.0,
    frequency: float = 1.6,
    ftir: float = 72.0,
) -> dict:
    """Meta Ads metrikalar zanjiri bo'yicha darhol tor joyni (bottleneck) va yechimni topadi."""
    bottlenecks: list[dict] = []
    healthy: list[str] = []

    if frequency > 2.8 or ftir < 55.0:
        bottlenecks.append({
            "stage": "AUDIENCE_SATURATION_AND_FATIGUE",
            "severity": "HIGH",
            "evidence": f"Frequency={frequency:.2f} (>2.8) yoki FTIR={ftir:.1f}% (<55%)",
            "fix": "Auditoriya to'yingan: yangi 3 xil Creative Angle qo'shing va auditoriyani Broad / yangi LAL qatlamiga kengaytiring.",
        })
    else:
        healthy.append(f"Auditoriya yangiligi sog'lom (Frequency={frequency:.2f}, FTIR={ftir:.1f}%)")

    if cpm > 6.5:
        bottlenecks.append({
            "stage": "AUCTION_CPM_INFLATION",
            "severity": "MEDIUM",
            "evidence": f"CPM=${cpm:.2f} (O'zbekiston me'yori $1.50–$5.00 dan yuqori)",
            "fix": "Juda tor qiziqish ustma-ustligi (narrowing) yoki Ad Set'lar o'rtasidagi Overlap >20% ni tekshiring; Placement'da Reels+Feed'ni oching.",
        })
    else:
        healthy.append(f"Auktsion CPM me'yorda (${cpm:.2f})")

    if ctr < 1.0:
        bottlenecks.append({
            "stage": "HOOK_AND_CREATIVE_STOP_RATE",
            "severity": "CRITICAL",
            "evidence": f"Link CTR={ctr:.2f}% (<1.0%) va CPC=${cpc:.2f}",
            "fix": "Muammo auditoriyada emas — KREATIV HOOKDA! Birinchi 3 soniyada aniq og'riq, raqam yoki noodatiy vizual (Demo/50-50) bilan yangi 3 ta Hook yozing (`tools/creative-matrix.py`).",
        })
    else:
        healthy.append(f"Kreativ CTR yaxshi ({ctr:.2f}%)")

    if ctr >= 1.0 and lp_cvr < 8.0:
        bottlenecks.append({
            "stage": "LANDING_OR_TELEGRAM_BOT_FRICTION",
            "severity": "CRITICAL",
            "evidence": f"CTR={ctr:.2f}% yaxshi, lekin Sahifa/Bot konversiyasi (LP CVR)={lp_cvr:.1f}% (<8%)",
            "fix": "Reklama va'dasi (Offer) bilan Landing/Telegram Bot birinchi ekrani mos emas yoki sahifa >3 soniya yuklanyapti. Telegram Botda ortiqcha savollarni 2 taga tushiring.",
        })
    elif lp_cvr >= 8.0:
        healthy.append(f"Voronka (Landing/Bot) konversiyasi sog'lom ({lp_cvr:.1f}%)")

    if lp_cvr >= 8.0 and lead_to_sale < 5.0:
        bottlenecks.append({
            "stage": "LEAD_QUALITY_OR_SALES_SPEED",
            "severity": "HIGH",
            "evidence": f"Lid bor (LP CVR={lp_cvr:.1f}%), lekin Lid->Sotuv={lead_to_sale:.1f}% (<5%)",
            "fix": "1) Sotuv bo'limi lidga >15 daqiqada qo'ng'iroq qilyapti; 2) Kreativda narx/byudjet filtri (Solventnost) yo'qligi sababli pulsiz lidlar tushyapti — Instant Form/Botga 2 ta saralovchi savol qo'shing.",
        })
    elif lead_to_sale >= 5.0:
        healthy.append(f"Sotuv konversiyasi me'yorda ({lead_to_sale:.1f}%)")

    return {
        "overall_health": "CRITICAL_BOTTLENECK_FOUND" if any(b["severity"] == "CRITICAL" for b in bottlenecks)
                          else ("NEEDS_OPTIMIZATION" if bottlenecks else "HEALTHY_SCALABLE"),
        "bottlenecks": bottlenecks,
        "healthy_signals": healthy,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="meta-audience.py",
        description="Tyrion Meta Ads Audience Architecture Engine (Andromeda 2 + UZ Market)",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_arch = sub.add_parser("architect", help="4-qatlamli Meta Ads auditoriya arxitekturasi va Exclusion matritsasi")
    p_arch.add_argument("--niche", choices=list(NICHE_TAXONOMY.keys()), default="ecom")
    p_arch.add_argument("--daily-budget", type=float, required=True)
    p_arch.add_argument("--geo", default="uzbekistan")
    p_arch.add_argument("--target-cpa", type=float, default=None)
    p_arch.add_argument("--has-pixel", action="store_true")
    p_arch.add_argument("--has-crm", action="store_true")
    p_arch.add_argument("--ig-followers", type=int, default=5000)
    p_arch.add_argument("--json", action="store_true")

    p_int = sub.add_parser("interests", help="Nisha bo'yicha Interest Cluster, Behavior va Solventnost filtrlari")
    p_int.add_argument("--niche", choices=list(NICHE_TAXONOMY.keys()), default="ecom")
    p_int.add_argument("--query", default="")
    p_int.add_argument("--live", action="store_true", help="META_ACCESS_TOKEN orqali jonli Graph API qidiruvi")
    p_int.add_argument("--json", action="store_true")

    p_ovl = sub.add_parser("overlap", help="Ikki ad set o'rtasidagi Auction Overlap foizini hisoblash")
    p_ovl.add_argument("--size-a", type=int, required=True)
    p_ovl.add_argument("--size-b", type=int, required=True)
    p_ovl.add_argument("--shared", type=int, required=True)
    p_ovl.add_argument("--json", action="store_true")

    p_sat = sub.add_parser("saturation", help="Auditoriya sig'imi, Frequency va charchash kunini hisoblash")
    p_sat.add_argument("--audience-size", type=int, required=True)
    p_sat.add_argument("--daily-budget", type=float, required=True)
    p_sat.add_argument("--cpm", type=float, default=3.2)
    p_sat.add_argument("--days", type=int, default=14)
    p_sat.add_argument("--json", action="store_true")

    p_ret = sub.add_parser("retargeting", help="Dinamik Retargeting oynalari (3d/7d/14d/30d/180d) va byudjet hisobi")
    p_ret.add_argument("--aov", type=float, default=100.0)
    p_ret.add_argument("--daily-visitors", type=int, default=300)
    p_ret.add_argument("--ig-engagers", type=int, default=5000)
    p_ret.add_argument("--video-viewers", type=int, default=8000)
    p_ret.add_argument("--has-telegram-bot", action="store_true", default=True)
    p_ret.add_argument("--json", action="store_true")

    p_lal = sub.add_parser("lookalike", help="Lookalike (LAL) seed sifati va 1%-5% pog'onali hajm hisoblagichi")
    p_lal.add_argument("--seed-size", type=int, required=True)
    p_lal.add_argument("--seed-type", default="purchase_ltv",
                       choices=["purchase_ltv", "purchase_all", "qualified_leads", "raw_leads", "ig_engagers"])
    p_lal.add_argument("--country", default="UZ")
    p_lal.add_argument("--json", action="store_true")

    p_diag = sub.add_parser("diagnose", help="Meta Ads metrikalar zanjiridan (CPM->CTR->CVR->Sale) tor joyni topish")
    p_diag.add_argument("--cpm", type=float, required=True)
    p_diag.add_argument("--ctr", type=float, required=True)
    p_diag.add_argument("--cpc", type=float, default=0.35)
    p_diag.add_argument("--lp-cvr", type=float, required=True)
    p_diag.add_argument("--lead-to-sale", type=float, default=10.0)
    p_diag.add_argument("--frequency", type=float, default=1.6)
    p_diag.add_argument("--ftir", type=float, default=72.0)
    p_diag.add_argument("--json", action="store_true")

    args = parser.parse_args(argv)

    try:
        if args.command == "architect":
            res = build_architecture(
                niche=args.niche,
                daily_budget=args.daily_budget,
                geo=args.geo,
                has_pixel=args.has_pixel,
                has_crm=args.has_crm,
                ig_followers=args.ig_followers,
                target_cpa=args.target_cpa,
            )
        elif args.command == "interests":
            res = get_interests(args.niche, args.query, args.live)
        elif args.command == "overlap":
            res = calc_overlap(args.size_a, args.size_b, args.shared)
        elif args.command == "saturation":
            res = calc_saturation(args.audience_size, args.daily_budget, args.cpm, args.days)
        elif args.command == "retargeting":
            res = calc_retargeting(args.aov, args.daily_visitors, args.ig_engagers, args.video_viewers, args.has_telegram_bot)
        elif args.command == "lookalike":
            res = calc_lookalike(args.seed_size, args.seed_type, args.country)
        elif args.command == "diagnose":
            res = diagnose_metrics(args.cpm, args.ctr, args.cpc, args.lp_cvr, args.lead_to_sale, args.frequency, args.ftir)
        else:
            return 2
    except Exception as exc:
        print(f"Xato: {exc}", file=sys.stderr)
        return 2

    if getattr(args, "json", False):
        print(json.dumps(res, ensure_ascii=False, indent=2))
        return 0

    print("=" * 66)
    print(f"  🎯 TYRION META AUDIENCE ENGINE — {args.command.upper()}")
    print("=" * 66)
    for k, v in res.items():
        if isinstance(v, list):
            print(f"\n  [{k}]:")
            for item in v:
                if isinstance(item, dict):
                    title = item.get("layer") or item.get("stage") or item.get("name") or ""
                    print(f"    • {title}")
                    for sk, sv in item.items():
                        if sk not in ("layer", "stage", "name"):
                            print(f"        {sk}: {sv}")
                else:
                    print(f"    • {item}")
        elif isinstance(v, dict):
            print(f"\n  [{k}]:")
            for sk, sv in v.items():
                print(f"    - {sk}: {sv}")
        else:
            print(f"  {k}: {v}")
    print("=" * 66)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
