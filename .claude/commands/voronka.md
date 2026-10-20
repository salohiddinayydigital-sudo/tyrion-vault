---
name: voronka
description: "Meta/Telegram/Google Ads dan Telegram Bot, ManyChat va AmoCRM gacha to'liq sotuv voronkasini va Offer'ni loyihalash"
---

# `/voronka` — Sotuv Voronkasi va Offer Arxitektori

Foydalanuvchi `/voronka [nisha yoki mahsulot]` deb chaqirganda quyidagi ketma-ketlikni bajaring:

1. **Kontekst va Playbook yuklash:** `contexts/launch-mode.md`, `contexts/uzbekistan-market.md` va `playbooks/telegram-bot-amocrm-voronka.md` (hamda nishaga mos `playbooks/nisha-*.md`) fayllarini o'qing.
2. **Unit-Iqtisodiyot va Break-Even:** `python3 tools/calculator.py breakeven` va `telegram-funnel` orqali har bir voronka bosqichining (`Click -> Bot /start -> Share Contact -> Qualified Lead -> Sale`) minimal konversiya normativlarini hisoblang.
3. **4 Bosqichli Voronka Chizmasi:**
   - **Trafik (TOF/BOF):** Meta Reels Ads / Telegram Ads (`<=160` belgi) / Google Search Coliseum.
   - **Ushlab olish (Capture):** Instagram izohda kalit so'z (`ManyChat`) yoki to'g'ridan-to'g'ri `t.me/bot?start=utm_payload` + 2 ta saralovchi savol (Solventnost filtri).
   - **Qiymat va Ishonch (Lead Magnet):** Mijoz og'rig'ini yechuvchi PDF/Video/Diagnostika/Kalkulyator (`[[lead-magnet-turlari]]`).
   - **Sotuv (CRM):** `Share Contact` -> `AmoCRM / Bitrix24` -> **15 daqiqa ichida qo'ng'iroq** + Payme/Click/Uzum Nasiya taklifi.
4. **Natija:** To'liq voronka sxemasi, bot skripti savollari va KPI jadvalini `outputs/<mijoz>/<sana>-voronka.md` ga yozing.
