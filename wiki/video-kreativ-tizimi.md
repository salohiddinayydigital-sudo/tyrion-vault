---
name: video-kreativ-tizimi
description: "Video kreativ tizimi — hook/tana/CTA arxitekturasi, 9 uchadigan format, test tartibi, spec darvozasi (joriy rasmiy manbadan), fatigue va AI ishlab chiqarish"
tags: [kreativ, video, meta-ads, format]
source: "kanal-bilim/03_9_ta_uchadigan_format.txt + ads/references/meta-creative-specs.md + marketolog/KNOWLEDGE.md §6 + bozor-trend-kreativi"
updated: 2026-09-20
---

# Video kreativ tizimi

> Bog'lanishlar: [[kreativ-sikl]] · [[kreativ-hit-rate]] · [[funnel-2-kreativ-format]] · [[reklama-matn-limitlari]] · [[unique-mexanizm]] · [[sop-meta-reklama-matni]]

## 1. Arxitektura (har video shu 4 qismdan)

| Qism | Vazifa | Amaliy qoida |
|---|---|---|
| **Hook (0-3s)** | To'xtatish — "bu menga tegishli" | Birinchi jumla **8-12 so'z**, mustaqil ma'no; Instagram'da **birinchi 125 belgi** ichida |
| **Ushlab turish** | Nega oxirigacha ko'rish kerak | Savol ochiq qoladi / natija ko'rsatiladi, keyin sabab |
| **Tana** | Isbot + mexanizm | Proof > promise: mexanizm va uning ortidagi dalil; 1 ta asosiy va'da |
| **CTA** | Aniq harakat | Fe'l + nima oladi ("Telegramda yozing — 20 daqiqalik tekshiruv") |

## 2. 9 uchadigan format (katalog)

| # | Format | Nima qiladi |
|---|---|---|
| 1 | **50/50** | Videoda boshqa video haqida gapiriladi (reaksiya/duet) |
| 2 | **Savol-Javob** | Savol → qisqa aniq javob |
| 3 | **Ekspert** | Mutaxassis tushuntiradi (vakolat) |
| 4 | **Face-to-camera** | Kameraga yaqin, to'g'ridan-to'g'ri gapirish |
| 5 | **Storytell** | Voqeani aytib berish |
| 6 | **Syujetli** | Voqea bilan bog'lab olib chiqish |
| 7 | **Ekstremal** | Mahsulotni qiziqarli podxodda yoritish |
| 8 | **Shaxsiyatni ochish** | Hayot/fikrlar bilan bo'lishish |
| 9 | **Solishtirish** | Mahsulot/odam/oldin-keyin taqqoslash |

🟡 **TAJRIBA** — kanal amaliyoti (nazorat ishi); har format nishaga moslanadi, ko'r-ko'rona ko'chirilmaydi.
Manba: `claude-ads-main/local/raw/kanal-bilim/03_9_ta_uchadigan_format.txt` (har formatga IG misol bor).

## 3. Test tartibi — ta'sir kuchi bo'yicha

| # | Nima testlanadi | Kutilayotgan farq | Muddat |
|---|---|---|---|
| 1 | **Offer** | 2-5 barobar | 7-14 kun |
| 2 | **Hook** (0-3s / birinchi qator) | 1.5-3 barobar | 5-7 kun |
| 3 | **Format** (video/statik/karusel/UGC) | 1.3-2 barobar | 7 kun |
| 4 | Auditoriya | 1.2-1.8 barobar | 7-14 kun |
| 5 | Landing sarlavhasi | 1.1-1.4 barobar | trafikka bog'liq |
| 6 | Tugma rangi, shrift | ~0 | **test qilma** |

🟡 Diapazonlar — amaliyot kuzatuvi, ilmiy o'lchov emas. Asosiy xulosa — **tartib**: offerni tekshirmasdan tugma rangini testlash — vaqt yo'qotish.
Bir ad set da **3-5 kreativ**; 5 tadan ortiq — "learning limited" sabablaridan biri ([[ab-test-mexanikasi]]).

## 4. Xilma-xillik qoidasi

**Resize ≠ diversity.** Bir konseptning o'lchamini o'zgartirish — coverage, kreativ test emas.
Konseptlar **moddiy jihatdan farqli** bo'lsin (boshqa angle/avatar/format).

## 5. Spec darvozasi (hardcode qilinmaydi)

Ratsionlar, o'lchamlar, davomiylik, xavfsiz zona (safe zone), matn kesilishi, fayl limitlari va format mavjudligi **o'zgaruvchan**.
Har placement uchun **joriy rasmiy manbadan** olinadi va manba ID + sana yoziladi. Tasdiqlanmasa — `needs_input`.
Bir placement qoidasi boshqasiga ko'chirilmaydi; "muayyan ratsion universal eng yaxshi" degan da'vo qilinmaydi.

🟢 Manba: `ads/references/meta-creative-specs.md` (Meta rasmiy)

## 6. Fatigue (charchash)

- **Chastota 3+** bo'lganda CPM o'sadi, CTR tushadi (kichik auditoriyada tez) 🟡
- Kreativni **rejaga ko'ra** yangila — natija tushgandan keyin emas
- Hit rate: kampaniya byudjetining **>5%**ini olgan kreativ — g'olib ([[kreativ-hit-rate]])
- G'olibdan iteratsiya: format/kompozitsiya/matnni saqlab, **yangi hook (0-5s) + headline + 2-3 jumla tana** bilan 2-3 variant ([[ad-iteration]])

## 7. AI ishlab chiqarish (tezlik uchun)

3-manbali pipeline: **Meta Ads Library** (g'olib pattern) → **AI generatsiya** (Higgsfield/Veo/Kling) → **tekshiruv** (brend + spec + policy).
Avtomatik haftalik refresh — statik + narx langari; to'liq avtonom emas, tekshiruv darvozasi bilan ([[bozor-trend-kreativi]] · [[kreativ-sikl]]).

## 8. Ishlab chiqarishni tekshirish (topshirishdan oldin)

- [ ] Hook 0-3s ichida, ovozsiz ham tushunarli (subtitr)
- [ ] Har placement uchun spec manbasi yozilgan
- [ ] Konseptlar bir-biridan farqli (resize emas)
- [ ] Proof/mexanizm bor — faqat va'da emas
- [ ] CTA aniq, destination Telegram/landing bilan mos
- [ ] Policy: isbotsiz va'da, "eng yaxshi", raqamsiz da'vo yo'q ([[ozbek-sotuv-matni-standarti]])
- [ ] Sifat chegarasi: [[sifat-darajasi]] · tekshiruv ro'yxati: [[topshirish-cheklist-matn]]

## Manba

- `claude-ads-main/local/raw/kanal-bilim/03_9_ta_uchadigan_format.txt`
- `claude-ads-main/ads/references/meta-creative-specs.md`
- `claude-ads-main/local/raw/claudes-bilim/marketolog/KNOWLEDGE.md` §6
