---
name: skill-shablon
description: "Yangi Tyrion skill yaratish andozasi (ECC standarti). Use when creating or refactoring a marketing, platform, or orchestration skill."
tags: [template, skill, ecc, standart]
source: "raw/2026-09-16-ecc-naqshlar-tahlili.md §3"
updated: 2026-10-17
attached_agents: []
standalone: true
---

# <Skill Sarlavhasi>

<Bir xatboshi: skill nima qiladi va qanday marketing/biznes natija beradi.>

## When to Activate

- Foydalanuvchi `<vazifa 1>` so'raganda
- `<platforma yoki metrika>` auditi yoki optimizatsiyasi kerak bo'lganda
- `<muammo>` diagnostika qilinayotganda

## Core Concepts

1. **Manba intizomi:** Barcha raqamlar va tavsiyalar [[00-manba]] qoidasiga bo'ysunadi.
2. **Xavfsizlik chegarasi:** Hisob o'zgarishlari [[40-xavfsizlik-va-hisob]] (6 darvoza) orqali o'tadi.
3. **Mahalliy moslashuv:** O'zbekiston bozori uchun [[30-ozbekiston-konteksti]] hisobga olinadi.

## Workflow

1. **Step 0 — Kontekst va Dalil Yig'ish:** Mavjud eksport, metrika, sanalar va maqsadni aniqlashtiring. Yetishmagan ma'lumotni so'rang (`unknown`).
2. **Step 1 — Diagnostika va Matematika:** `tools/calculator.py` yoki platforma qoidalari asosida hisoblang.
3. **Step 2 — Strategiya / Tavsiya Ishlab Chiqish:** Har bir tavsiyada dalil, mexanizm, kutilayotgan ta'sir va `Rollback` qadami bo'lsin.
4. **Step 3 — Sifat va Xavfsizlik Tekshiruvi:** `tools/spend-guard.py` va [[50-topshirish-dod]] bo'yicha tekshiring.

## Anti-Patterns (Nima Qilmaslik Kerak)

- **FAIL: WRONG** — Mijozning break-even CPA ko'rsatkichini bilmasdan "CPA $10 bo'lishi kerak" deb global benchmarkni qoida qilish.
- **PASS: CORRECT** — Avval marja va AOV asosida break-even CPA'ni hisoblash (`calculator.py breakeven`), keyin akkauntning o'z tarixi bilan solishtirish.

- **FAIL: WRONG** — O'rganish fazasidagi (learning phase) ad set byudjetini bir kunda +100% ga oshirish.
- **PASS: CORRECT** — Byudjetni 48 soatda maksimal +20% ga oshirish (`spend-guard.py budget`) yoki g'olib ad setni duplikatsiya qilish.

## Best Practices

1. Har bir topilma aniq `control_id` va manbaga bog'lansin.
2. Og'ir jadvallar va ma'lumotnomalarni `references/` papkasiga chiqaring (`SKILL.md` ≤ 300 qator).
3. Yakuniy natijani har doim `outputs/` ichiga fayl sifatida yozing.

## Related Skills

- [[sop-xarita]] · [[skill-router]] · [[70-charter-baseline]]
