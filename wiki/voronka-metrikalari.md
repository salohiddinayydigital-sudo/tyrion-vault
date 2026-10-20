---
name: voronka-metrikalari
description: "Voronka bosqichlari va metrikalari — TOFU/MOFU/BOFU, AARRR (Pirate Metrics), diagnostika qoidasi va benchmarklarni ehtiyotkorlik bilan ishlatish"
tags: [voronka, metrika, strategiya]
source: "claude-ads-main/local/raw/claudes-bilim/marketolog/KNOWLEDGE.md (§5 Voronka)"
updated: 2026-09-20
---

# Voronka metrikalari — bosqichlar va diagnostika

> Bog'lanishlar: [[funnel-filtr-qoidalari]] · [[survey-funnel]] · [[lead-magnet-turlari]] · [[sotuv-va-retention]]

## TOFU / MOFU / BOFU

| Bosqich | Mijoz holati | Kontent | Asosiy metrika | Kanal |
|---|---|---|---|---|
| **TOFU** | Muammoni endi sezyapti | Ta'lim, Reels, maqola | Reach, CTR, 3s view | Instagram, TikTok, YouTube, SEO |
| **MOFU** | Yechim qidiryapti | Keys, taqqoslash, lead magnit | Lead soni, CPL, ro'yxatga qo'shilish | Telegram kanal, email, retargeting |
| **BOFU** | Sotuvchi tanlayapti | Narx, kafolat, demo, sharh | Lead→mijoz %, CPA, sotuv sikli | Suhbat, sayt, DM |

## AARRR (Pirate Metrics — Dave McClure)

| Bosqich | Savol | Metrikalar |
|---|---|---|
| Acquisition | Qanday topishyapti? | CAC, CPA, manba bo'yicha konversiya |
| Activation | Birinchi qiymatga yetdimi? | Activation %, birinchi qiymatgacha vaqt |
| Retention | Qaytishyaptimi? | D1/D7/D30, churn |
| Referral | Tavsiya qilishyaptimi? | Tavsiya %, viral koeffitsiyent |
| Revenue | To'layaptimi? | Konversiya %, ARPU, LTV |

## Diagnostika qoidasi

- **Eng katta pasayish qayerda bo'lsa — o'sha yerni tuzat.** Bir vaqtda ikkita bosqichni tuzatish — resursni sochish.
- Bo'g'iqni **foiz pasayishi** bilan emas, **yo'qotilgan mijoz soni** bilan o'lcha:
  2% → 3% o'sish 50 000 trafikda 10 ta lead beradi; 500 trafikda 0 ta.
- Trafik yo'q holda konversiyani optimallashtirish — eng keng tarqalgan strategik xato.

## Benchmarklar — ehtiyotkorlik bilan

**Landing page (Unbounce, Q4 2024):** 41 000 sahifa, 464 mln tashrif, 57 mln konversiya — **median** berilgan (o'rtacha emas).
Barcha sohalar mediani **6.6%** · "yaxshi" = 10%+ (~75-persentil) · eng yaxshi 10% = 11.45%+.
Sohalar farqi 3.2 barobargacha: Entertainment 12.3% … SaaS 3.8% → **sohasiz benchmark keltirish — xato.**

**Google Ads (WordStream, 2025-04 – 2026-03):** 13 474 AQSh kampaniyasi, **arifmetik o'rtacha**:
CTR 6.64% · CPC $5.42 · konversiya 8.18% · CPL $66.69.

> ⚠️ 8.18% (kampaniya, o'rtacha) va 6.6% (sahifa, median) — **taqqoslab bo'lmaydi**: boshqa metrika, boshqa birlik, boshqa trafik. Ikkalasini bir jumlada ishlatish — xato.

> ⚠️ Bu raqamlar **AQSh bozori** uchun. O'zbekistonda CPC/CPL pastroq, konversiya ko'pincha ishonch omili sababli pastroq.
> Mahalliy raqamni faqat **mijozning o'z kabinetidan** ol. Xalqaro raqam faqat tartib ko'rsatadi ([[30-ozbekiston-konteksti]]).

## Manba

- `claude-ads-main/local/raw/claudes-bilim/marketolog/KNOWLEDGE.md` §5
- Unbounce: https://unbounce.com/average-conversion-rates-landing-pages/
- WordStream: https://www.wordstream.com/blog/2026-google-ads-benchmarks
