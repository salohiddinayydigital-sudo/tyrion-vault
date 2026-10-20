---
name: sop-meta-reklama-matni
description: "SOP: Meta reklama matni — 5 variant 5 xil burchakdan, belgi chegaralari, test qoidasi va landing mosligi tekshiruvi"
tags: [sop, matn, meta-ads, reklama]
source: "claude-ads-main/local/raw/claudes-bilim/kopirayter/PLAYBOOKS.md (PB-3)"
updated: 2026-09-20
---

# SOP — Meta reklama matni (5 variant)

> Bog'lanishlar: [[reklama-matn-limitlari]] · [[kopirayter-frameworklar]] · [[ab-test-mexanikasi]] · [[learning-phase-qoidalari]]

**Qachon:** Instagram/Facebook reklamasi ishga tushiriladi va matn kerak.

## Kirish ma'lumotlari

1. Offer aniq nima va narxi
2. Auditoriya (yosh, shahar, qiziqish)
3. Joylashuv: Instagram Feed / Facebook Feed / Stories / Reels
4. Landing yoki Telegram — qayerga olib boradi?
5. Bor kreativ bormi yoki matn birinchi yoziladimi?
6. Auditoriya sovuqmi, iliqmi?

## Qadamlar

1. **Chegaralarni belgila:** Instagram Feed — primary **125 belgi**, headline **40**;
   Facebook Feed — primary 50–150, headline **27**. Hook birinchi 125 belgi ichida.
2. **5 variantni 5 xil burchakdan yoz** — bir xil gapning 5 shakli emas:

| # | Burchak | Framework |
|---|---|---|
| 1 | Og'riq | PAS |
| 2 | Natija/transformatsiya | BAB |
| 3 | Ijtimoiy dalil (mijoz gapi) | Sitatadan boshlanadi |
| 4 | E'tirozni oldindan olish | "Buni o'ylagan bo'lsangiz..." |
| 5 | To'g'ridan-to'g'ri offer | Buyruq sarlavhasi |

3. Har variantga: primary text + headline + CTA tugma matni.
4. **Belgi sonini sanab yoz** — har matn ostida `(118/125)`.
5. **Test qoidasi:** 5 variant **bir vaqtda** qo'yiladi, ketma-ket almashtirilmaydi
   (har jiddiy o'zgarish learning phase'ni qayta boshlaydi). Bitta ad set ga 5 tadan ortiq reklama qo'yilmaydi.
6. **Landing bilan moslikni tekshir** — mos bo'lmasa, landing sarlavhasini ham tuzat.

## Chiqish artefakti

```markdown
# {Kampaniya} — Meta reklama matni
Joylashuv | Chegaralar
## Variant 1 — Og'riq (PAS): primary (118/125) + headline (34/40) + CTA + nega bu burchak
## Variant 2..5
## Landing moslik: reklama va'dasi | landing H1 | mos: ha/yo'q
## Test rejasi: barchasi bir vaqtda, 1 ad set; metrika CTR → konversiya → lead narxi
```

## Muvaffaqiyat mezoni

- 5 variant 5 xil burchakdan, takrorlanmaydi
- Har matn belgi chegarasidan **oshgan emas** (sanalgan)
- Hook birinchi jumlada, mustaqil ma'noga ega
- Landing bilan xabar mosligi tekshirilgan

## Manba

- `claude-ads-main/local/raw/claudes-bilim/kopirayter/PLAYBOOKS.md` PB-3
