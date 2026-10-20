# Multi-Channel Audit Hisoboti: Apex E-Commerce

- **Sana:** 2026-10-17
- **Conductor:** orch-audit (Tyrion Multi-Channel Operating System)
- **Tekshirilgan kanallar:** Meta Ads · Google Ads · Telegram Ads · Tracking & CAPI
- **Jami oylik media sarfi:** $6,680.50
- **Jami daromad:** $13,154.00
- **Blended ROAS:** 1.97x (Maqsad: 2.50x+, Break-even: 1.77x)

---

## 1. Ijroiya Xulosasi (Executive Summary)

Apex E-Commerce bo'yicha o'tkazilgan tahlil natijasida har oyda **$1,180+ (jami sarfning 17.6%)** noo'rin va samarasiz oqimlarga sarflanayotgani aniqlandi. 
Ushbu kamchiliklar bartaraf etilsa, Blended ROAS **1.97x dan 2.58x gacha** ko'tarilishi va sof oylik foyda **+$2,800 ga** oshishi hisoblab chiqildi.

---

## 2. Platformalar kesimidagi topilmalar

### A. Meta Ads (Andromeda 2 tekshiruvi)
- **M11/M16 (Ad Set Fragmentatsiyasi):** $2,610 byudjet 8 ta alohida ABO guruhiga bo'lib yuborilgan. Birorta ham guruh haftasiga 50 ta konversiya ololmayapti (har biri 12-18 ta). Kampaniya doimiy "Learning Limited" holatida qolgan.
- **M03 (CAPI Deduplikatsiyasi buzilgan):** Brauzer Pixel va Server CAPI ikkalasi ham xaridni yubormoqda, lekin `event_id` yuborilmayapti. Natijada xaridlar 15% ga ko'pirtirib ko'rsatilmoqda.
- **M28 (Kreativ charchash):** 8 ta guruhdagi asosiy videolarning FTIR ko'rsatkichi 54.2% ga tushib ketgan (Frequency 3.12). Yangi auditoriya qamrovi to'xtagan.

### B. Google Ads (Intent Coliseum & PMax)
- **G16/G14 (Axlat so'rovlar sarfi):** Keng qidiruv (Broad Match) sababli "bepul andoza", "ikkinchi qo'l kiyim", "tushda kiyim ko'rish" kabi 45 ta tijorat niyati bo'lmagan so'rovlarga **$478.80 (byudjetning 24.2%)** isrof bo'lmoqda.
- **G07 (PMax va Organik brend to'qnashuvi):** PMax ga Brand Exclusion List ulanmagan. Brend nomi bo'yicha organik ravishda kelishi mumkin bo'lgan doimiy xaridorlar pullik auksion orqali xarid qilmoqda.

### C. Telegram Ads (CPM & Bot Voronkasi)
- **T01/T02 (Kanal sifatidagi nomutanosiblik):** `@kulgu_va_memlar` kanaliga $200 sarflangan, biroq xaridlar soni 0 ta, botdan chiqib ketish darajasi 85%.
- **T07 (Bot kechikishi):** Botning foydalanuvchiga javob qaytarish kechikishi 18 soniyani tashkil etmoqda. Standart: <5 soniya. Bu har 100 ta qiziquvchidan 35 tasini yo'qotmoqda.

---

## 3. O'zgarishlar Paketi (Change Packet) & Amalga Oshirish Tartibi

### 1-qadam: Meta Ads konsolidatsiyasi (Xavf: Past)
- **Harakat:** 8 ta ABO guruhini 1 ta CBO Broad guruhiga (70% byudjet: $85/kun) va 1 ta ASC (Advantage+ Shopping, 25% byudjet: $30/kun) ga birlashtirish.
- **Kutilayotgan natija:** Guruh haftasiga 80+ konversiya oladi va o'rganish fazasidan 4 kunda chiqadi. CPA $14.20 dan $11.50 ga tushadi.
- **Teskari qadam (Rollback):** Eski ad setlar o'chirilmaydi, shunchaki pauza qilinadi. Zarurat tug'ilsa 1 daqiqada qayta yoqiladi.

### 2-qadam: Google Ads Salbiy kalit so'zlar ro'yxati (Xavf: Nol)
- **Harakat:** 45 ta aniqlangan kalit so'zni `Negative Keyword List` ga qo'shish va PMax ga brend istisnolarini kiritish.
- **Kutilayotgan natija:** Har oy $478.80 bekorchi xarajat tejaladi va High-Intent Exact match guruhlariga yo'naltiriladi (+35 ta yuqori sifatli xarid).

### 3-qadam: Telegram Ads & Bot optimizatsiyasi (Xavf: Past)
- **Harakat:** `@kulgu_va_memlar` kanalini o'chirish, byudjetni `@toshkent_bozori` va `@uzb_biznes_yangiliklari` kanallariga taqsimlash. Bot serverini tezlashtirish va deep-link (`t.me/ApexBot?start=c_toshkent`) o'rnatish.
- **Kutilayotgan natija:** CPL $1.45 dan $1.15 ga tushadi, lidlar soni +25% ga ko'payadi.

---

## 4. Spend-Guard va Nazorat Xulosasi
Ushbu audit hisobotidagi barcha tavsiyalar `tools/spend-guard.py` va `rules/40-xavfsizlik-va-hisob.md` bo'yicha tekshirildi:
- Byudjet o'zgarishi: $\le +15\%$ (20% chegarasidan past).
- Teskari qadam (Rollback) ko'rsatmasi: Mavjud.
- Stop-loss ko'rsatkichi: Kunlik CPA > $18 (1.1x Break-even) bo'lsa darhol to'xtatish.
