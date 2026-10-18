---
name: campaign-launch-packet-template
description: "Kampaniya ishga tushirish paketi andozasi — 3 bosqichli sinov narvoni, byudjet, nomlash standarti va favqulodda to'xtatish (rollback)"
tags: [template, launch, change-packet, safety]
source: "rules/40-xavfsizlik-va-hisob.md"
updated: 2026-10-17
---

# 🚀 Kampaniyani Ishga Tushirish Paketi (Change Packet)

- **Mijoz:** `[Mijoz nomi]`
- **Platforma:** `[Meta Ads | Google Ads | Telegram Ads]`
- **Sanasi:** `YYYY-MM-DD`
- **Mas'ul:** Tyrion Conductor

---

## 1. 3 Bosqichli Sinov Narvoni (Testing Ladder)

```
[Phase 1: Sandbox (10-20% byudjet)] ──(CPA $\le$ Target)──> [Phase 2: Validation] ──> [Phase 3: Scale]
```

- **Hozirgi Bosqich:** Phase 1 (Sandbox)
- **Ajratilgan Test Byudjeti:** `$0.00 / kun`
- **Maksimal Stop-Loss Chegarasi:** `$0.00` (agar 0 konversiya bilan shu miqdor yeyilsa — to'xtatish)

---

## 2. Kampaniya Sozlamalari

- **Kampaniya Nomi:** `[TYRION]_[Mijoz]_[Platforma]_[Maqsad]_[Angle]_[Sana]`
- **Targeting / Auditoriya:**
  - Kiritilgan: `[Auditoriya / Qidiruv so'zlari / Telegram kanallari]`
  - Istisnolar (Exclusions): `[O'tgan 30 kunlik xaridorlar / Negatives]`
- **Taklif va UTM URL:**
  `https://example.com/landing?utm_source=meta&utm_medium=cpc&utm_campaign=sandbox_angle1`

---

## 3. Qat'iy Promot va Kill Qoidalari

1. **KILL Qoidasi:** Agar ad set 2x Target CPA miqdorida spend qilsa-yu, 0 ta konversiya bersa $\to$ **PAUSE**.
2. **PROMOTE Qoidasi:** Agar CPA $\le$ Target CPA va 50 ta konversiya olsa $\to$ Phase 2/3 (CBO/Scale) ga o'tkazish.

---

## 4. Favqulodda Qaytish Rejasi (Emergency Rollback)

Agar kampaniya kutilmagan yuqori CPA yoki xatolik bersa:
1. Reklama kabinetiga kirish.
2. `[Kampaniya nomi]` ni tanlash va statusini **PAUSED** ga o'tkazish.
3. Hisob balansi va sarf limitini tekshirish.
