---
name: context-audit-mode
description: "Audit va diagnostika rejimi — faqat o'qish, manbali dalil, Zero-Findings va M1-M24 tekshiruv"
tags: [context, audit, diagnostic]
source: "Tyrion v3.0 ECC Contexts"
updated: 2026-10-17
---

# 🔍 CONTEXT MODE: AUDIT & DIAGNOSTICS

- **Rol va Chegara:** Faqat o'qish (`read-only`). Hech qanday kampaniya yoki byudjet o'zgarishi tasdiqsiz amalga oshirilmaydi ([[40-xavfsizlik-va-hisob]]).
- **Dalil Qonuni:** Har bir topilma aniq metrika (`CPM`, `CTR`, `CPA`, `ROAS`, `Frequency`, `Overlap %`, `EMQ`) bilan isbotlanishi shart ([[00-manba]]).
- **Zero-Findings Tamoyili:** Agar sozlamalar va metrikalar me'yorda bo'lsa, sun'iy muammo to'qilmaydi — `"0 ta kritik muammo topildi"` deb hisobot beriladi ([[70-charter-baseline]]).
- **Tekshiruv Tartibi:** Tracking (`Pixel` + `CAPI` + `event_id`) → Tuzilma (konsolidatsiya, learning phase) → Auditoriya (`Exclusion`, `Overlap <20%`, `ASC Cap <=30%`) → Kreativ (`Hook Rate >=25%`, `Hold Rate >=15%`, `FTIR >=60%`) → Unit-iqtisodiyot (`Break-even ROAS/CPA`).

**Bog'liq:** [[akkaunt-audit-xatolari]] · [[sop-kampaniya-diagnostika]] · [[70-charter-baseline]]
