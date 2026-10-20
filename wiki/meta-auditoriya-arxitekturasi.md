---
name: meta-auditoriya-arxitekturasi
description: "Meta Ads Andromeda 2 auditoriya arxitekturasi — 4 qatlamli voronka (Broad, Interest Stack, 1P Custom Audience, Value LAL), Exclusion matritsasi, Overlap va Saturation matematikasi"
tags: [meta-ads, auditoriya, retargeting, lookalike, exclusion, andromeda]
source: "tools/meta-audience.py + wiki/meta-kampaniya-tuzilmalari.md + wiki/andromeda-scalability-signal.md (2026-10-18)"
updated: 2026-10-18
---

# 🎯 Meta Ads Auditoriya Arxitekturasi (Andromeda 2 + UZ Standarti)

> **Asosiy tamoyil:** Andromeda 2 algoritmida auditoriyani faqat qiziqish (interest) bilan qidirish eskirgan — **kreativ burchak (angle) birlamchi filtr**, 1P Custom Audience va Exclusion matritsasi esa byudjetni kannibalizatsiyadan himoya qiluvchi temir panjaradir ([[content-is-targeting]], [[meta-kampaniya-tuzilmalari]]).

## 1. To'rt Qatlamli Auditoriya Piramidasi

| Qatlam | Ulush | Tarkibi va Sozlamasi | Majburiy Exclusion (Istisno) |
|---|---|---|---|
| **1. Broad + Signal Steering (TOF)** | 40–50% | Faqat Geo + Yosh + Til. Algoritm video/rasmning ilk 3 soniyasidagi hook orqali mos auditoriyani o'zi topadi ([[andromeda-scalability-signal]]) | `Purchase_180d`, `CRM_Active_Clients`, `LeadForm_Submitted_90d` |
| **2. Advantage+ Interest & Solventnost (TOF)** | 20–30% | Sohaga xos 3–5 ta yirik Interest Cluster + `Engaged Shoppers` yoki `Frequent Travelers` ([[meta-ads-interest-api]]) | `Purchase_180d`, `CRM_Active_Clients`, `LeadForm_Submitted_90d` |
| **3. First-Party (1P) Warm Retargeting (MOF)** | 15–20% | `IG_Engaged_30d`, `Video_50pct_14d`, `LeadForm_Opened_Not_Submitted_30d`, `Web_Visitors_30d` | `Purchase_180d`, `LeadForm_Submitted_30d`, `InitiateCheckout_7d` |
| **4. Value LAL & Hot BOF Closing** | 10–15% | **LAL 1% / 1–2%** (faqat CRM/CAPI to'lov qilgan mijozlardan!) + **BOF:** `AddToCart_14d`, `Checkout_7d`, `CRM_Unclosed_14d` | `Purchase_30d` (BOF uchun) / `Purchase_180d` (LAL uchun) |

## 2. O'zbekiston Bozorida Auditoriya Qonunlari ([[30-ozbekiston-konteksti]])

1. **Til bo'yicha Ad Set Izolyatsiyasi:** O'zbek (lotin/kirill) va Rus tilidagi kreativlarni bitta ad set ichiga qo'ymang. Algoritm arzonroq CPM bergan tilga byudjetni burib yuboradi. Har bir til uchun alohida ad set ochiladi.
2. **Toshkent vs Viloyatlar Geo-Split:** Toshkent shahri va viloyatlarni bitta CBO kampaniyada birlashtirmang — viloyatlarda CPM 2–3 barobar arzon bo'lgani uchun byudjet viloyatga oqib ketadi, to'lov qobiliyati esa Toshkentda yuqori.
3. **Instagram Direct va Lead Form — Asosiy 1P Baza:** Trafik Telegram botga yoki Direct'ga ketganda Web Pixel ko'r bo'lib qoladi. Shuning uchun `IG_Engaged_30d` (shu jumladan Direct yozishmalar) va `LeadForm_Opened_30d` O'zbekistonda eng kuchli retargeting manbaidir.
4. **Sifatsiz Lidlardan LAL Yasash Taqiqi:** Arzon lead formadan tushgan barcha raqamlardan Lookalike (LAL) yasalsa, Meta yana "bekorchi raqam qoldiruvchilar"ni topadi. LAL faqat **CRM'da tasdiqlangan (`Qualified` / `Paid`)** kamida 100–500 ta mijoz bazasidan quriladi.

## 3. Auction Overlap va Saturation Matematikasi (`tools/meta-audience.py`)

- **Auction Overlap Chegarasi:** Ikki ad setning o'zaro ustma-ust tushishi kichik ad set hajmining **$\le 20\%$** qismidan oshmasligi shart (`py -3 tools/meta-audience.py overlap`). Agar $>25\%$ bo'lsa — ad setlarni birlashtiring (konsolidatsiya) yoki o'zaro Exclude qiling.
- **Saturation va Charchash (Fatigue):** 14 kunlik oynada Prospecting Frequency **$\le 2.5	ext{x}$** (FTIR $\ge 60\%$) bo'lishi kerak (`py -3 tools/meta-audience.py saturation`). Frequency $>2.8	ext{x}$ ga chiqsa, CPA keskin qimmatlashadi ([[kreativ-hit-rate]]).

## Anti-Patterns (WRONG vs CORRECT)

- **FAIL: WRONG** — Sovuq (Prospecting) kampaniyada `Purchase_180d` va `IG_Engaged_30d` ni Exclude qilmasdan yoqish (natijada sovuq kampaniya issiq bazaga reklama ko'rsatib, yolg'on ROAS beradi).
- **PASS: CORRECT** — `meta-audience.py architect` orqali barcha TOF ad setlardan mavjud mijozlar va so'nggi 90 kunlik lidlarni qat'iy Exclude qilish; ASC kampaniyada esa `Existing Customer Budget Cap = 25%` o'rnatish ([[learning-phase-qoidalari]]).

## Manba

- `tools/meta-audience.py` — Deterministik Meta Ads auditoriya dvigateli
- [[meta-ads-interest-api]] · [[meta-kampaniya-tuzilmalari]] · [[content-is-targeting]] · [[andromeda-scalability-signal]] · [[30-ozbekiston-konteksti]]
