---
name: scale
description: "Meta, Google va Telegram kampaniyalarida Kill / Keep / Scale qarorini qabul qilish, Learning Phase himoyasi va 20% byudjet scaling"
---

# `/scale` — Kill / Keep / Scale va Yuqori Byudjet Boshqaruvi

Foydalanuvchi `/scale` deb chaqirganda:

1. **Kontekst:** `contexts/scale-mode.md`, `wiki/meta-katta-byudjet-scaling.md` va `wiki/scaling-cheklovlari.md` ga tayaning.
2. **Diagnostika va Charchoq Tekshiruvi:**
   - `python3 tools/meta-audience.py diagnose --cpm <X> --ctr <Y> --lp-cvr <Z> --frequency <F> --ftir <FTIR>`
   - `python3 tools/meta-audience.py saturation --audience-size <N> --daily-budget <B>`
   - `python3 tools/spend-guard.py budget --current <eski> --proposed <yangi> --max-cap <limit>`
3. **Qaror Matritsasi:**
   - **KILL (To'xtatish):** `Sarf >= 1.5x–2.0x Target CPA` va `0` konversiya, yoki 7 kunlik `ROAS < Break-even ROAS`.
   - **KEEP (Ushlab turish):** `CPA <= Target CPA`, `Frequency < 2.5`, `FTIR >= 60%`.
   - **SCALE (Kattalashtirish):**
     - **Vertikal:** Har 48–72 soatda byudjetni ko'pi bilan **+20%** oshirish (Learning Phase reset bo'lmasligi uchun).
     - **Gorizontal:** G'olib kreativning 3 ta yangi Hook variatsiyasini (`More -> Better -> New`) yangi auditoriya qatlamiga (Broad / 1% Value LAL) klonlash.
