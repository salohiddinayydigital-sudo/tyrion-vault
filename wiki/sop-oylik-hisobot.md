---
name: sop-oylik-hisobot
description: "SOP: oylik marketing hisoboti — kanallar bo'yicha raqam, voronka taqsimoti, uch savol, keyingi oyga 3 harakat, biznes tilida yozish"
tags: [sop, hisobot, metrika, mijoz]
source: "claude-ads-main/local/raw/claudes-bilim/marketolog/PLAYBOOKS.md (PB-7)"
updated: 2026-09-20
---

# SOP — Oylik marketing hisoboti

> Bog'lanishlar: [[mijoz-ishga-tushirish]] · [[unit-iqtisodiyot-formulalari]] · [[voronka-metrikalari]] · [[sop-kampaniya-diagnostika]]

**Qachon:** har oy oxirida, yoki mijozga natija ko'rsatish kerak bo'lganda.

## Kirish ma'lumotlari

Oy davomidagi barcha kanal raqamlari · xarajat · sotuv · o'tgan oy raqamlari.

## Qadamlar

1. **Raqamlarni yig'** — har kanal bo'yicha: xarajat, natija (lead/sotuv), CAC, ROAS. **Manbani ko'rsat** (qayerdan olingan).
2. **Voronka bo'yicha taqsimla** — qaysi bosqichda nima o'zgardi.
3. **O'tgan oy bilan solishtir** — foiz o'zgarish bilan.
   ⚠️ **Bitta oy trend emas:** 3 oydan kam ma'lumot bo'lsa, "trend" deb atama.
4. **Uch savolga javob ber:** Nima ishladi? Nima ishlamadi? Nega?
5. **Keyingi oy uchun 3 ta harakat** — ustuvorlik tartibida, har birida kutilayotgan ta'sir va **kim bajaradi**.
6. **Biznes tilida yoz.** ❌ "Organik trafik 34% o'sdi" → ✅ "qidiruvdan oyiga 40 ta yangi murojaat keldi, o'tgan oy 30 ta edi".
   Mijoz marketing metrikasi bilan emas, **murojaat va pul** bilan o'ylaydi.

## Chiqish artefakti

`HISOBOT-<oy>.md`:

```markdown
## <Oy> natijalari
### 1. Asosiy raqamlar (o'tgan oy | bu oy | farq | maqsad)
### 2. Kanal bo'yicha (sarf | lead | CPL | mijoz | CPA | ROAS)
### 3. Nima ishladi (3 ta, raqam bilan)
### 4. Nima ishlamadi (2 ta, sababi bilan)
### 5. Keyingi oy: 3 ta ustuvor harakat
### 6. Qaror talab qiladigan savol (mijozga)
```

## Muvaffaqiyat mezoni

Mijoz hisobotni o'qib **"endi nima qilamiz" deb so'ramaydi** — javob hisobotda bor.

## Manba

- `claude-ads-main/local/raw/claudes-bilim/marketolog/PLAYBOOKS.md` PB-7
