---
name: kontekst-xatolari
description: AI noto'g'ri gapirishining 4 sababi — Poisoning, Bloat, Confusion, Clash (profilaktikasi bilan)
tags: [audit, xatolik, kontekst, AIOS]
source: raw/2026-09-03-aios-xatoliklar-va-audit.md (§ 4 sabab) + raw/2026-09-03-mybrain-vault-spec.md (§ 2.5)
updated: 2026-09-03
---

# Kontekst xatolari (AIOS — 4 sabab)

Ma'lumotlar ko'payganda AI noto'g'ri gapirishining (hallucination) 4 ta sababi va profilaktikasi:

| Xato | Sabab | Oldini olish |
|------|-------|--------------|
| **Poisoning** | Bazada noto'g'ri fakt bor | Faqat manbadagi fakt qabul (`source` majburiy); manba noto'g'ri chiqsa — raw o'zgarmaydi, wiki qayd tuzatiladi |
| **Bloat** | Ortiqcha ma'lumot (needle in the haystack) | Atomik qaydlar, zich xulosa; to'liq material xom manbada qoladi, yoppasiga o'qilmaydi |
| **Confusion** | Muhim fakt yetishmasligi | Manbasiz raqam/fakt to'qilmaydi; yetishmayotgan ma'lumot izlab topiladi yoki aytiladi |
| **Clash** | Eskirgan + yangi qoida bir vaqtda | Ziddiyatda yangisi qoladi, eskisi arxivga/belgilashga ketadi |

Vault qoidasi №5 ([[CLAUDE.md|router]]) bu 4 rejimni majburiy qiladi. Harakatdagi profilaktika: [[kontekst-ajratish]] (Bloat/Confusion) · Muntazam tekshiruv: [[haftalik-audit]] (barcha tur) · Token asoslari: [[token-gigiyenasi]]
