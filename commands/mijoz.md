---
name: mijoz
description: "Yangi mijoz loyihasi uchun 1 buyruqda tayyor BRIEF, 4-qatlamli Meta Auditoriya xaritasi, 3x3 Kreativ Matritsa va Tracking cheklistini ochish"
---

# `/mijoz` — Mijoz Ish Maydoni (Client Workspace Scaffolder)

Foydalanuvchi `/mijoz [nomi]` deb chaqirganda:

1. **Avtomatik Scaffold (`0 token`):**
   ```bash
   python3 tools/client-workspace.py new --client "<nom>" --niche <nisha> --budget <oylik_usd> --aov <ortacha_chek> --margin-pct <marja_foizi> --geo <tashkent|regions|uzbekistan>
   ```
2. **Yaratiladigan Artefaktlar (`clients/<slug>/`):**
   - `BRIEF.md` — Break-even ROAS, Target CPA va 70/20/10 byudjet taqsimoti.
   - `AUDIENCE-MAP.md` — `meta-audience.py` tomonidan hisoblangan 4-qatlamli `TOF/MOF/BOF` + `Exclusions` + `Solventnost` xaritasi.
   - `CREATIVE-MATRIX.md` — `creative-matrix.py` tomonidan tuzilgan 3x3 Andromeda 2 kreativ sinov matritsasi.
   - `TRACKING-CHECKLIST.md` — Pixel + CAPI + `event_id` + Telegram Bot + AmoCRM tekshiruv ro'yxati.
   - `journal.md` — Kampaniya qarorlari jurnali.
