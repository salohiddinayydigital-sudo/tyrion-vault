---
name: session-handoff
description: Session Handoff — kontekst to'lganda 150 so'zlik xulosa + /clear + yangi sessiya (compact o'rniga)
tags: [token, kontekst, protsedura]
source: raw/2026-09-03-token-gigiyena-va-meta-mashinasi.md (§ Asosiy amaliy xaklar)
updated: 2026-09-05
---

# Session Handoff

**Qachon:** kontekst to'lish arafasida (60% qoidasiga qarang) — 95% da ishga tushadigan avto-ixchamlashtirishni kutmasdan.

**Nima uchun /compact emas:** /compact ixchamlashtiradi, handoff esa toza kontekstda davom ettiradi — qilingan ish va ochiq vazifalar yo'qolmaydi, sifat buzilmaydi.

## Protsedura (3 qadam)

1. **Xulosa yozing:** qilingan ishlar + ochiq vazifalar bo'yicha 150 so'zlik xulosa
2. **`/clear`** bering
3. Xulosani **yangi toza sessiyaga** tashlab davom eting

Handoff kesh uzilishlari ro'yxatining ham qismi (DoD): tanaffus 1 soatdan oshsa ham shu yo'l bilan qaytish tavsiya. Asos: [[token-gigiyenasi]] · Kesh muddati: [[prompt-caching]]

Kontekstni qayta yig'ishda faqat kerakli vaziyatli bilimni yuklang: [[kontekst-ajratish]]. Yangi sessiyada yo'nalish xaritasi: [[INDEX.md]].
