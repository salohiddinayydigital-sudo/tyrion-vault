---
description: Boshlash — tizim bilan tanishish, demo rejim yoki yangi mijozni ishga tushirish
argument-hint: [demo | <mijoz>]
---

# /start — Tyrion bilan boshlash

Vazifa: **$ARGUMENTS**

## 1. Rejimni tanlang:
- **Demo Rejim (`/start demo`):** Sintetik ma'lumotlar bilan 3 daqiqalik to'liq amaliy tahlil (Meta 1-5-5 tahlili, Google Coliseum so'rovlari va Telegram voronkasi).
- **Yangi Mijoz (`/start <mijoz>`):** Yangi loyiha uchun `journal/<mijoz>.md` ochish, maqsad va unit-iqtisodiyotni kiritish.

## 2. Dastlabki tekshiruv (avtomatik)
1. Tizim holati: `rules/00-manba.md` va `rules/40-xavfsizlik-va-hisob.md` yuklanadi.
2. Operator xotirasi: `MEMORY.md` tekshiriladi.
3. Asboblar holati: `doctor.py --quick`.

## 3. Keyingi tavsiya etilgan qadamlar:
- **Audit o'tkazish:** `/audit <platforma> <mijoz>`
- **Kreativ sprint:** `/kreativ <mijoz>`
- **Byudjet hisoblash:** `/budget <mijoz>`
- **Haftalik hisobot:** `/hisobot <mijoz>`
