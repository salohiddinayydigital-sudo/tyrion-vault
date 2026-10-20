---
name: narxlash-va-narx-psixologiyasi
description: "Narxlash modellari (setup+performance, retainer, value-based, soatlik, paket), tier dizayni va narx psixologiyasi (anchoring, decoy, left-digit) mexanikasi bilan"
tags: [narx, offer, strategiya, psixologiya]
source: "claude-ads-main/local/raw/claudes-bilim/marketolog/KNOWLEDGE.md (§2-3)"
updated: 2026-09-20
---

# Narxlash va narx psixologiyasi

> Bog'lanishlar: [[taklif-tuzilishi]] · [[unit-iqtisodiyot-formulalari]] · [[pozitsiyalash-dunford]] · [[zaifdan-kuchli-matn]]

## Narxlash modellari

| Model | Qanday ishlaydi | Qachon | Xavfi |
|---|---|---|---|
| **Setup + performance** | Boshlang'ich to'lov + natijadan foiz | Mijoz natijaga ishonmaydi; natijani nazorat qila olasan | Atribusiya bahsi — shartnomada "natija" ta'rifi aniq bo'lsin |
| **Retainer** (oylik) | Belgilangan summa, belgilangan hajm | Uzoq muddatli, takrorlanadigan ish | Scope creep — oylik ish limitini yoz |
| **Value-based** | Yaratilgan qiymatning ulushi | Qiymat aniq o'lchanadi va katta | Mijoz iqtisodiyotini bilish talab; kichik biznesda kam ishlaydi |
| **Soatlik** | Soat × stavka | Hajmi noaniq, konsultatsiya | Tezlashsang — kamroq olasan; faqat kirish nuqtasi |
| **Paket** (fixed scope) | Aniq natija — aniq narx | Chegarasi aniq loyiha | Noto'g'ri baholash; "nima kirmaydi" ro'yxati kerak |

**Amaliy qoida:** yangi mijoz bilan **paket**dan boshla (risk kam, qaror tez) → natija chiqqach **retainer**ga o'tkaz.
Performance modelga faqat 2-3 ta muvaffaqiyatli loyihadan keyin o't.

## Tier dizayni

- **3 ta tier** — 2 tadan yaxshiroq (decoy effekti).
- Har tierda **"kim uchun"** bir jumlada. Target — **o'rtadagisi** ("eng ommabop" belgisi bilan).
- Yuqori tier target'dan **2-3 barobar** qimmat — u anchor, sotilishi shart emas.
- Tierlar farqi **qiymat metrikasi** bo'yicha (mijoz soni, kanal, kreativ), tasodifiy xususiyat emas.

## Narx psixologiyasi — mexanikasi bilan

**Anchoring** (Tversky & Kahneman, 1974). Odam birinchi ko'rgan raqamdan hisoblab, yetarlicha tuzatmaydi — anchor mantiqsiz bo'lsa ham ishlaydi.
Amaliy: eng qimmat tierni birinchi ko'rsat; "jami qiymat 11.5 mln → paket 6.9 mln"; chizib tashlangan narx.
🟢 Manba: https://www.science.org/doi/10.1126/science.185.4157.1124

**Decoy / asimmetrik dominatsiya** (Huber, Payne & Puto, 1982). Uchinchi variant ikkita o'lchov bo'yicha ham bitta variantdan yomon bo'lsa — tanlov ustun variantga siljiydi.
Shart: decoy **ikkala** o'lchovda yomon bo'lishi kerak; bittasida bo'lsa ishlamaydi.

**Left-digit effect** (Thomas & Morwitz, 2005). $2.99 vs $3.00 ishlaydi; **$3.59 vs $3.60 ishlamaydi** — chapdagi raqam o'zgarmaydi.
Ya'ni "99 bilan tugatish" faqat **razryad chegarasidan** o'tganda foyda beradi. Effekt raqobatchi narxi yaqin bo'lganda kuchliroq.
Amaliy: 490 000 vs 500 000 ishlaydi; 470 000 vs 480 000 ishlamaydi.
🟢 Manba: https://academic.oup.com/jcr/article-abstract/32/1/54/1796360

## Offer stacking

Har bir tarkibiy qismni **alohida nomla va alohida narxla**, keyin birlashtir:

```
Landing page (dizayn + matn + kod)   — 4 000 000
Meta Ads sozlash + 3 kreativ         — 2 500 000
Telegram bot + voronka               — 3 000 000
30 kun optimizatsiya                 — 2 000 000
Jami qiymat:                         11 500 000
Paket narxi:                          6 900 000
```

Raqamlar — illyustratsiya; har mijoz uchun o'zi hisoblanadi ([[unit-iqtisodiyot-formulalari]]).

## Kafolat turlari (Erishish ehtimoli richagi)

| Tur | Formulasi | Qachon |
|---|---|---|
| Shartsiz | "30 kun ichida pulni qaytaramiz, sababsiz" | Yuqori marja, qaytarish past |
| Shartli | "3 oyda 30 ta lead bo'lmasa — keyingi oy bepul" | Xizmat, natija o'lchanadi |
| Ishlash kafolati | "KPI ga yetmasa — farqni ishlab beramiz" | Retainer |
| Anti-kafolat | "Pul qaytmaydi — jarayon o'zaro majburiyat" | Yuqori narx, tanlangan mijoz |

> **O'zbekistonda shartli kafolat** eng ishonchli: shartsiz kafolat "bu qanday tuzoq?" degan shubha uyg'otadi.

## Manba

- `claude-ads-main/local/raw/claudes-bilim/marketolog/KNOWLEDGE.md` §2–3
- Alex Hormozi, *$100M Offers* — https://www.acquisition.com/training/offers
