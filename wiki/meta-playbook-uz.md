---
name: meta-playbook-uz
description: Meta Ads (Facebook/Instagram) $1,000+ loyihalar uchun ish yuritish playbook — tuzilma, learning phase, byudjet, diagnostika, kill/keep/scale
source: amaliyot (tyrion vault bilimlari asosida)
tags: [local, meta-ads, playbook, byudjet]
updated: 2026-09-03
---

# 🎯 META ADS $1K PLAYBOOK (o'zbekcha)

> 📖 **O'qish:** faqat Meta kampaniya qurish / diagnostika / kill-keep-scale qarorlarida. `ads/SKILL.md` routing'ida plan/meta vazifasida yuklanadi.

> Ushbu fayl — Meta loyihalarini `/ads` bilan boshqarishda **lokal ish yuritish standarti**.
> Platforma auditlari va tekshiruvlar `skills/ads-meta` + `ads/references/meta-audit.md` da — bu fayl ularni to'ldiradi.

---

## 1. KAMPANIYA TUZILMASI (3 daraja)

```
CAMPAIGN   → Maqsad (objective) + byudjet (CBO/Advantage+ bo'lsa)
  └─ AD SET → Auditoriya + joylashuv + optimizatsiya hodisasi + byudjet (ABO)
       └─ AD → Kreativ + primary text + headline + CTA + destination
```

**Qoida:** har darajada faqat **bitta o'zgaruvchi** sinaladi.
Ad set'da auditoriya ham, kreativ ham o'zgarsa — natija hech narsani isbotlamaydi.

## 2. LEARNING PHASE (o'rganish bosqichi)

- Ad set optimizatsiya hodisasi bo'yicha **~50 konversiya / 7 kun** to'plamaguncha "Learning"da
- Learning'dagi ad set'ni tahrirlash → **learning reset** (natija nolga qaytadi)
- Dastlabki 3–4 kun **tegmaymiz** — sabr strategiya
- Byudjet juda kichik bo'lsa "Learning Limited" → ad set sonini kamaytirish, byudjetni jamlash
- CBO: byudjetni kampaniya darajasida birlashtirish — ad set'larning o'zi o'rganishi uchun

## 3. $1,000 BYUDJET TAQSIMOTI (70/20/10)

| Ulush | Summa | Maqsad |
|-------|-------|--------|
| **70%** | ~$700 | Isbotlangan kampaniya (scaling) |
| **20%** | ~$200 | Yangi kreativ / auditoriya testi |
| **10%** | ~$100 | Riskli eksperiment (yangi format, angle) |

Byudjet mijozdan kelganda: birinchi hafta asosiy e'tibor — **test bosqichi**, 70% qoidasi 2-haftadan.

## 4. METRIKALAR ZANJIRI (voronka mantiqi)

```
Ko'rsatish → Bosish → Sahifa → Lid → Sotuv
   CPM        CTR      LP CVR    CPL    CPA / ROAS
```

Har bir metrik o'zidan oldingi bosqich salomatligini ko'rsatadi — muammoni **qayerdan** izlashni bilish kerak:

| Belgi | Muammo qayerda | Birinchi harakat |
|-------|----------------|------------------|
| CPM juda baland | Tor auditoriya / past kreativ sifat / qizigan auktsion | Auditoriyani kengaytirish, yangi kreativ |
| CTR past | **Hook ishlamayapti** | Yangi hook, yangi vizual |
| CTR yaxshi, lid yo'q | Landing / offer / forma | Sahifa va offerni tekshirish |
| Lid arzon, sotuv yo'q | Lid sifati past — auditoriya noto'g'ri | Auditoriyani toraytirish, savol qo'shish |
| Frequency > 3 (qisqa muddat) | Auditoriya "kuygan" | Kreativ almashtirish / kengaytirish |
| Boshida yaxshi, keyin o'ldi | Kreativ charchagan (fatigue) | Kreativ rotatsiya |
| Telegram DM'ga o'tish past | Lead magnit / oferta kuchsiz, ishonch yo'q | Ofеrta + ishonch signallari (lokal kontekst!) |

## 5. QAROR QOIDALARI (Kill / Keep / Scale)

Statistik yetarlilikka asoslanadi — **1 kunlik ma'lumot bilan qaror yo'q**.

### 🔴 KILL
- CPA maqsaddan **3x** ko'p sarfladi, konversiya **0**
- 3+ kun ishladi, CPA maqsaddan barqaror **2x** yuqori, tendensiya yaxshilanmayapti
- CTR nishadagi o'z o'rtachasidan **2x** past va 1,000+ ko'rsatish bor

### 🟡 KEEP
- CPA maqsad atrofida (±30%), hajm kichik → 2–3 kun ko'proq ma'lumot
- Learning phase tugamagan → **tegmaymiz**

### 🟢 SCALE
- CPA maqsaddan past, 3 kun barqaror, 15+ konversiya
- **Vertikal:** byudjet 20–30% dan oshmay, har 2–3 kunda (learning'ni buzmaslik)
- **Gorizontal:** yangi auditoriya / joylashuv / lookalike bilan dublikat
- Bir vaqtda ikkalasini birdan **qilmaymiz**

> Har kill/scale qarori sababi bilan `journal/` ga yoziladi.

## 6. BENCHMARK OGOHLANTIRISH

> ⚠️ Universal "yaxshi CPM/CTR" yo'q — nisha, geo, mavsum, offerga qarab bir necha barobar farq qiladi.
> Tashqi benchmark bilan emas, **akkauntning O'Z tarixi** bilan solishtiriladi (ads-meta audit ham shu tamoyilda).

## 7. MAHALLIY MOSLASHUV (O'zbekiston)

- Landing/lead forma → **Telegram DM/bot** destination (email emas)
- Ad set tili bo'yicha bo'linadi: o'zbekcha / ruscha / kirill segmentlar
- CPA maqsadi: mijozning konversiya ta'rifi bilan kelishilgan bo'lishi shart (qo'ng'iroqmi, DM'mi, forma?)
- Atributsiya cheklovlarini (piksel/CAPI bo'lmasa) boshida ochiq aytish
- Batafsil: [[claude-ads-main/local/ozbekiston-konteksti|O'zbekiston konteksti]]

---

**Bog'liq:** [[meta-kampaniya-tuzilmalari]] · [[learning-phase-qoidalari]] · [[meta-auditoriya-arxitekturasi]] · [[ozbekiston-konteksti]]
