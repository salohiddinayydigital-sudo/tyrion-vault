---
name: AGENTS
description: "Tyrion v5.0 — kanonik agent shartnomasi. Har qanday AI harness (Claude Code, Cursor, Codex, Windsurf) uchun yagona qatlamlar, 36 agent va orkestratsiya tartibi"
tags: [router, agents, shartnoma, arxitektura, ecc]
source: "ECC (affaan-m/ECC) naqshi asosida Tyrion v5.0 uchun qurildi"
updated: 2026-10-20
---

# 🧠 TYRION v5.0 — KANONIK AGENT SHARTNOMASI

> **Bir qator:** Tyrion v5.0 — pullik reklama (Meta Ads, Google Ads, Telegram Ads, TikTok, YouTube va b.) hamda targetologiya uchun **ECC darajasidagi operatsion tizim**: yagona ildizda 36 ixtisoslashgan agent, 62 skill, 100 atomik wiki qayd, 9 playbook fayli, 6 kontekst fayli, 18 slash buyruq va 29 ta 0-token deterministik Python asbobi.

<!-- tyrion:catalog agents=36 skills=62 wiki=100 playbooks=9 contexts=6 commands=18 rules=9 tools=29 -->

## 1. Boot Tartibi (Token Tejamkor)

1. **Shu fayl (`AGENTS.md`)** — qatlamlar, 36 agent, orkestratsiya va xavfsizlik chegaralari.
2. **`MEMORY.md`** — operator xotirasi (`<=90` qator: til qonuni, O'zbekiston bozori asoslari, aktiv Bet Ledger va saboqlar).
3. **Vazifaga mos Kontekst va Qoida:** `contexts/` dan 1 ta ish rejimi (`audit-mode`, `launch-mode`, `scale-mode`, `creative-mode`, `uzbekistan-market`) va `rules/` dan 1–2 qoida.
4. **Universal Auto-Router va 0-Token Kontekst Yuklash:** Foydalanuvchi oddiy tilda topshiriq berganda (`/skill-search` yoki `/agent` yozishi shart emas!), `python3 tools/skill-search.py route "<vazifa>" --load` avtomatik ravishda `primary_agent`, `supporting_agents`, `required_skills`, `references_to_load`, `rules_to_load` va `tools_to_use` ni aniqlaydi hamda faqat kerakli charter va `SKILL.md` fayllarini yuklaydi ([[20-token-gigiyena]], [[70-charter-baseline]]).

## 2. Yagona Ildizli Qatlamlar (Single-Root Layers)

| Qatlam | Kanonik Manzil | Nima saqlanadi | Holat |
|---|---|---|---|
| **Agentlar** | `agents/` (36) | 36 ta ixtisoslashgan agent charteri (`Prompt Defense Baseline` + `skills:` ulangan) | kanonik |
| **Skilllar** | `skills/` (62) | 36 platforma (`ads-*`, `ads/` + 39 `references/`) va 26 operator/marketing skill | kanonik |
| **Buyruqlar** | `commands/` (18) | 18 ta slash buyruq (`.claude/commands/` ga avtomatik mirror qilinadi) | kanonik |
| **Kontekstlar** | `contexts/` (6) | 5 ta ECC Dynamic Context Mode (`audit`, `launch`, `scale`, `creative`, `uzbekistan`) + `README.md` | kanonik |
| **Playbooklar** | `playbooks/` (9) | 8 ta to'liq nisha va platforma playbooki + `README.md` | kanonik |
| **Bilim (Wiki)** | `wiki/` (100) | 100 ta atomik, wikilink bilan bog'langan bilim qaydi va 16 ta SOP | kanonik |
| **Qoidalar** | `rules/` (9) | 8 ta buzilmas qoida (`00-manba` .. `70-charter-baseline`) + `README.md` | kanonik |
| **Asboblar** | `tools/` (29) | `tyrion.py`, `meta-targeting-engine.py`, `meta-audience.py`, `meta-insights-sync.py`, `ad-export-analyzer.py`, `capi-utm-builder.py`, `creative-matrix.py`, `client-workspace.py`, `calculator.py`, `spend-guard.py`, `doctor.py`, `tyrion-shield.py`, `instincts.py` | faol |
| **Xotira** | `MEMORY.md` · `manifests/instincts.json` | Operator xotirasi (`<=90` qator) va `/learn` instinktlar reestri | faol |
| **Katalog & Graf** | `manifests/catalog.json` · `graphify-out/` | Mashina o'qiydigan yagona reestr va 0-token wikilink grafi (generatsiya) | generatsiya |

## 3. Agentlar Jamoasi (36 Charter)

| Guruh | Agentlar | Vazifa |
|---|---|---|
| **Meta Auditoriya & Voronka (1)** | `meta-audience-architect` | Meta Andromeda 2 4-qatlamli auditoriya, Exclusion matritsa, Solventnost, Overlap (<20%), Saturation va LAL/Retargeting loyihalash |
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
