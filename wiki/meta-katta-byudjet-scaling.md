---
name: meta-katta-byudjet-scaling
description: "Katta byudjetda Meta scaling intizomi — marginal matematika (marginal CPA/ROAS), 6 shartli scale darvozasi, vertikal/gorizontal qadamlar, pause intizomi va change packet"
tags: [meta-ads, scaling, byudjet, qaror]
source: "wiki/meta-playbook-uz.md + ads/references/budget-allocation.md (2026-07-11) + marketolog/KNOWLEDGE.md §6"
updated: 2026-09-20
---

# Meta — katta byudjet scaling intizomi

> Bog'lanishlar: [[unit-iqtisodiyot-formulalari]] · [[scaling-cheklovlari]] · [[blended-roas-net-cash]] · [[learning-phase-qoidalari]] · [[sop-kampaniya-diagnostika]]

Katta byudjetda xato qimmat: **"o'rtacha yaxshi" ≠ "marginal yaxshi"**. Scaling — matematika + darvozalar, instinkt emas.

## 1. Marginal matematika (o'rtacha emas)

```
CPA            = spend / accepted conversions
ROAS           = accepted value / spend
contribution_after_ads = accepted contribution − spend
break_even_CPA = contribution per accepted conversion
break_even_ROAS = 1 / contribution_margin_rate

marginal_CPA   = incremental spend / incremental accepted conversions
marginal_ROAS  = incremental accepted value / incremental spend
```

🟢 **FAKT** (deterministik moliya matematikasi). Qaytarish, firibgarlik, bekor qilinish, dublikat lead bo'lsa — **net accepted value** ishlatiladi.
**Platforma ROAS'idan foyda chiqarma** — u atribusiya, foyda emas ([[blended-roas-net-cash]]).

## 2. Byudjet taqsimoti ketma-ketligi

1. Majburiy xarajatlar va o'lchash xarajatini ajrat.
2. **Ijobiy marginal hissa** dalili bor kampaniyalarni himoya qil — to'yinganlik (saturation) va naqd pul cheklovini hisobga olib.
3. Eksperimentlarni **e'lon qilingan gipoteza + minimal aniqlanadigan effekt + qaror sanasi + to'xtatish sharti** bilan moliyalashtir.
4. Zaxira faqat aniq ishlatilishi bo'lsa saqlanadi.
5. Qayta taqsimlash — **eng zaif marginal imkoniyatdan**, "eng yomon o'rtacha CPA"dan emas.

> "70/20/10" (isbotlangan/test/eksperiment) — **operator siyosati**, default emas. Tanlangan split va sababi hujjatga yoziladi.

## 3. Scale darvozasi — 6 shart (hammasi bajarilishi kerak)

- [ ] Konversiya va daromad ma'lumoti tegishli **lag**dan o'tgan
- [ ] Tracking, consent, policy, inventar va landing **sog'lom** (natija talqin qilinadi)
- [ ] **Marginal** samaradorlik egasi tasdiqlagan iqtisod chegarasi ichida
- [ ] Kampaniya taklif qilingan byudjet/bid o'zgarishiga **eligible**
- [ ] Reklama beruvchi learning/delivery/**naqd pul** volatilligini ko'tara oladi
- [ ] **Before/after o'lchov, tekshirish oynasi va rollback trigger** mavjud

## 4. Qadamlar (o'lcham va vaqt)

- **Vertikal:** byudjet **20-30%** dan oshmas, har **2-3 kunda** (learning'ni buzmaslik) — 🟡 amaliyot qoidasi.
- **Gorizontal:** yangi auditoriya / joylashuv / lookalike bilan **dublikat**; har yangi creative round **yangi ad set**da (Andromeda scalability — [[andromeda-scalability-signal]]).
- **Bir vaqtda ikkalasi birdan qilinmaydi** (natija sababi ajralmaydi).
- O'lcham/vaqt **platforma simulyatsiyasi + hisob tarixi + konversiya sikllari + blast-radius**dan olinadi — **universal foiz xavfsiz emas**.

## 5. Pause / kamaytirish intizomi

**"CPA maqsadning N barobari" bo'ldi deb to'xtatma.** Avval tekshir: konversiya lag, tracking uzilishi, kichik namuna, lead sifati (pastga qarab), mavsumiylik, boshqa aktiv eksperimentga kerakmi.

Darhol to'xtatish faqat: egasi belgilagan **runaway-spend shifti**, policy/huquqiy xavf, buzilgan destination, tasdiqlangan tracking buzilishi, ruxsatsiz delivery. **Eng kichik qaytariladigan harakat** tanlanadi.

## 6. Kill / Keep / Scale (amaliy qoidalar)

Statistik yetarliliksiz qaror yo'q — **1 kunlik ma'lumot bilan qaror yo'q**.

| Qaror | Shart |
|---|---|
| 🔴 **KILL** | CPA maqsaddan **3x**, konversiya 0 · yoki 3+ kun barqaror **2x** va tendensiya yo'q · yoki CTR nisha o'rtachasidan **2x** past + 1000+ ko'rsatish |
| 🟡 **KEEP** | CPA maqsad atrofida (±30%), hajm kichik → 2-3 kun ko'proq · yoki learning tugamagan → **tegmaymiz** |
| 🟢 **SCALE** | CPA maqsaddan past, **3 kun barqaror, 15+ konversiya** |

🟡 **TAJRIBA** — operator amaliyoti; koeffitsiyentlar nishaga qarab sozlanadi.
Har kill/scale qarori **sababi bilan `journal/`** ga yoziladi.

## 7. Byudjet mantiqi (Meta rasmiy tavsiyalari)

- Minimal boshlang'ich: **$5** va **≥6 kun**; byudjet **≥7 kunga** yetsin
- Kunlik byudjet **75% gacha oshib ketishi mumkin**; haftalik sarf 7× kunlikdan oshmaydi
- Ad set auditoriyasi **≥2 mln** (UZ: shahar darajasida ko'pincha yo'q → butun mamlakat + broad)
- Impressiya uchun kuniga **≥$1**; **cost cap** bo'lsa kunlik byudjet ≥ **5× cap**
- **50 event / 7 kun** har bir ad set uchun alohida → 4 ad set = haftasiga 200 event. Kichik byudjetda **1-2 ad set**dan ortiq ochma

🟢 Manba: https://www.facebook.com/business/ads/pricing

## 8. Change packet (har byudjet o'zgarishi uchun)

Joriy va taklif summalar · ta'sirlangan obyekt ID'lari · iqtisodiy sabab · kutilayotgan effekt · noaniqlik · learning ta'siri · egasi · tasdiq · **tekshirish sanasi** · **rollback chegarasi** · idempotency key.
**Tasdiq (mutation gate) bo'lmaguncha — taklif draft.**

## 9. Katta byudjetda eng ko'p uchraydigan to'siqlar

- **Kreativ quvvat (throughput)** — scaling'ni birinchi bo'lib kreativ ishlab chiqarish to'sadi ([[kreativ-sikl]])
- **Auditoriya to'yinganligi / TAM** → yangi angle/audience/offer ([[scaling-cheklovlari]])
- **Chastota** portlashi → CPM o'sadi, CTR tushadi → yangilash **rejaga ko'ra**, natija tushgandan keyin emas
- **Cash-flow** — katta byudjetda learning volatilligi naqdga tegadi
- **Atribusiya bahsi** — kanal taqqoslashda bitta haqiqat manbai: **CRM yoki MER** ([[blended-roas-net-cash]])

## Manba

- `wiki/meta-playbook-uz.md` (§3-5)
- `claude-ads-main/ads/references/budget-allocation.md` (2026-07-11)
- `claude-ads-main/local/raw/claudes-bilim/marketolog/KNOWLEDGE.md` §6
