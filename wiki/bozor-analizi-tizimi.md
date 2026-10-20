---
name: bozor-analizi-tizimi
description: "Bozor va raqobat tahlili tizimi — Ads Library g'olib pattern oqimi, ochiq manbalar, 10 tamoyilli fikrlash intizomi va RAQOBAT.md artefakti"
tags: [bozor, raqobat, tadqiqot, tahlil]
source: "ads/references/thinking-framework.md + meta-ads-library-tadqiqot + sop-raqobat-tahlili + ads/references/meta-ai-stack.md"
updated: 2026-09-20
---

# Bozor analizi tizimi

> Bog'lanishlar: [[sop-raqobat-tahlili]] · [[meta-ads-library-tadqiqot]] · [[bozor-trend-kreativi]] · [[pozitsiyalash-dunford]] · [[cjm-mijoz-yoli]]

## 1. Fikrlash intizomi (10 tamoyil — qaysi birini tashlab ketdingiz?)

| # | Tamoyil | Ads ishida |
|---|---|---|
| 1 | **OBSERVE (tashqi)** | Avval ma'lumot: eksport, Ads Library skrinshot, landing (mobil, to'lov manbasi bilan), SERP |
| 2 | **OBSERVE (o'z fikri)** | O'z taxminini tekshir: B2B evristikasini mahalliy xizmatga qo'llayapsanmi? |
| 3 | **LISTEN** | Briefni **so'zma-so'z** o'qi; platforma rasmiy yo'riqnomasini o'qi; hamjamiyat natijalarini tekshir |
| 4 | **THINK** | Unit iqtisodni **qo'lda** hisobla; voronkani qur; cheklovlarni joriy holatdan ol |
| 5 | **CONNECT (lateral)** | Boshqa nishadagi patternni ko'chir; kreativ ↔ offer ↔ kanal bog'lanishi |
| 6 | **CONNECT (tizim)** | Kim nimani qiladi, qaysi artefakt qayerga tushadi ([[sop-xarita]]) |
| 7 | **FEEL** | Raqam soviq — mijozning qo'rquvi/umidi matnda aks etishi kerak |
| 8 | **ACCEPT** | "Bilmayman" — legitim javob. **Zero findings — qabul qilinadigan natija** |
| 9 | **CREATE** | Faqat dalildan keyin yechim generatsiyasi |
| 10 | **GROW** | Har ishdan saboq → keyingi iteratsiya |

🟢 Manba: `ads/references/thinking-framework.md` (claude-ads canonical)
**Test:** qaysi tamoyilni o'tkazib yubordingiz — ish o'sha yerda zaif.

## 2. Manbalar (faqat ochiq)

| Manba | Nima olinadi |
|---|---|
| **Meta Ads Library** | Faol e'lonlar, **qancha vaqtdan beri ishlaydi**, format/hook/offer patternlari |
| **Raqobatchi sayti** | Narx sahifasi, offer tuzilishi, CTA kanali, ishonch signallari |
| **Mijoz sharhlari** | Google Maps, Instagram izohlar, Telegram guruhlar — **haqiqiy og'riq va e'tirozlar** |
| **Mijoz suhbati (CustDev)** | 5-7 suhbat: oldin/keyin, raqam bilan |
| **Platforma rasmiy hujjati** | Architecture/feature da'volari (vendor raqami — faqat labeled context) |

## 3. Ads Library oqimi (g'olib pattern)

1. Nisha bo'yicha qidir → **faol** e'lonlarni ajrat.
2. **Uzoq ishlagan** e'lon = g'olib proksi (30-60 kun; oddiy test o'lik bo'lardi) 🟡
3. Har g'olibdan ajrat: **hook (0-3s) · angle · offer · format · destination**.
4. Takrorlanadigan patternlarni jadvalga yoz — bu bozorning "nima ishlayapti" xaritasi.
5. **Nusxa ko'chirma** — pattern + o'z mijozning noyob mexanizmi = yangi angle ([[unique-mexanizm]]).
6. Watermark/sharing muammosi bo'lsa: ruxsatli download yo'li ([[meta-ads-library-tadqiqot]]).

**Cheklov:** Ads Library — da'vo emas, kuzatuv. "Ishlayapti" degan xulosa faqat raqam bilan.

## 4. Tahlil artefakti (`RAQOBAT.md`)

| Bo'lim | Mazmun |
|---|---|
| Solishtirish jadvali | Raqobatchi · kimga · asosiy va'da · narx modeli · kuchli/zaif tomoni · shikoyatlar |
| Bo'sh joylar | Qaysi segment e'tiborsiz · qaysi og'riqni hech kim aytmaydi · qaysi formatda hech kim ishlamaydi |
| Farqlanish o'qi | **Bitta** (arzon+tez+sifatli birga bo'lmaydi) + sababi |
| 3 asosiy xabar | Mijoz tilida, bitta jumla |

Mezon: farqlanish **isbotlanadigan** va raqobatchi **bir haftada nusxa ko'chira olmaydigan** bo'lsin.

## 5. Mahalliy (UZ) tuzatishlar

- Raqamni **faqat mijoz hisobidan** ol; global benchmark faqat tartib ko'rsatadi ([[voronka-metrikalari]])
- Telegram ustuvorligini tekshir: raqobatchi CTA'si Telegrammi yoki forma?
- Til segmentlari alohida tahlil (o'zbek lotin / kirill / rus)
- Mavsumiylik: Ramazon, Navro'z, 1-sentabr, dekabr, to'y mavsumi

## 6. Tekshiruv

- [ ] Har da'vo manbali yoki "taxminiy" deb belgilangan ([[dalil-tasnifi]])
- [ ] Ads Library kuzatuvi ≠ xulosa (faqat raqam bilan xulosa)
- [ ] Vendor da'volari (Meta o'z natijasi) 🔴 REKLAMA deb belgilangan
- [ ] "Zero findings" — qabul qilinadigan natija (sun'iy muammo to'qilmaydi)

## Manba

- `claude-ads-main/ads/references/thinking-framework.md`
- `claude-ads-main/ads/references/meta-ai-stack.md` (vendor da'vo siyosati)
- [[meta-ads-library-tadqiqot]] · [[sop-raqobat-tahlili]]
