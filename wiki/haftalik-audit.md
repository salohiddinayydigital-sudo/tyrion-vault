---
name: haftalik-audit
description: Haftalik read-only avto-audit — INDEX havolalari, noto'g'ri fayllar, dublikatlar, qoida ziddiyatlari → audits/report
tags: [audit, protsedura, sogliq]
source: raw/2026-09-03-aios-xatoliklar-va-audit.md (§ Haftalik Avto-Audit)
updated: 2026-09-05
---

# Haftalik avto-audit

Vault sog'lig'ini ushlab turish — har hafta oxirida **read-only** audit o'tkaziladi.

## Buyruq (Claude Code terminalida)

> Run read-only audit: Check all links in INDEX.md against files on disk. Identify any misrouted files, duplicate notes, or conflicting rules between CLAUDE.md and subfolders. Write findings to audits/report-YYYY-MM-DD.md. Do not delete or rename anything automatically.

## Nima tekshiriladi

1. [[INDEX.md]] dagi barcha havola ↔ diskdagi fayllar mosligi (orphan/dead link)
2. Noto'g'ri joylashtirilgan fayllar (misrouted)
3. Dublikat qaydlar
4. `CLAUDE.md` ↔ subpapkalar orasidagi qoida ziddiyatlari

## Natija

- Topilmalar → `audits/report-YYYY-MM-DD.md` ga yoziladi (eskirgan havolalar, buzilgan marshrutlar, ziddiyatlar bo'yicha tavsiyalar shaklida)
- **Qat'iy:** hech narsa avtomatik o'chirilmaydi, rename qilinmaydi (vault qoidasi №6)

Topilmalar turlari 4 xato sinfiga tushadi: [[kontekst-xatolari]] · Oldini olishda asos: [[kontekst-ajratish]] · Hisobot yozish formati: [[LOG.md]] · Vault qatlami: [[wiki-arxitektura]]
