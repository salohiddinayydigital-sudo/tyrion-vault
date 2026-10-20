---
name: context-launch-mode
description: "Kampaniya ishga tushirish rejimi — 1-5-5 Sandbox, Spend-Guard darvozasi va Pixel/CAPI preflight"
tags: [context, launch, sandbox]
source: "Tyrion v5.0 ECC Contexts"
updated: 2026-10-17
---

# 🚀 CONTEXT MODE: CAMPAIGN LAUNCH (24-HOUR PROTOCOL)

- **Asosiy Tuzilma:** Meta Ads uchun `1-5-5 ABO Sandbox` (1 Campaign → 3–5 Ad Set → har birida 3–5 farqli burchakdagi kreativ), Google Ads uchun `Search Coliseum` (Exact/Phrase yuqori niyat + Negative Keywords).
- **Ishga Tushirish Darvozasi (Launch Gate):**
  1. Break-even CPA va Target ROAS `tools/calculator.py` orqali hisoblangan.
  2. `Pixel` + `CAPI` (`event_id` deduplikatsiyasi) yoki Telegram Bot `?start=utm` zanjiri tekshirilgan.
  3. 4 qatlamli Exclusion matritsasi (`tools/meta-audience.py architect`) o'rnatilgan.
  4. Spend-Guard (`tools/spend-guard.py`) stop-loss va kunlik limit (`max_daily_cap`) tasdiqlangan.
  5. Dastlabki 72 soat (3–4 kun) learning phase davomida ad set tahrirlanmaydi ([[learning-phase-qoidalari]]).

**Bog'liq:** [[meta-kampaniya-tuzilmalari]] · [[sop-kampaniya-rejalash]] · [[40-xavfsizlik-va-hisob]]
