---
name: playbook-nisha-ecommerce-uz
description: "E-Commerce, kiyim-kechak, texnika va online do'konlar uchun Meta + Telegram sotuv voronkasi"
tags: [playbook, ecommerce, fashion, electronics]
source: "Tyrion v3.0 Niche Playbooks"
updated: 2026-10-17
---

# 🛍️ E-COMMERCE, MODA VA TEXNIKA PLAYBOOKI

## 1. Asosiy Muammo va Yechim
To'g'ridan-to'g'ri "Sotib oling, narxi X so'm" degan katalog rasmlar past CTR va qimmat CPA beradi.
**Yechim:** Mahsulotning o'ziga xos xususiyatini ekstremal yoki ko'rgazmali test orqali ko'rsatish (masalan: kostyumning g'ijimlanmasligi va suv o'tkazmasligini jonli sinash → real keysda **1 kunda 40 ta kostyum sotuv**).

## 2. Voronka va To'lov Arxitekturasi
- **Arzon chek (<$40):** Reels/Video Ads → Instagram DM / Telegram Bot katalog → Darhol buyurtma (eshik oldida to'lov + tezkor dostavka).
- **Yuqori chek ($50–$1,000, texnika/mebel):** Reels Demo → Landing yoki TG Bot → **Uzum Nasiya / Alif Nasiya (oyiga X so'mdan, boshlang'ich to'lovsiz)** taklifi → Call-center tasdiqlash.

## 3. Meta Ads Auditoriya Sozlamasi
- `python3 tools/meta-audience.py architect --niche ecom --budget 100 --geo tashkent --has-pixel --has-crm`
- **BOF Dynamic Retargeting:** `AddToCart 14d` va `ViewContent 14d` (`Purchase 30d` exclude) uchun: *"Savatchangizda qolgan mahsulotga bugun bepul yetkazib berish!"*

**Bog'liq:** [[nisha-playbooklar]] · [[optimitzaetsiya-va-case]] · [[metrikalar-formulalari]]
