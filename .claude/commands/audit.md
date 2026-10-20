---
description: Platforma auditi — conductor + worker'lar bilan (Meta, Google, TikTok, ...)
argument-hint: <platforma> <mijoz>
---

# /audit — platforma auditi

Vazifa: **$ARGUMENTS** (platforma + mijoz)

## Oldindan (majburiy)

1. Qoida yukla: `rules/00-manba.md` + `rules/40-xavfsizlik-va-hisob.md` (+ mijoz bo'lsa `rules/30-ozbekiston-konteksti.md`).
2. Kontekst: `MEMORY.md` (operator xotirasi) + `journal/<mijoz>.md` (mijoz holati).
3. Ma'lumot bor/yo'q ro'yxatini tuz — yetishmaganini **so'ra**, taxmin qilma.

## E'lon (fan-out oldidan)

```
Maqsad: <X> · Jamoa: <N bot: nomlari>
```

## Ijro

| Qadam | Kim | Nima |
|-------|-----|------|
| 1 | conductor (shu sessiya) | kontrakt, dalil yig'ish, savol berish |
| 2 | `audit-<platforma>` worker | platforma bo'yicha dalilga asoslangan findings |
| 3 | `audit-tracking` / `audit-budget` | kerak bo'lsa: o'lchov va matematika |
| 4 | conductor | yig'ish, ziddiyatlarni ajratish, tavsiya |
| 5 | `release-verifier` | topshirish oldidan nazorat |

## Natija

- Fayl: `outputs/<mijoz>/<sana>-<platforma>-audit.md`
- Har topilma: `control_id` · dalil · severity · confidence · teskari qadam
- Checklist: ROAS · Pixel/CAPI · UTM · Policy ([[50-topshirish-dod]])
- Hisob o'zgarishi kerak bo'lsa — **draft + tasdiq**, o'zing o'zgartirmaysan.

Oxirida: `journal/<mijoz>.md` ga qaror va sababi, `LOG.md` ga 1 qator.
