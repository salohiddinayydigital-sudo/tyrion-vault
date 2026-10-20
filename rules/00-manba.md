---
name: "00-manba"
description: Manba majburiyati — har raqam va fakt manbaga tayanadi; benchmark ko'chirilmaydi; bilinmasa "ma'lumot yo'q"
tags: [rules, manba, ishonch]
source: "claude-ads-main/control-plane (source-ledger, claim-ledger) + vault kontekst qoidalari (2026-09-16)"
updated: 2026-09-16
---

# 📌 00 — MANBA MAJBURIYATI

> **Qoida:** manbasiz fakt yozilmaydi. Raqam to'qish — eng qimmat xato ([[kontekst-xatolari|Poisoning]]).

## Manba darajalari (yuqoridan pastga ishonch)

| # | Manba | Misol | Ishonch |
|---|-------|-------|---------|
| 1 | **Hisobning o'z ma'lumoti** | export, Ads Manager, API/MCP javobi, screenshot | eng yuqori |
| 2 | **Tyrion wiki qaydi** | `wiki/meta-kampaniya-tuzilmalari.md` (frontmatter'ida manba bor) | yuqori |
| 3 | **Dated reference** | `ads/references/meta-audit.md`, `local/meta-playbook-uz.md` | o'rta |
| 4 | **Tashqi manba** | video, maqola, raqobatchi sahifasi | past — **sana + havola shart** |
| 5 | **Model taxmini** | "odatda shunday bo'ladi" | ❌ manba emas |

## Buzilmaydigan qoidalar

1. **Bilinmasa — "ma'lumot yo'q".** Taxmin qilib raqam yozilmaydi, bo'sh joy to'ldirilmaydi.
2. **Yetishmayotgan ma'lumot — `unknown`, xato emas.** Evidence yo'q bo'lsa `fail` ham, `pass` ham emas.
3. **Benchmark ko'chirilmaydi.** Global jadval (CTR/CPC/ROAS normasi) avtomatik qoidaga aylanmaydi —
   avval objective, geografiya, metodologiya, namuna hajmi, conversion lag va akkaunt yoshi tekshiriladi.
4. **O'z tarixi — eng yaxshi benchmark.** Mijoz akkauntining oldingi davri bilan solishtiriladi.
5. **Ziddiyatda yangisi qoladi.** Eski qayd arxivga o'tadi, o'chirilmaydi ([[kontekst-xatolari|Clash]]).
6. **Har natijada manba satri bo'ladi:** `Manba: <fayl/export/API> · <sana>`.

## Amalda

- Tahlil boshida: qaysi ma'lumot **bor**, qaysi biri **yo'q** — ro'yxat qilinadi.
- Har da'vo yonida manbasi; aniq bo'lmasa "taxmin" deb belgilanadi.
- Meta policy bo'yicha tekshirilmagan matn mijozga berilmaydi ([[40-xavfsizlik-va-hisob]]).

**Bog'liq:** [[rules/README|Qoidalar indeksi]] · [[10-til-va-uslub]] · [[kontekst-xatolari]] · [[haftalik-audit]]
