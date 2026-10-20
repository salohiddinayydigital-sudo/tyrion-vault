---
name: eksport
description: "Meta Ads, Google Ads yoki Telegram Ads CSV/JSON eksport fayllarini 0 tokenda tahlil qilish, Kill/Keep/Scale va Meta 'Breakdown Effect' tuzog'ini aniqlash"
---

# `/eksport` — Ad Manager CSV/JSON Eksport va Breakdown Effect Tahlilchisi

Foydalanuvchi `/eksport [fayl_yoli]` deb chaqirganda:

1. **Eksport Tahlili (`0 token`):**
   ```bash
   python3 tools/ad-export-analyzer.py analyze --file "<csv_yoki_json_fayl>" --target-cpa <target_cpa> --breakeven-roas <breakeven_roas>
   ```
2. **Meta "Breakdown Effect" Tekshiruvi:**
   Agar foydalanuvchi qaysidir placement (masalan, `Instagram Reels` vs `Facebook Feed`) yoki yosh segmentini "o'rtacha CPA qimmat ekan" deb o'chirmoqchi bo'lsa, darhol tekshiring:
   ```bash
   python3 tools/ad-export-analyzer.py breakdown-effect --seg-a-name "<Placement_A>" --seg-a-spend <Spend_A> --seg-a-conv <Conv_A> --seg-b-name "<Placement_B>" --seg-b-spend <Spend_B> --seg-b-conv <Conv_B>
   ```
3. **Natija:** Havoga sovurilgan byudjet (`Wasted Spend`), `Learning Limited` holatidagi Ad Set'lar va aniq `Kill / Keep / Scale` jadvalini taqdim eting.
