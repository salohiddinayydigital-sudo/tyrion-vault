---
name: meta-breakdown-effekti
description: "Meta Ads 'Breakdown Effect' (Marginal vs Average CPA) — nega o'rtacha CPA baland ko'ringan placement yoki segmentni o'chirish umumiy natijani buzadi"
tags: [meta-ads, breakdown-effect, cpa, auktsion, algoritm]
source: "Meta Official Breakdown Effect Documentation + mathiaschu/meta-ads-analyzer tahlili (2026-10-18)"
updated: 2026-10-18
---

# 📉 META ADS "BREAKDOWN EFFECT" (MARGINAL VS AVERAGE CPA)

## 1. Muammo: Targetologlarning #1 Xatosi
Meta Ads Manager'da `Breakdown -> By Placement` (yoki `Yosh / Jins / Hudud`) ochilganda ko'pincha bunday manzara ko'rinadi:
- **Instagram Reels:** Sarf `$750` (83%), Konversiya `50` ta $	o$ **O'rtacha CPA = `$15.00`**
- **Facebook Feed:** Sarf `$150` (17%), Konversiya `12` ta $	o$ **O'rtacha CPA = `$12.50`**

Tajribasiz targetolog *"Facebook Feed arzonroq ekan ($12.50 vs $15.00), Instagram Reels'ni o'chirib, butun pulni Facebook Feed'ga beraman"* deb o'ylaydi. Natijada keyingi 3 kunda umumiy CPA `$14.52` dan **`$20.00+`** ga sakrab ketadi!

## 2. Sabab: Marginal CPA vs Average CPA
Meta Andromeda auktsioni **o'rtacha CPA (Average CPA)** bo'yicha emas, balki **navbatdagi konversiya narxi (Marginal CPA)** bo'yicha pul taqsimlaydi:
1. Algoritm avval `Facebook Feed` dagi eng arzon `12` ta konversiyani terib oladi (`$12.50`).
2. `13-chi` konversiyaning marginal narxi Facebook Feed'da `$19.00` ga chiqib ketgani sababli, algoritm byudjetni `Instagram Reels` ga yo'naltiradi (chunki u yerda `$15.00` dan o'nlab konversiya olish imkoni bor).
3. Agar siz dominant placement (`Instagram Reels`) ni majburan o'chirsangiz, Meta butun `$900` byudjetni `Facebook Feed` ning qimmat marginal egri chizig'iga sarflashga majbur bo'ladi.

## 3. Deterministik Tekshiruv (`0 token`)
Har qanday placement yoki segmentni o'chirishdan oldin Tyrion CLI orqali tekshiring:
```bash
python3 tools/ad-export-analyzer.py breakdown-effect --seg-a-name "Instagram Reels" --seg-a-spend 750 --seg-a-conv 50 --seg-b-name "Facebook Feed" --seg-b-spend 150 --seg-b-conv 12
```

**Bog'liq:** [[andromeda-scalability-signal]] · [[learning-phase-qoidalari]] · [[meta-auditoriya-arxitekturasi]] · [[akkaunt-audit-xatolari]]
