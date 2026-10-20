---
description: Meta Ads auditoriya arxitekturasi — 4-qatlamli voronka, 6-statusli Detailed Targeting Accuracy tekshiruvi, Exclusion matritsasi, Overlap (<20%) va Saturation hisobi
argument-hint: <nisha: ecom|edu|real-estate|medical|b2b|beauty|auto|local> <kunlik_byudjet> [mijoz]
---

# /auditoriya — Meta Ads Auditoriya & Detailed Targeting Arxitektori (Andromeda 2 + UZ Standarti)

Vazifa: **$ARGUMENTS**

## 1. Avtomatik Hisob-Kitob (`tools/meta-audience.py` & `tools/meta-targeting-engine.py`)

Ishni boshlashdan oldin deterministik Meta Audience va Detailed Targeting Accuracy dvigatellarini ishga tushiring:

```bash
# 1. 4-qatlamli auditoriya rejasi va Exclusion matritsasi (unit-ekonomika bilan)
python3 tools/meta-audience.py architect --niche <niche> --daily-budget <byudjet> --aov <chek> --margin-pct <marja> --geo <tashkent|regions|uzbekistan> --has-pixel --has-crm

# 2. Detailed Targeting (Interest/Behavior) variantlarini rasmiy Meta API orqali qidirish va tekshirish
python3 tools/meta-targeting-engine.py search --product "<mahsulot>" --niche <niche> --account-id <act_id>

# 3. Ustma-ust tushish (Static Pool Overlap < 20%) va Charchash oynasi (Saturation Sensitivity Window)
python3 tools/meta-audience.py overlap --size-a <A> --size-b <B> --shared <S>
python3 tools/meta-audience.py saturation --audience-size <hajm> --daily-budget <byudjet> --cpm 3.2
```

## 2. Qat'iy Qoidalar ([[meta-auditoriya-arxitekturasi]] · [[meta-ads-interest-api]])

1. **Uydirma Interest Taqiqlanadi:** Hech qachon tasdiqlanmagan AI taxminini yoki statik lug'atni (`RELATED_UNVERIFIED`) Meta Ads Manager'da mavjud (`VERIFIED_AVAILABLE`) deb ko'rsatmang.
2. **Solventnost Gipotezasi:** `iPhone`, `Frequent International Travelers`, `Page Admin` kabi signallar daromad kafolati emas, balki sinovdan o'tkaziladigan marketing gipotezasidir (`MARKETING_HYPOTHESIS`).
3. **Geo-Split va Til Izolyatsiyasi:** Toshkent shahri va Viloyatlar bitta CBO kampaniyada aralashtirilmaydi; O'zbek (lotin/kirill) va Rus tilidagi kreativlar alohida ad setlarga bo'linadi.
4. **Exclusion Matritsasi:** Barcha sovuq (TOF) ad setlardan `Purchase_180d`, `CRM_Active_Clients` va `LeadForm_Submitted_90d` istisno qilinadi; ASC da `Existing Customer Cap = 25%`.

## 3. Natija Format

1. **Live Tekshiruv Holati (`live_check_status`)**
2. **Tasdiqlangan Targeting Variantlari (`VERIFIED_AVAILABLE` / `FOUND_NOT_VALIDATED`)**
3. **Eskirgan yoki Birlashtirilgan Variantlar (`UNAVAILABLE_OR_CONSOLIDATED`)**
4. **Tasdiqlanmagan Mazmunan Mos G'oyalar (`RELATED_UNVERIFIED`)**
5. **Topilmagan So'rovlar (`NOT_FOUND`)**
6. **Tavsiya Etilgan Auditoriya Kombinatsiyasi va Cheklovlar**
