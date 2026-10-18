---
name: "20-token-gigiyena"
description: Token va kontekst tejash — graf avval, butun papkani o'qimaslik, 60% qoidasi, MCP faqat kerak bo'lganda
tags: [rules, token, kontekst]
source: "wiki/token-gigiyenasi + ECC context optimization (2026-10-18)"
updated: 2026-09-16
---

# 🪙 20 — TOKEN GIGIYENASI

> Kontekst — cheklangan resurs. Uni to'ldirish sifatni tushiradi, narxni oshiradi ([[token-gigiyenasi]]).

## Bilim olish tartibi (arzon → qimmat)

1. **Qidiruv avval (0 token):** `py -3 tools\brain-search.py search "<so'z>"` — deterministik, LLM'siz. Graf kerak bo'lsa `tools\gy.cmd build` (0 token, lahzali) yoki `tools\gy.cmd query "<savol>" --budget 1200`.
2. **Ko'rsatilgan qayd:** faqat `INDEX.md` dagi kerakli fayl o'qiladi.
3. **Xom manba (`raw/`, `vedio bilimlar/youtubedagilar/`)** — faqat aniq bir manba kerak bo'lganda.
4. ❌ **Butun papkani yoppasiga o'qish** — taqiqlanadi (bir `extract` yuz minglab token yeydi).

## Qoidalar

| Qoida | Nega |
|-------|------|
| Butun vaultni skanerlamaslik | `wiki/` 100 qayd, `vedio bilimlar/youtubedagilar/` 16 transkript — kerak emas |
| Kontekst **60%** ga yetganda: 150 so'zli xulosa → yangi sessiya | [[session-handoff]] |
| Modelni `/model` bilan almashtirmaslik | prompt cache nollanadi, narx oshadi |
| Og'ir MCP (`code-review-graph`) — **arxivga olindi (2026-09-20)** | har sessiyada ~17–18k token + 103 MB disk yeydi; bilim vaultiga keraksiz |
| Kontekst rejimini tanlab yuklash (`contexts/`) | 40 KB → 8 KB fokuslangan kontekst |
| Og'ir "o'ylash" — conductor'da, yengil ish — worker'larda | qadam soni = vaqt va pul |
| Uzun tanaffusdan keyin yangi sessiya | eski kontekst aralashadi |

## Tekshirish

- Tizim va token holati: `python3 tools/tyrion.py status`

**Bog'liq:** [[rules/README|Qoidalar indeksi]] · [[prompt-caching]] · [[session-handoff]] · [[AGENTS.md]]
