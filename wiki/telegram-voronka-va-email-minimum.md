---
name: telegram-voronka-va-email-minimum
description: "Mahalliy Telegram voronkasi strukturasi va email uchun texnik minimum (SPF/DKIM/DMARC, TLS, PTR, spam chegaralari, one-click unsubscribe)"
tags: [voronka, telegram, email, ozbekiston, texnik]
source: "claude-ads-main/local/raw/claudes-bilim/marketolog/KNOWLEDGE.md (§8)"
updated: 2026-09-20
---

# Telegram voronkasi va email texnik minimumi

> Bog'lanishlar: [[survey-funnel]] · [[sotuv-va-retention]] · [[lead-magnet-yetkazish-nomlash]] · [[30-ozbekiston-konteksti]]

## Telegram voronkasi — mahalliy standart

O'zbekiston bozorida email o'rniga ko'p hollarda **Telegram** ishlaydi.

```
Reklama (Meta/Instagram) → t.me link yoki bot deep link
   ↓
Bot: 1 ta savol + lead magnit (PDF, hisoblagich, checklist)
   ↓
Kanalga taklif (kontent = MOFU)
   ↓
3-5 kun kontent → shaxsiy taklif (bot yoki menejer)
   ↓
Sotuv suhbati DM da
```

**O'lchash:** bot `start` bosilishi · lead magnit olinishi · kanalga qo'shilish · menejerga o'tish — har biri **alohida event**.
UTM ni deep link parametrida uzat: `t.me/bot?start=meta_video1`.

**Afzalligi:** yetkazilish email'dan yuqori, javob tezligi daqiqalarda.
**Kamchiligi:** Meta piksel bilan bog'lash qiyin → bot tomonidan **Conversions API** orqali server-side event yuboriladi.

## Email — texnik minimum (aks holda spamga tushadi)

Gmail talablari (kuniga 5000+ xabar yuboruvchilarga, 2024-02-01 dan):

- **SPF va DKIM** — domen uchun; **DMARC** — yuboruvchi domen uchun (`p=none` ham yetarli)
- Alignment: `From:` domeni SPF yoki DKIM domeni bilan mos
- Yuboruvchi SMTP IP'sida **PTR**; hostname **A/AAAA** orqali o'sha IP'ga qaytsin
- **TLS** majburiy (2023-dekabrdan); RFC 5322 va yaroqli **Message-ID**

**Spam darajasi — ikkita raqam:** maqsad **< 0.10%**, **0.30% ga hech qachon yetmaslik**.
Amalda: 0.10% = 1000 yetkazilgandan 1 shikoyat; 0.30% = 3 ta.

**One-click unsubscribe:** RFC 8058 va RFC 2369 bo'yicha **ikkala** sarlavha kerak:
`List-Unsubscribe-Post: List-Unsubscribe=One-Click` + `List-Unsubscribe: <URL>`. **48 soat** ichida bajariladi.
Ishlamaydi: landing page'ga olib boradigan "one-click" link.

Yahoo (2024-fevraldan): SPF + DKIM; DMARC kamida `p=none` va o'tishi shart; one-click unsubscribe;
bekor qilish **2 kun** ichida; spam **< 0.3%**.

🟢 Manba: https://support.google.com/a/answer/81126 · https://senders.yahooinc.com/best-practices/

## Manba

- `claude-ads-main/local/raw/claudes-bilim/marketolog/KNOWLEDGE.md` §8
