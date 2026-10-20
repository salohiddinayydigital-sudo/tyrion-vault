---
name: unit-iqtisodiyot-formulalari
description: "Har bir reklama qarorining asosi — CAC/CPL/LTV/ROAS/POAS/MER formulalari, break-even va target ROAS, LTV:CAC chegaralari, byudjetni orqadan hisoblash"
tags: [metrika, iqtisod, byudjet, formula]
source: "claude-ads-main/local/raw/claudes-bilim/marketolog/KNOWLEDGE.md (§4 Unit iqtisodiyot)"
updated: 2026-09-20
---

# Unit iqtisodiyot — formulalar

> Bog'lanishlar: [[blended-roas-net-cash]] · [[taklif-tuzilishi]] · [[ad-iteration]] · [[scaling-cheklovlari]]

**Marjinallik noma'lum bo'lsa — quyidagi hech qaysi formula ishlamaydi.** GM% (gross margin) hamma narsaning kaliti.

## Asosiy formulalar

```
CAC           = (marketing + sotuv xarajati) / yangi mijozlar
CPL           = reklama xarajati / lead soni
Lead→mijoz %  = mijozlar / leadlar
CPA (mijoz)   = CPL / (lead→mijoz %)

GM%           = (daromad − to'g'ridan-to'g'ri xarajat) / daromad
LTV           = ARPU × GM% × o'rtacha mijoz umri (oy)
LTV (churn)   = (ARPU × GM%) / oylik churn %
CAC payback   = CAC / (oylik ARPU × GM%)   → oyda

ROAS          = reklamadan daromad / reklama xarajati
POAS          = reklamadan sof foyda / reklama xarajati
MER           = umumiy daromad / umumiy reklama xarajati

Break-even ROAS = 1 / GM%
Break-even CPA  = AOV × GM%
Target ROAS     = 1 / (GM% − maqsad sof marja %)
```

## Hisoblangan misol (illyustratsiya)

Onlayn kurs: narx 1 200 000 so'm, to'g'ridan-to'g'ri xarajat 420 000 (platforma, komissiya, o'qituvchi ulushi).

```
GM%             = (1 200 000 − 420 000) / 1 200 000 = 0.65
Break-even ROAS = 1 / 0.65 = 1.54
Break-even CPA  = 1 200 000 × 0.65 = 780 000 so'm
Maqsad 20% sof marja → Target ROAS = 1 / (0.65 − 0.20) = 2.22
```

**O'qilishi:** ROAS < 1.54 — zarar · 1.54–2.22 — nolga ishlash · > 2.22 — foyda.
Kabinetdagi "ROAS 2.0" o'z-o'zicha yaxshi ham, yomon ham emas — GM% ni bilmasdan hukm chiqarib bo'lmaydi.

**Lead voronkasi:** lead→mijoz 12% bo'lsa, maksimal CPL = 780 000 × 0.12 = **93 600 so'm**. Bu byudjet rejalashtirishning yagona to'g'ri kirish nuqtasi.

## Byudjetni orqadan hisoblash

```
Maqsad: oyiga 20 ta mijoz · lead→mijoz 12%  → kerakli lead = 20/0.12 = 167
Maksimal CPL 93 600                          → byudjet = 167 × 93 600 ≈ 15.6 mln so'm/oy
```

Mijoz byudjeti 5 mln bo'lsa — maqsad real emas. Ikki yo'l: konversiyani oshirish yoki maqsadni tushirish.
Buni **oldindan** ayt, kampaniya oxirida emas.

## LTV : CAC — nima demoqchi

| Nisbat | O'qilishi | Harakat |
|---|---|---|
| < 1:1 | Har bir mijoz zarar | Darhol to'xtat; offer/narxni qayta ko'r |
| 1:1 – 3:1 | Nozik, o'sish moliyalashtirilmaydi | Konversiya va AOV ustida ishla |
| ≈ 3:1 | Sog'lom chegara | Bu sanoat evristikasi, qonun emas |
| > 5:1 | Kam investitsiya qilinyapti | Byudjetni oshir |

**CAC payback:** umumqabul qilingan chegara < 12 oy; kichik biznesda pul aylanmasi tor → amalda **< 3 oy** maqsad qilinadi.

## Bog'liq xatolar

- LTV ni marjasiz hisoblash — aylanmani LTV deb olish CAC ni 2-3 barobar ortiq ko'rsatadi ([[akkaunt-audit-xatolari]]).
- GM% bilmasdan ROAS maqsadi qo'yish.
- Kanal taqqoslashni atribusiyasiz qilish — bitta haqiqat manbai: CRM yoki MER.

## Manba

- `claude-ads-main/local/raw/claudes-bilim/marketolog/KNOWLEDGE.md` §4
