---
name: sop-matn-auditi
description: "SOP: mavjud matnni konversiya uchun qayta yozish — diagnostika jadvali, P0/P1/P2 ustuvorlik, oldin→keyin formati"
tags: [sop, matn, audit, kopirayter]
source: "claude-ads-main/local/raw/claudes-bilim/kopirayter/PLAYBOOKS.md (PB-2)"
updated: 2026-09-20
---

# SOP — Matn auditi va qayta yozish

> Bog'lanishlar: [[zaifdan-kuchli-matn]] · [[kopirayter-frameworklar]] · [[etiroz-javob-patternlari]] · [[sop-landing-matni]]

**Qachon:** sayt/sahifa bor, lekin konversiya past yoki mijoz "matn ishlamayapti" deyapti.

## Kirish ma'lumotlari

1. Sahifa URL yoki matn to'liq
2. Hozirgi konversiya raqami (bor bo'lsa) va trafik manbai
3. Mijozlar eng ko'p beradigan savollar
4. Nima o'zgartirilishi mumkin — faqat matnmi yoki struktura ham?

## Qadamlar

1. Sahifa matnini to'liq ol (`WebFetch` yoki foydalanuvchidan).
2. **Diagnostika jadvali:** har blok uchun — nima qilyapti · 5 qarshilikdan qaysi biri · muammo · ustuvorlik.
3. **Bo'sh sifatlarni belgila** — har birini o'chirib ko'r; ma'no yo'qolmasa, birinchi navbatdagi tuzatish.
4. **Xabar mosligini tekshir** — reklama va'dasi bilan hero bir xilmi? Bu **eng tez qaytim beradigan** tuzatish.
5. **Yo'q bloklarni aniqlа** — ko'pincha yo'q: ijtimoiy dalil hero yonida, e'tiroz bloki, "kimga to'g'ri kelmaydi", mikro-matn.
6. **Ustuvorlik bo'yicha tartibla:**
   - **P0** — sarlavha, asosiy CTA, xabar mosligi (eng katta ta'sir)
   - **P1** — ijtimoiy dalil joyi, e'tirozlar, offer taqdimoti
   - **P2** — foyda matni, FAQ, footer
7. **Qayta yoz** — faqat P0 va P1 to'liq yoziladi; P2 ga tavsiya yetarli.
8. **Oldin → keyin jadvali** — har tuzatish uchun **sabab** bilan.
9. **Test rejasi:** qaysi 2 variant, qaysi metrika o'lchanadi ([[ab-test-mexanikasi]]).

## Chiqish artefakti

```markdown
# {Sahifa} — matn auditi
## Xulosa (3 qator): eng katta muammo | eng tez tuzatish | kutilayotgan ta'sir
## Diagnostika jadvali (blok / muammo / ustuvorlik)
## Oldin → Keyin | Blok | Hozirgi | Yangi | Nega |
## P2 tavsiyalar (ko'rsatma, yozilmagan)
## Test rejasi
```

## Muvaffaqiyat mezoni

- Har tuzatish uchun **sabab** yozilgan
- P0 tuzatishlar **to'liq yozilgan** — "o'zingiz to'ldirasiz" yo'q
- Kutilayotgan ta'sir aytilgan, lekin **aniq foiz va'da qilinmagan** (tekshirilmagan bo'lardi — [[dalil-tasnifi]])

## Manba

- `claude-ads-main/local/raw/claudes-bilim/kopirayter/PLAYBOOKS.md` PB-2
