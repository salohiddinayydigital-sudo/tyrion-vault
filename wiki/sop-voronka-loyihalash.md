---
name: sop-voronka-loyihalash
description: "SOP: voronka loyihalash va metrika o'rnatish — bosqichlar zanjiri, Telegram ustuvorligi, eng tor joyni topish, nazorat paneli"
tags: [sop, voronka, metrika, tracking]
source: "claude-ads-main/local/raw/claudes-bilim/marketolog/PLAYBOOKS.md (PB-2)"
updated: 2026-09-20
---

# SOP — Voronka loyihalash va metrika o'rnatish

> Bog'lanishlar: [[voronka-metrikalari]] · [[unit-iqtisodiyot-formulalari]] · [[telegram-voronka-va-email-minimum]] · [[survey-funnel]]

**Qachon:** trafik bor, sotuv yo'q; yoki yangi biznesga birinchi voronka kerak; yoki "pul qayerda yo'qolayotganini bilmayman".

## Kirish ma'lumotlari

Offer ([[sop-pozitsiyalash-offer-qurish]] dan) · hozirgi kanallar · hozirgi raqamlar · **o'rtacha chek va marja**.

## Qadamlar

1. **Bosqichlarni chiz.** Har biri uchun: nima sodir bo'ladi · qayerda · qanday o'lchanadi.
   Mahalliy standart zanjir:
   `Reklama ko'rish → Bosish → Sahifa → Telegram/qo'ng'iroq → Suhbat → Sotuv → Takroriy`
2. **Telegramni birinchi ko'rib chiq** — email voronkasi ko'pincha ishlamaydi; sahifadan Telegramga o'tish formadan kuchliroq bo'ladi.
3. **Har bosqichga metrik va bugungi qiymat qo'y.** Noma'lum bo'lsa — **"o'lchanmagan"** deb yoz, taxmin qilma.
   O'lchanmagan bosqich — birinchi tuzatiladigan joy.
4. **Unit iqtisodiyotni hisobla:** CAC, o'rtacha chek, marja, break-even ROAS, payback ([[unit-iqtisodiyot-formulalari]]).
   **Break-even ROAS = 1 / marja** — bundan pastda reklama zarar.
5. **Eng tor joyni top.** Har bosqichda yo'qotilayotgan odam sonini hisobla. Eng ko'p yo'qotayotgan bosqich — birinchi ish.
6. **O'lchash tizimini o'rnat** (tekin): UTM, GA4, Meta Pixel/CAPI, Telegram bot statistikasi, Google Sheets jurnali.
7. **Nazorat paneli qur** — bosqichlar, haftalik raqamlar, konversiya %, CAC, ROAS. **Kim to'ldiradi va qachon** — aniq yoz.

## Chiqish artefakti

`VORONKA.md` — sxema, bosqich metrikalari jadvali, unit iqtisodiyot hisobi, UTM shabloni, nazorat paneli strukturasi.

## Muvaffaqiyat mezoni

Har bosqich uchun raqam bor yoki "o'lchanmagan" deb belgilangan; **eng tor joy aniq ko'rsatilgan**.

## Manba

- `claude-ads-main/local/raw/claudes-bilim/marketolog/PLAYBOOKS.md` PB-2
