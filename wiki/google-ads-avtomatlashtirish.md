---
name: google-ads-avtomatlashtirish
description: "Google Ads avtomatlashtirish shartlari — kampaniya turi tanlash, tROAS minimal konversiya hajmi, enhanced conversions (SHA256) va Consent Mode v2"
tags: [google-ads, avtomatlashtirish, konversiya, tracking]
source: "claude-ads-main/local/raw/claudes-bilim/marketolog/KNOWLEDGE.md (§7)"
updated: 2026-09-20
---

# Google Ads — avtomatlashtirish va konversiya kuzatuvi

> Bog'lanishlar: [[google-ads-search-kampaniya-qollanma]] · [[unit-iqtisodiyot-formulalari]] · [[blended-roas-net-cash]] · [[meta-ads-sozlamalari]]

## Kampaniya turi — qachon

| Tur | Qachon | Shart |
|---|---|---|
| **Search** | Talab allaqachon bor, odam qidiryapti | Kalit so'zda qidiruv hajmi bor |
| **Performance Max** | Butun inventarga kirish, avtomatlashtirish | Konversiya kuzatuvi to'g'ri, kreativ aktivlar bor |
| **Shopping** | E-commerce, mahsulot fidi | Merchant Center sozlangan |
| **Display / Demand Gen** | Talab yaratish, retargeting | Arzon reach; konversiya kutma |
| **Video (YouTube)** | Ko'rgazmali mahsulot, ta'lim | Video aktiv bor |

> **Talab yo'q mahsulotga Search kampaniya — pul yo'qotish.** Avval Meta bilan talabni yarat.

## Target ROAS — minimal konversiya hajmi

tROAS'ni **yoqishdan oldin** kerakli hajm:

| Kampaniya turi | Minimal talab |
|---|---|
| Search va Shopping | Oxirgi 30 kunda **15 ta** konversiya |
| Display | Oxirgi 30 kunda barcha kampaniyalar bo'ylab **15 ta** (qiymati bilan) |
| App | Kuniga **10 ta** (yoki 30 kunda 300) |
| Demand Gen | Oxirgi 35 kunda **50 ta** (10 tasi oxirgi 7 kunda) |
| Video Action | Oxirgi 30 kunda **30 ta** |
| Hotel | Haftasiga **50 ta** |
| Travel | Oxirgi 7 kunda **50 ta** |

Google qiymatlarni **4 hafta yoki 3 konversiya sikli** (uzuni) davomida yig'ishni tavsiya qiladi.

**Kichik biznes uchun xulosa:** oyiga 15 ta konversiya bo'lmasa — tROAS **yoqma**.
Maximize Clicks yoki Manual CPC bilan boshla, hajm to'plangach o't.

🟢 Manba: https://support.google.com/google-ads/answer/6268637

## Enhanced conversions

Hashlangan birinchi tomon ma'lumoti bilan o'lchov aniqligini oshiradi.
Qabul qilinadigan: email, ism, uy manzili, telefon → **SHA256** bilan hashlanadi, uzatishdan oldin.
Ikki turi: **web** (saytdagi konversiya) va **leads** (lead formasi + offline konversiya importi).

## Consent Mode v2

To'rt signal: `ad_storage`, `analytics_storage`, `ad_user_data`, `ad_personalization` (oxirgi ikkitasi v2 da).
- **Basic:** teglar banner bilan muloqotgacha yuklanmaydi.
- **Advanced:** teglar darhol yuklanadi, rozilik yo'qda cookie-siz ping yuboradi → modellashtirish imkoni.

2024-martdan EEA trafigida personalizatsiya va Customer Match uchun `ad_user_data` + `ad_personalization` **granted** bo'lishi shart.

> **O'zbekistonda EEA talablari amal qilmaydi**, lekin mijoz Yevropa bozoriga chiqsa — blokerga aylanadi. Xalqaro loyihada oldindan hisobga ol.

🟢 Manba: https://support.google.com/google-ads/answer/13695607

## Manba

- `claude-ads-main/local/raw/claudes-bilim/marketolog/KNOWLEDGE.md` §7
