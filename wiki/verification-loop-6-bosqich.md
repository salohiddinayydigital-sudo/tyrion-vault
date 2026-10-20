---
name: verification-loop-6-bosqich
description: "Marketing auditi, kreativ va kampaniya o'zgarishlarini topshirishdan oldin 6 bosqichli deterministik tekshiruv zanjiri (ECC verification-loop adaptatsiyasi)"
tags: [verification, sifat, dod, audit, ecc, xavfsizlik]
source: "raw/2026-09-16-ecc-naqshlar-tahlili.md §6 + rules/50-topshirish-dod.md (2026-10-17)"
updated: 2026-10-17
---

# 🔍 6-Bosqichli Marketing Tekshiruv Zanjiri (Verification Loop)

> **Asosiy qoida:** Hech bir audit hisoboti, byudjet rejasi yoki kreativ paket 6 ta tekshiruv bosqichidan o'tmasdan mijozga yoki `outputs/` papkasiga topshirilmaydi ([[50-topshirish-dod]]).

## 6 Faza Ketma-ketligi

| Faza | Nima tekshiriladi | Asbob / Qoida | To'xtash sharti (STOP Gate) |
|------|-------------------|---------------|-----------------------------|
| **1. Manba (Source)** | Har bir raqam va da'voning manbasi bormi? | [[00-manba]], [[dalil-tasnifi]] | Manbasiz benchmark yoki to'qima raqam bo'lsa — **STOP** |
| **2. Matematika (Math)** | Break-even CPA, ROAS, 1-5-5 va pacing to'g'rimi? | `tools/calculator.py`, [[unit-iqtisodiyot-formulalari]] | Zararga ishlovchi marja yoki <50 konv/hafta ad set — **STOP** |
| **3. Spend-Guard (Safety)** | Byudjet o'zgarishi $\le 20\%$, Stop-loss va Rollback bormi? | `tools/spend-guard.py`, [[40-xavfsizlik-va-hisob]] | `spend-guard.py` xato qaytarsa (`exit 1`) — **STOP** |
| **4. Platforma Siyosati (Policy)** | Telegram 160 belgi/1 emoji, Meta/Google policy to'g'rimi? | `spend-guard.py copy`, [[reklama-matn-limitlari]] | Taqiqlangan va'da yoki format buzilishi — **STOP** |
| **5. Mahalliy Kontekst (UZ)** | Telegram voronka, 3 til qoidasi va to'lov mosmi? | [[30-ozbekiston-konteksti]], [[ozbek-sotuv-matni-standarti]] | To'g'ridan-to'g'ri tarjima yoki noto'g'ri voronka — **STOP** |
| **6. Topshirish (Delivery Gate)** | Fayl `outputs/` da, `INDEX.md` va `LOG.md` yangilanganmi? | `hooks/tyrion-hook.py dod`, `tools/vault-audit.py --gate` | Darvoza yopiq bo'lsa (`exit 1`) — **STOP** |

## Anti-Patterns (WRONG vs CORRECT)

- **FAIL: WRONG** — Mijozga chatning o'zida hisob-kitobsiz "Byudjetni 2 barobar oshiring" deb javob berish.
- **PASS: CORRECT** — `calculator.py` bilan unit-iqtisodiyotni hisoblash, `spend-guard.py` orqali +20% qoidasini tekshirish va `outputs/` da `Rollback` rejali fayl yaratish ([[70-charter-baseline]]).

## Manba

- `raw/2026-09-16-ecc-naqshlar-tahlili.md` §6 — ECC `verification-loop` va `delivery-gate`
- [[50-topshirish-dod]] · [[00-manba]] · [[40-xavfsizlik-va-hisob]] · [[70-charter-baseline]] · [[uzluksiz-organish-instinktlar]]
