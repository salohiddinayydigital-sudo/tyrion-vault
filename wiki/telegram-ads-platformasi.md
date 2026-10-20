---
name: telegram-ads-platformasi
description: "Telegram Ads rasmiy platformasi (ads.telegram.org / Fragment), kanallarni tanlash, 160 belgili matn andozalari, bot voronkasi va server-side konversiya o'lchash tizimi"
tags: [telegram, ads, platforma, voronka, marketing]
source: "Telegram Ads official documentation & local operator playbooks"
updated: 2026-10-17
---

# Telegram Ads rasmiy platformasi va konversiya voronkasi

> Bog'lanishlar: [[telegram-voronka-va-email-minimum]] · [[30-ozbekiston-konteksti]] · [[voronka-metrikalari]] · [[blended-roas-net-cash]]

Telegram Ads — O'zbekiston va MDH bozorida eng yuqori diqqat va o'qilish darajasiga ega bo'lgan rasmiy reklama platformasi hisoblanadi.

---

## 1. Platforma xususiyatlari va kirish

- **Boshqaruv:** `ads.telegram.org` yoki `Fragment` (TON / Telegram Stars orqali to'g'ridan-to'g'ri to'lov).
- **Format:** Matnli e'lon (maksimal 160 ta belgi).
- **Harakatga chaqiruv (CTA):** Tugma ko'rinishida (`Kanalga o'tish`, `Botni ochish`, `Postni ko'rish` yoki tashqi veb-sayt havolasi).
- **Auksion:** CPM (har 1,000 ko'rsatish uchun narx) modeli.

---

## 2. Targetlash turlari va kanal tanlash

Telegram Ads'da ikkita asosiy targetlash usuli mavjud:

1. **Aniq kanallar bo'yicha (Channel-Specific Targeting) — TAVSIYA ETILADI:**
   - Reklama faqat qo'lda tanlangan, tasdiqlangan kanallarda chiqadi.
   - Tanlov mezoni: obunachilar $\ge 1,000$, Engagement Rate on Reach (ERR) $\ge 15\%$, auditoriya mavzusi mahsulotga to'g'ridan-to'g'ri mos.
   - Soxta (nakrutka) qilingan yoki nofaol kanallar darhol chiqarib tashlanadi (Negative Channels).
2. **Keng mavzular bo'yicha (Topic/Category Targeting):**
   - Moliya, IT, Ko'chmas mulk, Ta'lim kabi sohalar bo'yicha.
   - Ehtiyotkorlik: Keng mavzular byudjetni tez yeydi, konversiya aniq kanallarga nisbatan 2-3 barobar past bo'lishi mumkin.

---

## 3. 160 Belgili Sotuvchi Matn Formulalari

Telegram moderatsiyasi juda qat'iy:
- **Taqiqlanadi:** ALL CAPS so'zlar, bittadan ortiq emoji, yolg'on va'dalar ("100% kafolat", "$10,000 daromad"), agressiv clickbait.
- **Ruxsat etiladi:** Aniq fakt, xolis taklif, muammo va yechim.

### Ishlaydigan 3 ta formula:
1. **Muammo $\to$ Aniq Yechim:**
   `Qimmat reklamadan charchadingizmi? Telegram Ads orqali lid narxini 2x arzonlashtiring. Bepul qo'llanmani oling:`
2. **Keys / Ijtimoiy dalil:**
   `Toshkentdagi 40+ kompaniya Telegram bot orqali qanday sotuv qildi? Amaliy keysni botdan o'qing:`
3. **Auditoriyani chaqirish:**
   `Kompaniya rahbarlari uchun: biznes jarayonlarini avtomatlashtirish bo'yicha 5 ta tayyor shablon. Yuklab oling:`

---

## 4. Konversiya va Bot Voronkasi

Telegram'da brauzer piksellari ishlamagani uchun voronka bot orqali o'lchanadi:

```
Telegram Reklama (160 belgi)
        ↓
Bot Deep Link (t.me/BrandBot?start=tgads_reklama1)
        ↓
Avtomatik xush kelibsiz xabari (< 10 soniyada) + Lead Magnit
        ↓
3-5 kunlik ishonch kontenti (avtomatik xabarlar)
        ↓
Menejer bilan shaxsiy muloqot (DM) $\to$ Sotuv
```

**Telemetriya:**
Bot backendidan CRM tizimiga (AmoCRM, Bitrix24) har bir `/start`, lead magnit yuklash va kontakt qoldirish hodisasi **webhook** orqali uzatiladi. Natijada har bir Telegram kanalidan tushgan **sof tushum (Net Revenue)** aniq o'lchanadi.

---

## Manbalar
- `ads/references/telegram-audit.md`
- `claude-ads-main/local/raw/claudes-bilim/marketolog/KNOWLEDGE.md`
