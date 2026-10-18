---
name: hooks-readme
description: Tyrion hook qatlami — deterministik nazorat, nima uchun faqat o'lchanadigan dalil ishlatiladi
tags: [hooks, avtomatika, sifat]
source: "ECC delivery-gate naqshi (skills/delivery-gate/SKILL.md) asosida Tyrion uchun (2026-09-16)"
updated: 2026-09-16
---

# 🪝 HOOK QATLAMI

> Hook har sessiyada ishlaydi va **kontekstga matn qo'shadi** — shuning uchun faqat
> o'lchanadigan dalil ishlatiladi: fayl bor/yo'q, sana, regex, exit kod. LLM hukmi yo'q.

## Nima ishlaydi

| Hodisa | Skript | Nima qiladi | Bloklaydimi |
|--------|--------|-------------|-------------|
| `SessionStart` | `tyrion-hook.py brief` | 1 qator holat: qayd/agent soni, graf eskiligi, drift, git | yo'q |
| `PostToolUse` (Edit/Write) | `tyrion-hook.py ingest` | yangi qayd `INDEX.md` da bormi, `LOG.md` bugun yangilanganmi | yo'q (ogohlantiradi) |
| `Stop` | `tyrion-hook.py dod --warn-only` | topshirish darvozasi: `doctor` xatolari + ingest | yo'q (ogohlantiradi) |

Qo'lda **qat'iy** rejim (ishni bloklaydi, exit 1):

```powershell
py -3 hooks\tyrion-hook.py dod              # to'siq bo'lsa exit 1
py -3 hooks\tyrion-hook.py ingest           # faqat ingest
```

## O'rnatish

```powershell
py -3 tools\install-hooks.py --dry-run      # nima qo'shilishini ko'rsatadi
py -3 tools\install-hooks.py                # .claude/settings.json ga qo'shadi (nusxa olib)
py -3 tools\install-hooks.py --target "claude-ads-main\.claude\settings.json"
```

`install-hooks.py` mavjud hook'larni **o'chirmaydi** — faqat o'zinikini qo'shadi (takrorlamaydi),
avval `settings.json.bak` nusxasini oladi.

## Nega Stop hook bloklamaydi

Har to'xtashda qat'iy tekshiruv ishni to'xtatib qo'yardi (katalog har tahrirdan keyin eskiradi).
Shuning uchun hook **ogohlantiradi**, qat'iy darvoza esa qo'lda yoki haftalik auditda ishlatiladi.

**Bog'liq:** [[AGENTS.md]] · [[50-topshirish-dod]] · [[tools/README|asboblar]] · [[haftalik-audit]]
