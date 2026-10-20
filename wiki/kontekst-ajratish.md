---
name: kontekst-ajratish
description: Expertise (doimiy) vs Situational (vaziyatli) kontekst — situational ma'lumot just-in-time yuklanadi, doimiy kontekstga tiqilmaydi
tags: [kontekst, qoidalar, arxitektura]
source: raw/2026-09-03-aios-xatoliklar-va-audit.md (§ Kontekstni ajratish)
updated: 2026-09-05
---

# Kontekstni ajratish

Bu ajratishning fayl darajasidagi ko'rinishi: [[wiki-arxitektura]]. Sessiya almashganda faqat kerakli vaziyatli qatlamni qayta yuklash uchun [[session-handoff]] ishlatiladi.

Ikki turdagi bilim aralashib ketsa — bloat va xarajat oshadi. Ajratish qoidasi:

| Tur | Nima | Qayerda |
|-----|------|---------|
| **Expertise Context** (doimiy) | Biznes nima bilan shug'ullanishi, qat'iy qoidalar | `CLAUDE.md` (router) da |
| **Situational Context** (vaziyatli) | Bir martalik hisobotlar, mijoz chatlari, uchrashuv transkriptlari | Doimiy kontekstga TIQILMAYDI — faqat savol tushganda **just-in-time** qidirib yuklanadi |

**Vault amaliyoti:** situational material → `raw/` arxivi (faqat o'qish), uning zich xulosasi → `wiki/`; ehtiyoj tug'ilganda aniq fayl o'qiladi, yoppasiga emas ([[token-gigiyenasi]]).

**Sababi:** katta kontekst → "needle in the haystack" → [[kontekst-xatolari]] (Bloat). Just-in-time yuklash kesh narxini ham kamaytiradi: [[prompt-caching]]
