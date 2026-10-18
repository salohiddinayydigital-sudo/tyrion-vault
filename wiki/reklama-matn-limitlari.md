---
name: reklama-matn-limitlari
description: "Meta va Google reklama matni limitlari (Facebook/Instagram Feed, RSA, Performance Max) va ular bilan ishlashning amaliy qoidalari"
tags: [matn, limit, meta-ads, google-ads]
source: "claude-ads-main/local/raw/claudes-bilim/kopirayter/KNOWLEDGE.md (§9) + marketolog/KNOWLEDGE.md (§6-7)"
updated: 2026-09-20
---

# Reklama matni limitlari (Meta + Google)

> Bog'lanishlar: [[kreativ-sikl]] · [[funnel-2-kreativ-format]] · [[meta-ads-sozlamalari]] · [[ab-test-mexanikasi]]

Bu raqamlar — **tavsiya etilgan** chegaralar (kesilib qolmasligi uchun), texnik maksimum emas.

## Meta (Facebook / Instagram)

| Joylashuv | Primary text | Headline | Description |
|---|---|---|---|
| Facebook Feed (rasm/video) | 50–150 belgi | 27 belgi | Ads Guide'da ko'rsatilmagan |
| Instagram Feed (rasm) | 125 belgi | 40 belgi | — |

- Instagram Feed'da "See more" kesilishi **~125 belgida** — **hook shu chegara ichida bo'lishi shart**.
- Instagram: maksimum 30 ta hashtag. Dizayn: 4:5, 1440×1800 px, min 600×750, 30 MB gacha.
- Video: 4:5, MP4/MOV/GIF, 1 sekunddan 241 daqiqagacha.

🟢 Manba: https://www.facebook.com/business/ads-guide/image/facebook-feed

**Amaliy natija:** birinchi jumla **8–12 so'z**, o'zi bilan mustaqil ma'no beradigan bo'lsin.

## Google Ads — Responsive Search Ad (RSA)

| Element | Soni | Uzunlik |
|---|---|---|
| Headline | min 3, max 15 | har biri 30 belgi |
| Description | min 2, max 4 | har biri 90 belgi |
| Display path | 2 ta maydon | har biri 15 belgi |

- Headline 1 va Description 1 odatda ko'rinadi; Headline 2-3 va Description 2 faqat tizim foydali deb hisoblasa.
- **Kafolatlangan matn** (brend nomi, litsenziya raqami) faqat **Headline 1, 2 yoki Description 1** ga pin qilinadi.

🟢 Manba: https://support.google.com/google-ads/answer/7684791

## Google Ads — Performance Max asset group

- **Headlines:** min 3, max 15, 30 belgi; **kamida bittasi 15 belgidan qisqa** bo'lishi shart
- **Long headlines:** min 1, max 5, 90 belgi · **Descriptions:** min 2, max 5, 90 belgi · **Biznes nomi:** 25 belgi
- Rasmlar: 1.91:1 (4+), 1:1 (4+), 4:5 (2+), logo 1:1 (1 majburiy). Video: min 1, max 15, ≥10 sekund.

🟢 Manba: https://support.google.com/google-ads/answer/17091269

## Learning phase bilan bog'liq

- Ad set oxirgi jiddiy tahrirdan keyin 7 kunda ~50 event yig'masa — "Learning limited".
  Ya'ni **matnni tez-tez o'zgartirish o'rganishni qayta boshlaydi** → variantlarni bir vaqtda qo'y ([[learning-phase-qoidalari]]).
- Meta endi dinamik chegara ishlatadi (`dynamic_lp_conversions_threshold`) — 50 hamma holatda qat'iy emas.
- **5 tadan ortiq matnni bir ad set ga tiqma** — o'zi "learning limited" sabablaridan biri.

## Manba

- `claude-ads-main/local/raw/claudes-bilim/kopirayter/KNOWLEDGE.md` §9
- `claude-ads-main/local/raw/claudes-bilim/marketolog/KNOWLEDGE.md` §6–7
