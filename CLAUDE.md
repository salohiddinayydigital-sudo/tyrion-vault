---
name: CLAUDE
description: "Tyrion v4.0 — AI Paid Media & Targetology Operating System routeri (ECC-grade yagona ildizli arxitektura)"
tags: [router, tyrion, ecc, v3]
source: "affaan-m/ECC arxitekturasi asosida Tyrion v4.0 uchun"
updated: 2026-10-17
---

# 🧠 TYRION v4.0 — AI PAID MEDIA & TARGETOLOGY OS

> **Kanonik shartnoma:** [[AGENTS.md]] · **Operator xotirasi:** [[MEMORY.md]] · **Bilim xaritasi:** [[INDEX.md]] · **Kirish:** [[README.md]]

Tyrion v4.0 — `affaan-m/ECC` (Everything Claude Code) arxitekturasida qurilgan **yagona ildizli (Single Source of Truth)** reklama, targetologiya va marketing operatsion tizimi. Hech qanday ichki dublikat papka (`claude-ads-main/`) yo'q — barcha agentlar, skilllar, playbooklar, kontekst rejimlari va 0-token CLI asboblar to'g'ridan-to'g'ri loyiha ildizida joylashgan.

## 1. Yagona Ildizli Tuzilma (Single-Root Architecture)

| Qatlam / Joy | Nima saqlanadi | Qachon o'qiladi |
|---|---|---|
| `AGENTS.md` | **Kanonik agent shartnomasi** — 36 agent, orkestratsiya, tamoyillar | Sessiya boshida (boot) |
| `MEMORY.md` | **Operator xotirasi va Bet Ledger** (`<=90` qator) — til, bozor, aktiv gipotezalar, saboqlar | Sessiya boshida (boot) |
| `INDEX.md` | **Yagona Bilim Xaritasi (MOC)** — barcha `wiki/` va `playbooks/` jadvali | Bilim qidirish / yozishdan oldin |
| `agents/` | **36 ta kanonik agent charteri** (13 platforma auditi, 5 ixtisos audit, 18 strategiya/kreativ/auditoriya) | Worker ishga tushganda |
| `skills/` | **62 ta kanonik skill** (`ads-*` platforma, `ads/` konduktor + 39 `references/`, operator skilllar) | Vazifa boshida (`skill-search.py`) |
| `commands/` | **16 ta slash buyruq** (`/start`, `/audit`, `/auditoriya`, `/kreativ`, `/voronka`, `/budget`, `/scale`, `/raqobatchi`, `/mijoz`, `/tracking`, `/hisobot`, `/savol`, `/sop`, `/learn`, `/shield`, `/doctor`) | Foydalanuvchi chaqirganda |
| `contexts/` | **5 ta ECC Dynamic Context Mode** (`audit-mode`, `launch-mode`, `scale-mode`, `creative-mode`, `uzbekistan-market`) | Vazifa rejimiga qarab ([[contexts/README]]) |
| `playbooks/` | **8 ta amaliy nisha va platforma playbooki** (Meta $1k–$10k, E-com, Ta'lim, Ko'chmas mulk, Tibbiyot, B2B, Atir/Fitness, TG Bot+AmoCRM) | Kampaniya / nisha strategiyasida ([[playbooks/README]]) |
| `wiki/` | **98 ta atomik bilim qaydi** (Andromeda 2, Meta Audience, Google Coliseum, Telegram Ads, CJM, 16 SOP) | Faqat kerakli qayd (`brain-search.py`) |
| `rules/` | **8 ta buzilmas qoida** (`00-manba` .. `70-charter-baseline`) | Vazifaga mos 1–2 qoida ([[rules/README]]) |
| `tools/` | **0-token deterministik CLI asboblar** (`tyrion.py`, `meta-audience.py`, `creative-matrix.py`, `client-workspace.py`, `calculator.py`, `spend-guard.py`, `doctor.py`, `tyrion-shield.py`, `instincts.py`) | Har tahlil, hisob va tekshiruvda ([[tools/README]]) |
| `hooks/` | **Deterministik lifecycle hooklar** (`SessionStart`, `PreToolUse`, `PostToolUse`, `Stop`) | Avtomatik ([[hooks/README]]) |
| `manifests/` | `catalog.json` (generatsiya reestri) va `instincts.json` (`/learn` xotirasi) | `tools/catalog.py` va `tools/instincts.py` |

## 2. Qat'iy Qoidalar

1. **95% Ishonch Qonuni:** Maqsad, byudjet yoki voronka noaniq bo'lsa — taxmin qilma, avval foydalanuvchidan so'ra.
2. **Token Gigiyenasi:** Butun omborni yoppasiga O'QIMA; avval `python3 tools/brain-search.py search "<so'z>"` yoki `python3 tools/skill-search.py brief "<vazifa>"` (0 token) ishlatiladi ([[token-gigiyenasi]]).
3. **Manbasiz Fakt Yo'q:** Raqam, benchmark yoki CPA/ROAS da'vosi faqat tekshirilgan manba yoki `tools/calculator.py` hisobiga tayanadi ([[00-manba]]).
4. **Spend-Guard Himoyasi:** Reklama hisobiga har qanday o'zgartirish (`budget >20%`, yangi kampaniya, pauza) `tools/spend-guard.py` tekshiruvi va foydalanuvchi tasdig'isiz bajarilmaydi ([[40-xavfsizlik-va-hisob]]).
5. **Atomiklik va Yagona Manba:** 1 qayd = 1 tushuncha, YAML frontmatter (`name/description/tags/source/updated`, `\` o'rniga `/`), kamida 2 ta wikilink (`[[...]]`). Barcha raqamlar `manifests/catalog.json` dan avtomatik sinxronlanadi (`python3 tools/catalog.py sync-claims`).

## 3. Asosiy CLI Asboblar (`tools/`)

| Buyruq | Vazifasi |
|---|---|
| `python3 tools/tyrion.py status` | **Yagona Master CLI** — tizim holati va barcha buyruqlar menyusi |
| `python3 tools/doctor.py` | **Tizim sog'lig'i** — 14 qatlamli tekshiruv (bilim, katalog, skill, sirlar, testlar) |
| `python3 tools/tyrion-shield.py scan` | **TyrionShield (/shield)** — 5 qavatli xavfsizlik va governance skaneri |
| `python3 tools/meta-audience.py <cmd>` | **Meta Ads Audience Studio (/auditoriya)** — `architect`, `interests`, `overlap`, `saturation`, `retargeting`, `lookalike`, `diagnose` |
| `python3 tools/creative-matrix.py <cmd>` | **Andromeda 2 Creative Studio (/kreativ)** — 3x3 Angle×Format matritsa, 3 tilli Hook va charchoq tahlili |
| `python3 tools/client-workspace.py <cmd>` | **Mijoz Ish Maydoni (/mijoz)** — yangi mijoz papkasi (`BRIEF`, `AUDIENCE-MAP`, `CREATIVE-MATRIX`, `journal`) |
| `python3 tools/calculator.py <cmd>` | **Media Matematika (/budget)** — `breakeven`, `meta-155`, `google-sculpt`, `telegram-funnel`, `ladder` |
| `python3 tools/spend-guard.py <cmd>` | **Spend-Guard** — byudjet (+20%), Telegram (160 belgi), Pixel+CAPI (`event_id`) va Change Packet darvozasi |
| `python3 tools/instincts.py <cmd>` | **Uzluksiz O'rganish (/learn)** — kampaniya saboqlarini saqlash va `MEMORY.md` ga ko'tarish |
