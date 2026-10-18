---
name: meta-ads-interest-api
description: "Meta/Facebook Ads Graph API va lokal taksonomiya orqali qiziqishlar (interests), xulq-atvor (behaviors) va to'lov qobiliyati (solventnost) tadqiqoti"
tags: [meta-ads, api, interests, auditoriya, targeting]
source: "tools/meta-audience.py + Meta Marketing API v22.0 (2026-10-18)"
updated: 2026-10-18
---

# 📘 Meta Ads Interest API & Qiziqishlar Taksonomiyasi

> **⚠️ Xavfsizlik va Ruxsatlar qoidasi ([[40-xavfsizlik-va-hisob]]):**
> * Reklama kampaniyalarini o'chirish, yoqish yoki byudjetni o'zgartirish **QAT'IYAN TAQIQLANADI**.
> * Bu vosita faqat **o'qish (read-only)** va auditoriya arxitekturasini loyihalash uchun ishlatiladi ([[meta-auditoriya-arxitekturasi]]).

## 🔑 API va CLI Konfiguratsiyasi

* **Asosiy CLI asbob (0 token, oflayn + onlayn):** `py -3 tools/meta-audience.py interests --niche <niche>`
* **Access Token (ixtiyoriy jonli API uchun):** `.env` faylida saqlanadi (`META_ACCESS_TOKEN`, namuna: `.env.example`).
* **Graph API Endpoint:** `GET https://graph.facebook.com/v22.0/search?type=adinterest&q=<keyword>&limit=20`

## 📂 Saved Interest Categories (8 Asosiy Soha Bo'yicha Qiziqishlar Bazasi)

| Soha (`--niche`) | Asosiy Interest Klasterlari | Yuqori Niyatli Behavior Signallari |
|---|---|---|
| **E-Commerce (`ecom`)** | `Online shopping`, `Shopping and fashion`, `Boutique`, `Discount store`, `Consumer electronics` | `Engaged Shoppers`, `iPhone 14/15/16 Pro owners` |
| **Ta'lim (`edu`)** | `Higher education`, `Online learning`, `Language school`, `IELTS`, `Career development` | `Parents (All / Teenagers 13-17)`, `International travelers` |
| **Ko'chmas mulk (`real-estate`)** | `Real estate`, `Property investment`, `Apartment`, `Mortgage loan`, `Luxury real estate` | `Frequent International Travelers`, `Small Business Owners` |
| **Tibbiyot (`medical`)** | `Healthcare`, `Dentistry`, `Cosmetic dentistry`, `Physical therapy`, `Wellness` | `Geo-radius (+5..15 km)`, `30-55 yosh to'lovga qodir qatlam` |
| **B2B / SaaS (`b2b`)** | `Small and medium-sized enterprises`, `Entrepreneurship`, `Business management`, `CRM` | `Facebook Page Admins`, `Small Business Owners` |
| **Go'zallik (`beauty`)** | `Cosmetics`, `Fragrances`, `Beauty salon`, `Skin care`, `Luxury goods` | `Engaged Shoppers`, `Instagram active engagers` |
| **Avto (`auto`)** | `Automobile`, `Car dealership`, `Auto detailing`, `SUV`, `Automotive repair shop` | `Shahar markazidagi avto-egalari (24-55 yosh)` |
| **Lokal xizmat (`local`)** | `Physical fitness`, `Gym`, `Restaurants`, `Tourism`, `Resort`, `Family entertainment` | `People living in or recently in location (+3..10 km)` |

## 💎 O'zbekiston Bozori Uchun To'lov Qobiliyati (Solventnost) Filtrlari

O'zbekistonda yuqori chekli mahsulot yoki B2B xizmat sotganda qiziqishlar ustiga (yoki alohida test ad setda) quyidagi qatlamlar qo'llanadi ([[30-ozbekiston-konteksti]]):

1. **`Engaged Shoppers`** — so'nggi 7 kunda reklamadagi CTA tugmasini bosgan faol xaridorlar.
2. **`Frequent International Travelers`** — chet elga chiquvchi, valyuta/karta to'lov qobiliyatiga ega auditoriya.
3. **`Mobile Device: iPhone Pro / Pro Max`** — premium segment filtri.
4. **`Facebook Page Admins` / `Small Business Owners`** — tadbirkorlar va qaror qabul qiluvchilar.
5. **Geo-Tiering:** Toshkent shahri va Viloyatlar **hech qachon** bitta CBO kampaniyada aralashtirilmaydi (viloyatning arzon CPM'i byudjetning 80% ini tortib oladi).

## 💻 CLI va API Integratsiyasi (Agent Uchun)

```powershell
# 1. Nisha bo'yicha tayyor Interest klasterlar va Solventnost filtrlarini olish (0 token)
py -3 tools/meta-audience.py interests --niche real-estate

# 2. To'liq 4-qatlamli auditoriya arxitekturasi va Exclusion matritsasini tuzish
py -3 tools/meta-audience.py architect --niche ecom --daily-budget 150 --geo tashkent --has-pixel --has-crm

# 3. Agar .env da META_ACCESS_TOKEN bo'lsa, jonli Graph API dan o'qish
py -3 tools/meta-audience.py interests --niche b2b --query "entrepreneurship" --live
```

**Bog'liq:** [[meta-auditoriya-arxitekturasi]] · [[meta-ads-sozlamalari]] · [[meta-kampaniya-tuzilmalari]] · [[content-is-targeting]]
