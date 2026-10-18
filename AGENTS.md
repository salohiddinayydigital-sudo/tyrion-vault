---
name: AGENTS
description: "Tyrion v4.0 — kanonik agent shartnomasi. Har qanday AI harness (Claude Code, Cursor, Codex, OpenCode) uchun yagona qatlamlar, 36 agent va orkestratsiya tartibi"
tags: [router, agents, shartnoma, arxitektura, ecc]
source: "ECC (affaan-m/ECC) naqshi asosida Tyrion v4.0 uchun qurildi"
updated: 2026-10-17
---

# 🧠 TYRION v4.0 — KANONIK AGENT SHARTNOMASI

> **Bir qator:** Tyrion v4.0 — pullik reklama (Meta Ads, Google Ads, Telegram Ads, TikTok, YouTube va b.) hamda targetologiya uchun **ECC darajasidagi operatsion tizim**: yagona ildizda 36 ixtisoslashgan agent, 62 skill, 98 atomik wiki qayd, 8 nisha playbook, 5 kontekst rejimi va 0-token deterministik Python dvigateli.

<!-- tyrion:catalog agents=36 skills=62 wiki=100 playbooks=9 contexts=6 commands=18 rules=9 -->

## 1. Boot Tartibi (Token Tejamkor)

1. **Shu fayl (`AGENTS.md`)** — qatlamlar, 36 agent, orkestratsiya va xavfsizlik chegaralari.
2. **`MEMORY.md`** — operator xotirasi (`<=90` qator: til qonuni, O'zbekiston bozori asoslari, aktiv Bet Ledger va saboqlar).
3. **Vazifaga mos Kontekst va Qoida:** `contexts/` dan 1 ta ish rejimi (`audit-mode`, `launch-mode`, `scale-mode`, `creative-mode`, `uzbekistan-market`) va `rules/` dan 1–2 qoida.
4. **0-Token Qidiruv:** Bilim kerak bo'lsa `python3 tools/brain-search.py search "<so'z>"`, skill kerak bo'lsa `python3 tools/skill-search.py brief "<vazifa>" --agent <agent>`. Butun papkani yoppasiga o'qish taqiqlanadi ([[20-token-gigiyena]]).

## 2. Yagona Ildizli Qatlamlar (Single-Root Layers)

| Qatlam | Kanonik Manzil | Nima saqlanadi | Holat |
|---|---|---|---|
| **Agentlar** | `agents/` (36) | 36 ta ixtisoslashgan agent charteri (`Prompt Defense Baseline` + `skills:` ulangan) | kanonik |
| **Skilllar** | `skills/` (62) | 36 platforma (`ads-*`, `ads/` + 39 `references/`) va 26 operator/marketing skill | kanonik |
| **Buyruqlar** | `commands/` | Slash buyruqlar (`.claude/commands/` ga avtomatik mirror qilinadi) | kanonik |
| **Kontekstlar** | `contexts/` | 5 ta ECC Dynamic Context Mode (`audit`, `launch`, `scale`, `creative`, `uzbekistan`) | kanonik |
| **Playbooklar** | `playbooks/` | 8 ta to'liq nisha va platforma playbooki (Meta $1k–$10k, E-com, Ta'lim, Ko'chmas mulk va b.) | kanonik |
| **Bilim (Wiki)** | `wiki/` (98) | Atomik, wikilink bilan bog'langan bilim qaydlari va 16 ta SOP | kanonik |
| **Qoidalar** | `rules/` (8) | Buzilmas qoidalar (`00-manba` .. `70-charter-baseline`) | kanonik |
| **Asboblar** | `tools/` | `tyrion.py`, `meta-audience.py`, `creative-matrix.py`, `client-workspace.py`, `calculator.py`, `spend-guard.py`, `doctor.py`, `tyrion-shield.py`, `instincts.py` | faol |
| **Xotira** | `MEMORY.md` · `manifests/instincts.json` | Operator xotirasi (`<=90` qator) va `/learn` instinktlar reestri | faol |
| **Katalog & Graf** | `manifests/catalog.json` · `graphify-out/` | Mashina o'qiydigan yagona reestr va 0-token wikilink grafi (generatsiya) | generatsiya |

## 3. Agentlar Jamoasi (36 Charter)

| Guruh | Agentlar | Vazifa |
|---|---|---|
| **Meta Auditoriya & Voronka (1)** | `meta-audience-architect` | **YANGI:** Meta Andromeda 2 4-qatlamli auditoriya, Exclusion matritsa, Solventnost, Overlap (<20%), Saturation va LAL/Retargeting loyihalash |
| **Platforma Auditi (13)** | `audit-meta`, `audit-google`, `audit-telegram`, `audit-tiktok`, `audit-youtube`, `audit-linkedin`, `audit-x`, `audit-reddit`, `audit-pinterest`, `audit-snapchat`, `audit-microsoft`, `audit-amazon`, `audit-apple` | Platforma bo'yicha dalilga asoslangan chuqur texnik tekshiruv |
| **Ixtisoslashgan Audit (5)** | `audit-budget`, `audit-creative`, `audit-tracking`, `audit-policy-compliance`, `audit-regulatory-compliance` | Byudjet matematikasi, kreativ salomatligi, Pixel/CAPI o'lchovi, policy va qonunchilik |
| **Strategiya va Kreativ (8)** | `creative-strategist`, `campaign-ideator`, `positioning-strategist`, `copy-writer`, `reels-scriptwriter`, `social-content-writer`, `visual-designer`, `format-adapter` | Angle/avatar, big idea, 3 tilli (UZ/RU) sotuv matni, Reels skript va format |
| **Video Ijro (1)** | `video-editor` | Video montaj, ritm, rang grading, subtitr, eksport spec (`video-editing`, `video-motion-graphics`) |
| **Rejalash (3)** | `content-planner`, `launch-planner`, `seo-auditor` | Kontent tizimi, kampaniya launch rejasi, SEO va landing audit |
| **Tadqiqot va Nazorat (5)** | `research-worker`, `source-verifier`, `release-verifier`, `skill-reviewer`, `tracking-specialist` | Manbali tadqiqot, GTM/CAPI arxitekturasi va topshirish darvozasi |

## 4. Orkestratsiya Qonuni (Conductor → Workers)

- **Conductor — asosiy sessiya (`skills/ads/SKILL.md`).** Worker sub-agentlar bir-biri bilan to'g'ridan-to'g'ri gaplashmaydi va yakuniy mijoz hisobotini yozmaydi; ular faqat conductor'ga tekshirilgan topilmalarni qaytaradi ([[bosh-agent-protokoli]]).
- **Fan-out e'loni:** Har qanday parallel ish oldidan bitta qatorda e'lon qilinadi: `Maqsad: <X> · Kontekst: <rejim> · Jamoa: <agentlar>`.
- **Zero-Findings Tamoyili:** Auditda muammo bo'lmasa, sun'iy kamchilik to'qish taqiqlanadi ([[70-charter-baseline]]).

## 5. Qoidalar (`rules/`)

| Qoida | Qachon yuklanadi |
|---|---|
| [[00-manba]] | Har tahlil, audit, benchmark va hisobot oldidan |
| [[10-til-va-uslub]] | Har javob va reklama matni yozishdan oldin |
| [[20-token-gigiyena]] | Uzoq sessiya va katta vazifalarda |
| [[30-ozbekiston-konteksti]] | O'zbekiston bozori, mijoz voronkasi va kreativda |
| [[40-xavfsizlik-va-hisob]] | Hisob o'zgarishi, Spend-Guard, Pixel/CAPI va mijoz faylida |
| [[50-topshirish-dod]] | Ish yakunida (Definition of Done tekshiruvi) |
| [[60-loyiha-papkasi]] | Yangi mijoz loyihasi (`clients/<slug>/`) ochilganda |
| [[70-charter-baseline]] | Sub-agent (worker) chaqirilganda (Prompt Defense + Zero-Findings) |
