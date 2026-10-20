---
name: uzluksiz-organish-instinktlar
description: "ECC continuous-learning naqshi asosida Tyrion instinktlar tizimi — kampaniya saboqlarini yig'ish, ishonch balli (1-5) bilan baholash va wiki/memory qatlamiga ko'tarish"
tags: [instinkt, organish, memory, ecc, tizim]
source: "raw/2026-09-16-ecc-naqshlar-tahlili.md + affaan-m/ECC continuous-learning-v2 (2026-10-17)"
updated: 2026-10-17
---

# 🧬 Uzluksiz O'rganish va Instinktlar Tizimi

> **Muammo:** Kampaniya auditi yoki kreativ sprint yakunlangach, topilgan qimmatli naqshlar chat tarixida qolib ketadi. Keyingi sessiyada agent xuddi shu xatoni qayta takrorlaydi.
> **Yechim:** Har bir tasdiqlangan marketing yoki tizim sabog'i **atomik instinkt** sifatida `manifests/instincts.json` reestriga yoziladi va `tools/instincts.py` orqali boshqariladi.

## Instinkt Anatomiyasi

Har bir instinkt 5 ta majburiy maydondan iborat ([[agent-os-qatlami]]):

| Maydon | Tavsif | Misol |
|--------|--------|-------|
| `id` | Qisqa unikal identifikator (kebab-case) | `meta-asc-existing-cap-25` |
| `domain` | Yo'nalish (`meta`, `google`, `telegram`, `kreativ`, `tracking`, `tizim`) | `meta` |
| `trigger` | Qaysi holatda faollashadi (`When...`) | `Advantage+ Shopping (ASC) kampaniyasi yoqilganda` |
| `action` | Qanday qoida qo'llanadi (`Do...`) | `Existing customer budget cap 25-30% qilib cheklansin` |
| `confidence` | Dalil kuchi (`1` = ilk kuzatuv ... `5` = ko'p marta tasdiqlangan qonuniyat) | `5` |

## Hayot Sikli (`/learn` → Instinkt → Wiki)

1. **Ajratib olish (`/learn`):** Sessiya yoki haftalik hisobot ([[haftalik-audit]]) yakunida `py -3 tools/instincts.py add` orqali yangi saboq kiritiladi.
2. **Tekshirish (`confidence 1 → 3`):** Gipoteza ikkinchi mijoz yoki kampaniyada ham tasdiqlansa, ishonch balli oshiriladi ([[dalil-tasnifi]]).
3. **Ko'tarish (`promote`, `confidence >= 4`):** Ishonch balli 4–5 ga yetgan instinkt `py -3 tools/instincts.py promote <id>` buyrug'i bilan `MEMORY.md` §6 (Saboqlar) bo'limiga yoki `wiki/` da alohida atomik qaydga aylantiriladi.

## Anti-Patterns (WRONG vs CORRECT)

- **FAIL: WRONG** — Bitta tasodifiy kunlik CTR o'zgarishini umumiy qoida sifatida `memory.md` ga yozib qo'yish ([[kontekst-xatolari|Poisoning]]).
- **PASS: CORRECT** — Kamida statistik ahamiyatli namuna (masalan, $\ge 50$ konversiya yoki 7 kunlik oyna) va aniq manba (`evidence`) bilan instinkt sifatida ro'yxatga olish ([[00-manba]]).

## Manba

- `raw/2026-09-16-ecc-naqshlar-tahlili.md` — ECC continuous learning tahlili
- [[agent-os-qatlami]] · [[haftalik-audit]] · [[00-manba]] · [[50-topshirish-dod]] · [[verification-loop-6-bosqich]]
