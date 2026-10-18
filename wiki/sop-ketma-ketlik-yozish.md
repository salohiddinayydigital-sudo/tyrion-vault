---
name: sop-ketma-ketlik-yozish
description: "SOP: email yoki Telegram ketma-ketligi (welcome/nurture/launch/win-back) — har xatga bitta maqsad, sotuv nisbati, texnik eslatmalar"
tags: [sop, email, telegram, voronka]
source: "claude-ads-main/local/raw/claudes-bilim/kopirayter/PLAYBOOKS.md (PB-4)"
updated: 2026-09-20
---

# SOP — Email / Telegram ketma-ketligi

> Bog'lanishlar: [[telegram-voronka-va-email-minimum]] · [[lead-magnet-turlari]] · [[survey-funnel]] · [[sotuv-va-retention]]

**Qachon:** lead magnit bor va uni sotuvga aylantirish kerak; yoki launch, win-back kerak.

## Kirish ma'lumotlari

1. Ketma-ketlik turi: welcome / nurture / launch / win-back
2. Baza qayerda: email xizmati yoki Telegram bot?
3. Baza hajmi va issiqligi
4. Offer va narx
5. Kirish nuqtasi — odam qanday ro'yxatga tushdi?

## Qadamlar

1. **Kanalni aniqlashtir.** Baza Telegramda yoki mahalliy B2C bo'lsa — email o'rniga **Telegram ketma-ketligini** taklif qil
   (struktura bir xil, format boshqa: qisqaroq, subject o'rniga birinchi qator).
2. Turga mos struktura: welcome **5-7** xat · launch **5** · win-back **3** · nurture davomiy.
3. **Har xat uchun bitta maqsad** — xat 2 ta ish qilmaydi.
4. **Yoz:** subject (3 variant) + preview text + tana + **bitta** CTA.
5. Preview text subject'ni **davom ettiradi**, takrorlamaydi.
6. **Sotuv nisbatini tekshir:** nurture'da 4 xatdan 3 tasi foydali bo'lishi kerak.
7. **Email texnik minimumi** eslatma sifatida qo'shiladi: SPF+DKIM+DMARC, spam maqsad 0.10% / chegara 0.30%,
   bir bosishda obuna bekor qilish **48 soat** ichida ([[telegram-voronka-va-email-minimum]]).
8. **Telegram bo'lsa:** har xabar **300-600 belgi**, bitta tugma, kunlik 1 tadan ko'p emas.

## Chiqish artefakti

```markdown
# {Loyiha} — {tur} ketma-ketligi
Kanal | Xatlar soni | Davomiylik
## Jadval: | # | Vaqt | Maqsad | Subject (tavsiya) |
## Xat 1: Subject A/B/C ← tavsiya · Preview · Tana (to'liq) · CTA
## Xat 2..N
## Texnik eslatma (SPF/DKIM/DMARC, unsubscribe, spam chegarasi)
```

## Muvaffaqiyat mezoni

- Har xatda **bitta maqsad, bitta CTA**
- Nurture'da sotuv nisbati buzilmagan
- Kanal tanlovi asoslangan (nega email, nega Telegram)
- Email bo'lsa texnik talablar yozilgan — mijoz keyin muammoga tushmaydi

## Manba

- `claude-ads-main/local/raw/claudes-bilim/kopirayter/PLAYBOOKS.md` PB-4
