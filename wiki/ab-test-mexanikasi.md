---
name: ab-test-mexanikasi
description: "A/B test qachon statistik ma'noga ega — minimal namuna hajmi formulasi, kichik trafik alternativasi va testni buzadigan 5 xato"
tags: [test, metrika, kreativ, statistika]
source: "claude-ads-main/local/raw/claudes-bilim/marketolog/KNOWLEDGE.md (§9 A/B test)"
updated: 2026-09-20
---

# A/B test mexanikasi — namuna hajmi va xatolar

> Bog'lanishlar: [[kreativ-hit-rate]] · [[ad-iteration]] · [[learning-phase-qoidalari]] · [[reklama-matn-limitlari]]

## Minimal namuna hajmi

Ikki proporsiyani taqqoslash uchun (α = 0.05 ikki tomonlama, quvvat 80%):

```
n (har bir variant uchun) ≈ 16 × p × (1 − p) / δ²

p = bazaviy konversiya (kasr)
δ = aniqlamoqchi bo'lgan MUTLAQ farq (kasr)
```

`16` koeffitsiyenti: 2 × (1.96 + 0.84)² = 15.68 ≈ 16.

**Misol.** Bazaviy konversiya 5%, 20% nisbiy o'sishni aniqlamoqchimiz → δ = 1 p.p. = 0.01.

```
n = 16 × 0.05 × 0.95 / 0.0001 = 7600
```

Har variantga **7600 tashrif**, jami **15 200**. Oyiga 2000 tashrif keladigan saytda bu **7.6 oy** — ya'ni amalda bajarilmaydi.

## Kichik trafikda nima qilish kerak

- **Yuqori hajmli nuqtada test qil** — reklama CTR (bir necha ming impressiya bir kunda to'planadi).
- **Katta o'zgarishni test qil** (butunlay boshqa offer), kichik tweak emas — katta δ kichik namunani yetarli qiladi.
- **Sifat usullari:** 5-7 mijoz bilan suhbat, sessiya yozuvi, sotuvchi e'tirozlari ro'yxati ([[ozbek-sotuv-matni-standarti]]).

## Testni buzadigan 5 xato

| Xato | Nima bo'ladi |
|---|---|
| Erta to'xtatish ("A yutyapti!") | Yolg'on pozitiv; namuna hajmini oldindan hisobla |
| Bir vaqtda 5 ta narsani o'zgartirish | Qaysi biri ishlaganini bilib bo'lmaydi |
| Haftaning bir qismida test | Dushanba va shanba xulqi har xil; kamida **7 kun**, mumkin bo'lsa 14 |
| Kichik segmentda "yutuq" topish | Post-hoc segmentatsiya — deyarli har doim tasodif |
| Klikni optimallashtirish, konversiyani emas | CTR o'sib, sotuv tushishi mumkin |

## Meta kontekstida

- Learning phase davomida matnni almashtirish o'rganishni **qayta boshlaydi** — variantlarni bir vaqtda qo'y, ketma-ket almashtirma ([[learning-phase-qoidalari]]).
- Bir ad set da 3-5 ta kreativ; 5 tadan ortiq matn — "learning limited" sabablaridan biri.

## Manba

- `claude-ads-main/local/raw/claudes-bilim/marketolog/KNOWLEDGE.md` §9
