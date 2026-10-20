---
name: "50-topshirish-dod"
description: Topshirish darvozasi (DoD) — natija fayl bo'ladi, manba ko'rsatiladi, checklist va verifier, LOG/INDEX yangilanadi
tags: [rules, dod, sifat, topshirish]
source: "claude-ads-main/control-plane/RELEASE_REQUIREMENTS.md + CLAUDE.md DoD (2026-09-16)"
updated: 2026-09-16
---

# ✅ 50 — TOPSHIRISH DARVOZASI (DoD)

> "Tayyor" deyish — **dalil** talab qiladi, ishonch emas. Tekshirilmagan ish topshirilmaydi.

## Har topshiriq uchun majburiy

| # | Talab | Tekshirish |
|---|-------|-----------|
| 1 | **Natija fayl** — `outputs/` ga yozilgan (chatda qolmagan) | `outputs/README.md` tartibi |
| 2 | **Manba satri** — har raqam/fakt manbasi bilan | [[00-manba]] |
| 3 | **Aniqlik belgisi** — taxmin bo'lsa "taxmin" deb yozilgan | — |
| 4 | **Checklist** — ROAS / Pixel-CAPI / UTM / Policy holati ko'rsatilgan | quyida |
| 5 | **Verifier** — katta ishda `release-verifier` bot tekshiruvi | [[AGENTS.md]] §1 |

## Mijoz ishi uchun checklist (4 band)

- **ROAS / break-even** — kuzatiladigan metrika aniqmi (blended ROAS + net cash)?
- **Pixel / CAPI** — o'lchov ishlayaptimi, event'lar to'g'rimi?
- **UTM** — trafik manbasi kuzatiladimi (aks holda Telegram'da yo'qoladi)?
- **Policy** — matn/kreativ Meta-Google qoidalariga mosmi?

## Tizim ishi uchun (Tyrion o'zi)

- `py -3 tools\vault-audit.py` — 0 muammo
- `py -3 tools\catalog.py check` — katalog mos
- `py -3 tools\doctor.py` — umumiy hisobot yashil
- Yangi bilim → `INDEX.md` + `LOG.md` yangilangan
- Kod o'zgargan bo'lsa → `tests/` da testi bor

## Tugagach

1. `LOG.md` tepasiga bitta qator: `sana | nima qilindi | natija`
2. Mijoz ishi bo'lsa — `journal/<mijoz>.md` ga qaror va sababi
3. Xato topilgan bo'lsa — `memory.md` §6 Saboqlar

**Bog'liq:** [[rules/README|Qoidalar indeksi]] · [[00-manba]] · [[40-xavfsizlik-va-hisob]] · [[haftalik-audit]]
