# Loyiha Jurnali: Apex E-Commerce

## 2026-10-15 — Boshlang'ich holat auditi
- **Conductor:** audit-orch ishga tushirildi.
- **Topilmalar:**
  - Meta: 8 ta ad set mavjud, haftalik konversiyalar 1 ad set uchun 12-18 ta atrofida (o'rganish fazasi yopilmagan). Pixel va CAPI ikkalasi ham o'rnatilgan, lekin `event_id` uzatilmagani sababli hisobotlarda xaridlar ~15% ortiqcha ko'rinmoqda.
  - Google: Broad match "erkaklar kiyimi" kampaniyasida "bepul andoza", "ikkinchi qo'l kiyim", "qanday tikish kerak" kabi so'rovlarga $480 sarflangan.
  - Telegram: 3 ta kanaldagi CPM €3.20, botga kirish yaxshi, lekin savollar botda to'xtab qolgan.

## 2026-10-16 — Strategik qarorlar
- **Qaror 1:** Meta da 8 ta ad setni 1 ta CBO Broad (70% byudjet) va 1 ta Advantage+ Shopping (25% byudjet) ga birlashtirish.
- **Qaror 2:** Google Ads ga hisoblangan salbiy kalit so'zlar ro'yxatini yuklash va $480 tejamkorlikni "erkaklar kostyumi sotib olish toshkent" exact match guruhiga yo'naltirish.
- **Qaror 3:** Telegram botida avto-javob tezligini 3 soniyaga tushirish va deep-link parametrlarini sozlash.
- **Qaror 4:** Barcha o'zgarishlar `tools/spend-guard.py` tekshiruvidan o'tdi (xavf darajasi: past).
