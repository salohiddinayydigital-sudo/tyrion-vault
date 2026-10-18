---
name: mijoz-ishga-tushirish
description: Mijoz kuni SOP — preflight, onboarding, offer, kampaniya, voronka, lead ishlov, hisobot (repo oqimi bilan)
tags: [sop, mijoz, meta-ads, checklist]
source: wiki qoidalar yig'indisi (meta mashinasi + repo memory.md §4) + mijoz shabloni
updated: 2026-09-03
---

# Mijozni ishga tushirish — SOP

> Ertalab shu faylni oching: tepadan pastga bajariladi. Har qadam bitta qaydga havola — detal shu yerda.

## 0. Preflight — 🔑 FAQAT INSON qiladi

- [ ] MetaMCP ulanganmi + draft yaratish sinovdan o'tganmi (Meta kabinetiga kirish)
- [ ] Pixel/CAPI: **Lead** va **Schedule** hodisalari test lead bilan o'lchanyaptimi
- [ ] HighLevel: taqvim bo'sh slotlar + avto-SMS/5 daqiqa qoidasi sozlanganmi
- [ ] Landing jonli va forma Lead/Schedule yuboryaptimi
- [ ] Hisob limiti/policy holati toza

## 1. Onboarding (mijoz bilan — siz)

- `journal/_SHABLON.md` dan nusxa: `journal/YYYY-MM-DD-mijoz-nomi.md`
- Mijozdan 6 savol (memory.md §4 qatori) — mahsulot, geo/til, byudjet, konversiya qiymati
- **1-1-1:** 1 nisha + 1 offer + 1 voronka → [[shown-appointments]]
- **Offer raqamlari:** mijoz byudjetni o'zi to'lasa — setup + $147/shown; siz qoplasangiz — $297/shown
- **KPI:** shown uchrashuv (Lead/Schedule); erta va'da yo'q — 30 uchrashuv qoidasi → [[sotuv-va-retention]]

## 2. Kampaniya qurish (agent: `/ads` routing)

- `memory.md` §2 qoida 6: audit → plan → create → launch; `local/meta-playbook-uz.md`
- **Parametrlar** → [[meta-ads-sozlamalari]]: Leads · Lead|Schedule · broad 29–64 + radius 25–35 mi · FB+IG Feed · $30–50/adset · oshirish ≤20–30%/kun (learning phase!)
- **Kreativ** → [[kreativ-sikl]]: statik + narx langari ("Deck replacement starting at…")
- **Kreativ manbasi** → [[meta-ads-library-tadqiqot]] (raqobatchi research) + [[ad-iteration]] (g'olibdan 2–3 variatsiya)

## 3. Voronka + lead ishlov (doimiy)

- Survey savollar → HighLevel taqvimi → [[survey-funnel]]
- Speed to Lead ≤5 daqiqa · lid→mijoz o'rtacha 8 aloqa · haftalik hisobot (silence = scam) → [[sotuv-va-retention]]

## 4. Yakunlash (har ish oxirida)

- Natija → `outputs/YYYY-MM-DD-mavzu.md` (repo qoidasi: chatda qolgan natija = yo'qolgan)
- Jurnalga statistika + kill/keep/scale qarorlar sababi bilan
- Vault LOG: `LOG.md` (mybrain) · `local/wiki/log.md` (repo)
- 4 xato rejimi nazorati: [[kontekst-xatolari]] · Hafta oxiri: [[haftalik-audit]]

---

**Bog'liq:** [[shown-appointments]] · [[meta-ads-sozlamalari]] · [[kreativ-sikl]] · [[survey-funnel]] · [[sotuv-va-retention]] · [[meta-ads-library-tadqiqot]] · [[ad-iteration]] · [[more-better-new]]
