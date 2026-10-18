---
description: Meta Ads auditoriya arxitekturasi — 4-qatlamli voronka, Interest Cluster, Exclusion matritsasi, Overlap va Saturation hisobi
argument-hint: <nisha: ecom|edu|real-estate|medical|b2b|beauty|auto|local> <kunlik_byudjet> [mijoz]
---

# /auditoriya — Meta Ads Auditoriya Arxitektori (Andromeda 2 + UZ Standarti)

Vazifa: **$ARGUMENTS**

## 1. Avtomatik Hisob-Kitob (`tools/meta-audience.py`)

Ishni boshlashdan oldin deterministik Meta Audience dvigatelini ishga tushiring:

```powershell
# 1. 4-qatlamli auditoriya rejasi va Exclusion matritsasi
py -3 tools/meta-audience.py architect --niche <niche> --daily-budget <byudjet> --geo <tashkent|regions|uzbekistan> --has-pixel --has-crm

# 2. Sohaga mos Interest Cluster va to'lov qobiliyati (Solventnost) filtrlari
py -3 tools/meta-audience.py interests --niche <niche>

# 3. Ustma-ust tushish (Overlap <= 20%) va Charchash (Saturation) tekshiruvi
py -3 tools/meta-audience.py overlap --size-a <A> --size-b <B> --shared <S>
py -3 tools/meta-audience.py saturation --audience-size <hajm> --daily-budget <byudjet> --cpm 3.2
```

## 2. Qat'iy Qoidalar ([[meta-auditoriya-arxitekturasi]])

1. **Geo-Split:** Toshkent shahri va Viloyatlar bitta CBO kampaniyada aralashtirilmaydi.
2. **Til Izolyatsiyasi:** O'zbek (lotin/kirill) va Rus tilidagi kreativlar alohida ad setlarga bo'linadi.
3. **Exclusion Matritsasi:** Barcha sovuq (TOF) ad setlardan `Purchase_180d`, `CRM_Active_Clients` va `LeadForm_Submitted_90d` istisno qilinadi; ASC da `Existing Customer Cap = 25%`.
4. **Toza LAL Manbasi:** Lookalike (1%, 1-2%) faqat CRM/CAPI orqali tasdiqlangan to'lovchi mijozlar bazasidan quriladi.

## 3. Natija

- Fayl: `outputs/<mijoz>/<sana>-meta-auditoriya.md`
- Jadval: Cold / Warm / Hot ad setlar, kunlik byudjet, Interest/Behavior stack, Custom Audience oynalari (`7d/14d/30d/90d/180d`) va Exclusion ro'yxati.
