---
name: agent-os-qatlami
description: "Tyrion ildizidagi agent-OS qatlami (2026-09-16): AGENTS.md shartnomasi, rules/, commands/, hooks/, katalog, doctor, testlar — nima uchun qurildi va ECC'ning qaysi naqshlari olindi, qaysilari ataylab rad etildi"
tags: [arxitektura, agent-os, sifat, tizim]
source: "affaan-m/ECC (github, v2.2.1) tahlili — raw/2026-09-16-ecc-naqshlar-tahlili.md (2026-09-16)"
updated: 2026-09-16
---

# Agent-OS qatlami (Tyrion)

2026-09-16 da Tyrion ildiziga **agent-OS qatlami** qo'shildi: tizim endi o'zini o'zi
tekshiradi, raqamlari qo'lda yozilmaydi va nusxalar bir-biridan uzoqlashmaydi.

## Qatlamlar

| Qatlam | Joy | Vazifa |
|--------|-----|--------|
| Shartnoma | `AGENTS.md` | Har qanday harness uchun qatlamlar, 34 agent, ish tartibi, tamoyillar |
| Qoida | `rules/` (6) | Manba · til · token · UZ kontekst · xavfsizlik · DoD — kanonik, nusxa emas |
| Buyruq | `commands/` (6) | `/savol` `/audit` `/kreativ` `/hisobot` `/bot` `/doctor` |
| Hook | `hooks/` | Deterministik nazorat: sessiya holati · ingest · topshirish darvozasi |
| Reestr | `manifests/catalog.json` | Hamma narsaning mashina katalogi — **fayl tizimidan generatsiya** |
| Asbob | `tools/doctor.py` | 11 tekshiruv: bilim · katalog · drift · raqamlar · botlar · graf · sirlar · git · testlar |
| Nazorat | `tests/` (21) | Asboblar testlari (stdlib `unittest`, qo'shimcha o'rnatish yo'q) |

## ECC'dan olingan 5 naqsh

1. **`AGENTS.md` — portativ shartnoma.** Claude'ga bog'liq bo'lmagan qoida fayli; `CLAUDE.md` esa faqat router bo'lib qoladi (ECC'da ham shunday: `AGENTS.md` kanonik, `CLAUDE.md` unga havola).
2. **Katalog = haqiqat manbai.** ECC'dagi `scripts/ci/catalog.js` README/AGENTS.md dagi e'lon qilingan sonlarni fayl tizimi bilan solishtiradi va `--write` bilan tuzatadi. Tyrion'da: `catalog.py check` + `sync-claims` + `doctor` dagi "Raqamlar" tekshiruvi.
3. **Deterministik darvoza.** ECC'ning `delivery-gate` hook'i faqat o'lchanadigan dalilga tayanadi (fayl, sana, regex) — LLM hukmiga emas. Shuning uchun Tyrion hook'i ham "yaxshi yozilganmi" deb baholamaydi, faqat **bajarilgan shartni** tekshiradi.
4. **Qo'shilmagan blok = Bloat.** ECC'da 67 agentda bir xil `Prompt Defense Baseline` bloki nusxalangan va uni hech bir skript in'ektsiya qilmaydi. Tyrion buning aksini qiladi: umumiy qoida **bitta** joyda (`rules/`), agentlar unga havola qiladi.
5. **Metama'lumot — dated reference'da.** Platforma faktlari doimiy qoidaga emas, sanali reference'ga yoziladi ([[00-manba]] ham shuni talab qiladi).

## Ataylab rad etilganlar

| ECC'da bor | Tyrion'da nega yo'q |
|-----------|---------------------|
| 292 skill · 122 rule · 94 command | Bir odam yuritadigan tizim uchun Bloat: har fayl token va e'tibor yeydi |
| 16 harness mirror (`.kiro/`, `.qwen/`, `.trae/`...) | Tyrion bitta ish oqimida ishlaydi (Claude Code + Cursor + Codex + MCP) |
| Install adapterlari, npm paketi, CI matritsasi | Shaxsiy tizim: `tools/install-hooks.py` yetarli |
| Mirror'larni qo'lda sinxronlash | ECC buni ochiq tan oladi ("keeping these subsets in sync is manual") — Tyrion'da `catalog.py sync-mirrors` generatsiya qiladi |

## Tekshirish

```powershell
py -3 tools\doctor.py            # 11 tekshiruv, bitta hisobot (0 xato bo'lishi kerak)
py -3 tools\catalog.py drift     # nusxalar kanonikdan farq qiladimi
py -3 -m unittest discover tests # 21 test
py -3 hooks\tyrion-hook.py dod   # topshirish darvozasi
```

## Saboqlar (qurish paytida topilgan xatolar)

- **YAML/JSON'da `\` — jim qotil.** `source: "..."` qo'shtirnoq ichida `\t` TAB belgisiga aylanadi
  va **xato chiqmaydi**; `install-hooks.py` da ham xuddi shu xato yo'l almashtirishda takrorlandi (dry-run tutdi).
  Yechim: yo'llarda `/`, almashtirishni **parse'dan keyin** qilish, testni regressiya sifatida saqlash ([[token-gigiyenasi]] emas — [[kontekst-xatolari|Clash]] emas, bu sof texnik xato).
- **Nusxa — vaqt bombasi.** 33 charterning 12 tasi ikki joyda farq qilib ketgan edi; kanonik manba aniqlanmaguncha
  hech narsa ustiga yozilmasligi kerak (avval solishtirish, keyin arxiv, keyin sinxronlash).

**Bog'liq:** [[AGENTS.md]] · [[rules/README]] · [[tools/README]] · [[hooks/README]] · [[wiki-arxitektura]] · [[kontekst-xatolari]] · [[haftalik-audit]]

**MCP va Multi-Harness:** [[mcp-va-multi-harness-integratsiya]] · [[uzluksiz-organish-instinktlar]]
