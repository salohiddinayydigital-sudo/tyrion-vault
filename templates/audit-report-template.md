---
name: audit-report-template
description: "Rasmiy audit hisoboti andozasi — xulosa, topilmalar jadvali, jiddiylik darajasi, dalil va teskari qadamlar (DoD muvofiq)"
tags: [template, audit, hisobot, dod]
source: "rules/50-topshirish-dod.md"
updated: 2026-10-17
---

# 🛡️ Reklama Hisobi Auditi Hisoboti

- **Mijoz / Loyiha:** `[Mijoz nomi]`
- **Platforma:** `[Meta Ads | Google Ads | Telegram Ads]`
- **Audit Sanasi:** `YYYY-MM-DD`
- **Tahlil qilingan davr:** `[Sana oralig'i, masalan: Oxirgi 30 kun]`
- **Auditor / Conductor:** Tyrion AI OS

---

## 1. Ijroiya Xulosasi (Executive Summary)

> **Asosiy xulosa (3 qator):**
> 1. Akkauntning umumiy holati va sarflangan byudjet samaradorligi.
> 2. Asosiy muammo va byudjet isrofi aniqlangan nuqta.
> 3. Eng tezkor 3 ta tavsiya va kutilayotgan moliyaviy natija.

### Asosiy Metrikalar

| Metrika | Hozirgi Ko'rsatkich | Soha / O'z Tarixi Brenchmarki | Farq / Holat |
|---|---|---|---|
| **Jami Sarf (Ad Spend)** | $0.00 | — | — |
| **Blended ROAS** | 0.0x | $\ge 2.5\text{x}$ | ⚠️ Diqqat |
| **Haqiqiy CPA (Cost Per Acquisition)** | $0.00 | $\le \$15.00$ | ⚠️ Qimmat |
| **CAPI / Tracking EMQ Skori** | 0.0 / 10 | $\ge 7.0$ | ❌ Kritik |
| **Charchash (FTIR)** | 0% | $\ge 60\%$ | ⚠️ Charchagan |

---

## 2. Topilmalar va Kamchiliklar Reestri

| ID | Soha | Natija | Jiddiylik | Topilma & Dalil | Tavsiya etilgan Amaliy Qadam | Teskari Qadam (Rollback) |
|---|---|---|---|---|---|---|
| **F01** | Tracking | ❌ FAIL | **CRITICAL** | Pixel va CAPI deduplikatsiyasi yo'q (`event_id` yetishmaydi, 2x takror hisoblash) | Yagona `event_id` parametrini GTM va backendda ulash | GTM oldingi versiyasiga qaytarish |
| **F02** | Struktura | ⚠️ FAIL | **HIGH** | Byudjet 14 ta ad setga maydalangan, hech biri haftasiga 50 ta konversiya olmaydi | 1-5-5 arxitekturasiga konsolidatsiya qilish | Eski ad setlarni qayta yoqish |
| **F03** | Kreativ | ⚠️ FAIL | **MEDIUM** | Barcha e'lonlar bir xil formatda; FTIR 38%, chastota 3.4 ga chiqqan | 3 ta yangi TOF Problem/Solution burchagini kiritish | Eski kreativlarga qaytish |

---

## 3. O'zgarishlar Paketi (Inson tasdiqlaydigan harakatlar)

> [!IMPORTANT]
> `rules/40-xavfsizlik-va-hisob.md` qoidasiga ko'ra, sun'iy intellekt hisobni bevosita o'zgartirmaydi. Quyidagi qadamlar operator tomonidan ko'zdan kechirilib tasdiqlanadi:

1. **1-Qadam (Bugun):** `[Aniq harakat va kampaniya nomi]`
2. **2-Qadam (48 soat ichida):** `[Byudjet yoki ad set harakati]`
3. **Kuzatuv davri:** `[7 kunlik monitoring oynasi]`
