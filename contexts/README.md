---
name: contexts-readme
description: "ECC Dynamic Context Modes — vazifa turiga qarab agent xulq-atvori va ustuvorliklarini o'zgartiruvchi kontekst rejimlari"
tags: [context, ecc, router, mode]
source: "affaan-m/ECC contexts/ arxitekturasi asosida Tyrion v3.0 uchun"
updated: 2026-10-17
---

# 🎛️ TYRION CONTEXT MODES (`contexts/`)

`affaan-m/ECC` arxitekturasidagi **Dynamic Context Injection** tamoyili asosida Tyrion 5 ta maxsus ish rejimiga ega. Vazifa boshlanganda faqat tegishli kontekst rejimi yuklanadi:

| Rejim fayli | Qachon yuklanadi | Asosiy fokus |
|---|---|---|
| `contexts/audit-mode.md` | `/audit`, `/tracking`, `/shield` | Faqat o'qish (read-only), manbali dalil, Zero-Findings ruxsati, M1–M24 nazorat |
| `contexts/launch-mode.md` | `/budget`, `/voronka`, yangi kampaniya | 24 soatlik tezkor launch, 1-5-5 Sandbox, Spend-Guard, Pixel+CAPI deduplikatsiya |
| `contexts/scale-mode.md` | `/scale`, `/auditoriya`, katta byudjet | 20% byudjet qoidasi, gorizontal klonlash, Overlap <20%, FTIR >=60% charchoq radari |
| `contexts/creative-mode.md` | `/kreativ`, Reels skript, reklama matni | Andromeda 2 signal xilma-xilligi, 3s Hook, 3 til (UZ Lotin / Kirill / RU) |
| `contexts/uzbekistan-market.md` | O'zbekiston bozori (default `uz`) | Telegram Bot/DM + AmoCRM voronka, Payme/Click/Uzum Nasiya, Solventnost filtrlari |

**Bog'liq:** [[AGENTS.md]] · [[CLAUDE.md]] · [[sop-xarita]]
