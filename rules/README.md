---
name: rules-index
description: Tyrion qoidalari indeksi — qaysi qoida qachon yuklanadi (boot'da butun papka o'qilmaydi)
tags: [rules, index, qoida]
source: "ECC naqshi (AGENTS.md + rules/) asosida, Tyrion uchun (2026-09-16)"
updated: 2026-10-17
---

# 📏 TYRION QOIDALARI

> **Qanday ishlaydi:** bu papka **kanonik manba**. Har fayl — bitta mavzu, qisqa.
> Boot'da hammasi o'qilmaydi — [[AGENTS.md]] jadvali bo'yicha faqat keraklisi yuklanadi.
> Qoida o'zgarsa — **faqat shu yerda** o'zgaradi, nusxalar (memory.md, bot SOUL.md) havola qiladi.

| Qoida | Nima haqida | Qachon yuklanadi |
|-------|-------------|------------------|
| [[00-manba]] | Manba majburiyati — raqam to'qilmaydi, benchmark ko'chirilmaydi | Har qanday tahlil, audit, hisobot oldidan |
| [[10-til-va-uslub]] | O'zbekcha javob, atamalar, format, wikilink | Har javobdan oldin |
| [[20-token-gigiyena]] | Graf avval, kontekst 60%, batching | Uzoq sessiya, katta vazifa |
| [[30-ozbekiston-konteksti]] | Telegram voronka, 3 til, to'lov, mavsum | Mijoz ishi, kreativ, offer |
| [[40-xavfsizlik-va-hisob]] | Read-only default, draft+tasdiq, tokenlar, mijoz ma'lumoti | Hisob o'zgarishi, tracking, mijoz fayli |
| [[50-topshirish-dod]] | Topshirish darvozasi — DoD, checklist, verifier | Ish tugagach, natija berganda |
| [[60-loyiha-papkasi]] | Har loyiha `clients/<slug>/` da; ish shu papkada, yangi sessiya shu yerdan davom | Yangi loyiha boshlanganda, sessiya resume'da |
| [[70-charter-baseline]] | 36 agent uchun Prompt Defense Baseline, Zero-Findings va rol chegaralari | Sub-agent (worker) ishga tushganda va auditda |

## Buzilmaydigan 3 ta

1. **Manbasiz fakt yo'q** — bilmasa "ma'lumot yo'q" ([[00-manba]])
2. **Hisob o'zgarishi tasdiqsiz yo'q** — draft + tasdiq ([[40-xavfsizlik-va-hisob]])
3. **Natija fayl bo'ladi** — chatda qolmaydi, `outputs/` ga yoziladi ([[50-topshirish-dod]])

