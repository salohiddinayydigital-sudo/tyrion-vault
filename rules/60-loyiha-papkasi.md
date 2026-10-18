---
name: "60-loyiha-papkasi"
description: Har bir loyiha Tyriondan tashqarida, D: diskida alohida papkada ochiladi; loyiha ishi faqat shu papkada yuritiladi; yangi sessiya shu papkadan davom etadi
tags: [rules, loyiha, papka, izolyatsiya, sessiya]
source: "Foydalanuvchi qarori (2026-09-22): loyihalar Tyriondan tashqarida D: da ochilsin, token maximal tejasin"
updated: 2026-09-22
---

# 📁 60 — LOYIHA PAPKASI (IZOLYATSIYA)

> **Bir qator:** Tyrion — **miya** (bilim + qoida). Loyiha — **alohida papka** `D:` da.
> Yangi loyiha boshlansa, ish papkasi Tyrion ichida ochilmaydi. Ish tugamaguncha shu papkada yuriladi.

## Buzilmaydigan qoida

1. **Har loyiha — o'z papkasi.** Standart ildiz: `clients/` · loyiha: `clients/<slug>/`
   (slug — kichik lotin, bo'shliqsiz, `-` bilan: `saunahub-uz`, `boost-vs-ads`).
   Boshqa joy kerak bo'lsa — foydalanuvchi aytadi, qoida shunga moslashadi.
2. **Loyiha ishi Tyrion ichida yozilmaydi.** Brief, qoralama, render, xom fayl, mijoz ma'lumoti —
   hammasi loyiha papkasida. Tyrion'ga faqat `LOG.md` qatori va katalog/INDEX yangilanishi tushadi.
3. **Nusxa emas, havola.** Loyiha papkasiga Tyrion qoidalari/bilimi ko'chirilmaydi — kerak bo'lsa
   [[rules/README|qoida]] yoki [[INDEX|bilim]] nomi tilga olinadi ([[20-token-gigiyena]]).

## Papka tuzilishi (minimal)

```
clients/<slug>/
├── BRIEF.md        # maqsad, mijoz, deadline, muvaffaqiyat mezoni
├── journal.md      # qaror + sabab (xronologik)
├── assets/         # kirish fayllari (rasm/video/matn)
├── outputs/        # yakuniy natijalar (bitta konduktor yozadi)
└── MANIFEST.md     # fayl → manba/litsenziya/hash
```

Og'ir ish uchun ixtisos asbob ishlatilsa (`tools/video-run.py` kabi) — **uning standart tuzilishi
ustun** ([[tools/README]]).

## Sessiya boshlanishi (resume)

1. **Faol loyiha ko'rsatkichi:** `local/active-project.md` — ichida bitta qator: loyiha absolyut yo'li.
2. Yangi sessiya boot'ida ([[AGENTS.md]] §1) ko'rsatkich mavjud bo'lsa — **ish shu papkadan davom etadi**:
   kontekst sifatida `BRIEF.md` + `journal.md` oxirgi yozuvi o'qiladi, keyin davom.
3. Ko'rsatkich yo'q / tugallangan bo'lsa — Tyrion o'zida qoladi, yangi loyiha so'ralganda papka ochiladi.
4. Loyiha tugagach — ko'rsatkich `_archive/` ga (hech narsa o'chirilmaydi), `LOG.md` ga yakuniy qator.

## Token gigiyenasi (nega bu qoidalar)

- Loyiha konteksti Tyrion bilim bazasiga aralashmaydi → boot har sessiyada yengil qoladi ([[20-token-gigiyena]]).
- Faqat loyihaga tegishli 2–3 fayl o'qiladi (`BRIEF.md`, `journal.md`, oxirgi `outputs/`), butun papka emas.
- Yangi sessiya — qayta tushuntirish yo'q: holat `journal.md` da yozib borilgan bo'ladi.

## Natija darvozasi

Loyiha yopilishidan oldin [[50-topshirish-dod]] checklisti: `outputs/` da fayl bor, manba satri bor,
`LOG.md`ga bitta qator yozilgan.

**Bog'liq:** [[rules/README|Qoidalar indeksi]] · [[20-token-gigiyena]] · [[50-topshirish-dod]] · [[CLAUDE.md|router]]
