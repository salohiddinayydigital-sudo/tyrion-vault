---
name: sop-kampaniya-rejalash
description: "SOP: reklama kampaniyasini noldan rejalashtirish — iqtisodni oldin tekshirish, platforma tanlash, konversiya hodisasi, test va to'xtatish qoidalari"
tags: [sop, kampaniya, meta-ads, google-ads]
source: "claude-ads-main/local/raw/claudes-bilim/marketolog/PLAYBOOKS.md (PB-3)"
updated: 2026-09-20
---

# SOP — Kampaniyani noldan rejalashtirish

> Bog'lanishlar: [[meta-kampaniya-tuzilmalari]] · [[unit-iqtisodiyot-formulalari]] · [[learning-phase-qoidalari]] · [[sop-voronka-loyihalash]]

**Qachon:** birinchi marta pullik reklama ishga tushirilganda yoki yangi mahsulot uchun kampaniya kerak.

## Kirish ma'lumotlari

Offer · ICP · byudjet · muddat · o'rtacha chek va marja · mavjud kreativlar · landing bormi?

## Qadamlar

1. **Iqtisodni birinchi tekshir.** Break-even ROAS ni hisobla. Byudjet learning phase uchun yetadimi?
   **Yetmasa — kampaniyani boshlashdan oldin ayt**, keyin emas.
2. **Platformani tanla:**
   - Talab mavjud (odam qidiryapti) → **Google**
   - Talab yaratish kerak (odam bilmaydi) → **Meta**
   - Mahalliy B2C → ko'pincha **Meta + Telegram**
3. **Obyektiv va konversiya hodisasini tanla** — hodisa haqiqatda sodir bo'ladigan va **tez-tez** bo'lsin.
   Kam uchraydigan hodisa (haftada 2 sotuv) o'rganish uchun signal bermaydi → voronkaning yuqoriroq hodisasini tanla.
4. **Struktura tuz** — boshlashda oddiy: **1 kampaniya, 1-2 auditoriya, 3-5 kreativ**.
   Ko'p bo'lish byudjetni bo'lib yuboradi.
5. **Kreativ va matn briefi tuz** — qaysi og'riq, qaysi va'da, qaysi CTA, qancha variant ([[sop-meta-reklama-matni]]).
6. **O'lchash zanjirini ula** — Piksel/CAPI, konversiya hodisalari, UTM.
   **Bularsiz ishga tushirma** — o'lchanmagan kampaniya pul yoqish demak.
7. **Test rejasini yoz — ustuvorlik bilan:** kreativ → auditoriya → landing → narx.
   Har test uchun: nima o'zgaradi · qancha byudjet · qaysi metrik hal qiladi · qachon qaror.
8. **To'xtatish qoidalarini yoz** — qaysi raqamda kampaniya to'xtatiladi (masalan CAC break-even'dan N% oshsa).
   Bu qoida **oldindan** yozilishi shart — kampaniya ketayotganda emas.

## Chiqish artefakti

`KAMPANIYA-<nom>.md` — iqtisod, struktura, auditoriyalar, kreativ brief, o'lchash sxemasi, test rejasi, to'xtatish qoidalari, haftalik jadval.

## Muvaffaqiyat mezoni

Kampaniyani **boshqa odam shu hujjat bilan mustaqil ishga tushira oladi**.

## Manba

- `claude-ads-main/local/raw/claudes-bilim/marketolog/PLAYBOOKS.md` PB-3
