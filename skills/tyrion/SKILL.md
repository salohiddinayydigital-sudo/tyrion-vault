---
name: tyrion
description: Tyrion v5.0 Master Operating System loader — operator xotirasi (MEMORY.md), O'zbekiston bozori konteksti, 8 nisha playbook, 5 kontekst rejimi va 0-token CLI dvigatellariga yagona kirish nuqtasi. Use when initializing a marketing session or routing complex multi-channel tasks.
standalone: true
triggers:
- tyrion
- tizim holati
- system status
- tyrion os
aliases:
- tyrion-os
- master-router
domains:
- orchestration
- system
platforms:
- multi-platform
related_skills:
- ads
- uzbekistan-market-intel
references: []
risk_level: low
output_contract: Tyrion OS system status and autonomous orchestration routing plan
---

# Tyrion v5.0 — Paid Media & Targetology OS Loader

## When to Activate
- Session initialization (`/start`) or multi-channel campaign orchestration across Meta Ads, Google Ads, Telegram Ads, TikTok, and YouTube.
- Loading Uzbekistan local market constraints (`contexts/uzbekistan-market.md`, `wiki/ozbekiston-konteksti.md`) and operator memory (`MEMORY.md`).

## Core Routing Protocol (0-Token First)
1. **Read Boot Memory:** Load `MEMORY.md` (`<=90` lines) and `AGENTS.md`.
2. **Select Context Mode (`contexts/`):**
   - Auditing an account $	o$ `contexts/audit-mode.md`
   - Launching a campaign $	o$ `contexts/launch-mode.md`
   - Scaling budgets $	o$ `contexts/scale-mode.md`
   - Writing hooks/scripts $	o$ `contexts/creative-mode.md`
   - Uzbekistan B2C/B2B $	o$ `contexts/uzbekistan-market.md`
3. **Run Deterministic CLI Tools Before LLM Generation:**
   - Audience architecture, overlap, saturation, LAL, retargeting: `python3 tools/meta-audience.py`
   - Ad Manager CSV/JSON export & Breakdown Effect: `python3 tools/ad-export-analyzer.py`
   - Andromeda 2 3x3 creative matrix & 3-language hooks: `python3 tools/creative-matrix.py`
   - CAPI v22 SHA-256 payload, EMQ & Telegram Bot UTM: `python3 tools/capi-utm-builder.py`
   - Unit economics & Spend-Guard: `python3 tools/calculator.py` and `python3 tools/spend-guard.py`

## Anti-Patterns
- **WRONG:** Reading all 100 `wiki/` files into context at once or guessing benchmarks without running `calculator.py`.
- **CORRECT:** Querying `python3 tools/brain-search.py search "<topic>"` (0 tokens) and reading only the top 1–2 matched notes or `playbooks/`.


## Deterministic CLI & Tooling Integration (`0 Token`)
Before generating recommendations or mutating plans for `tyrion`, execute the relevant Tyrion v5.0 deterministic checks:
- **Unit Economics & Break-Even:** `python3 tools/calculator.py breakeven --price <AOV> --cogs <COGS>`
- **Meta Audience & Funnel Diagnostics:** `python3 tools/meta-audience.py architect --niche <niche> --budget <daily_usd>`
- **CSV/JSON Export & Breakdown Effect:** `python3 tools/ad-export-analyzer.py analyze --file <export.csv>`
- **CAPI v22 SHA-256 & Telegram Bot UTM:** `python3 tools/capi-utm-builder.py utm --url <url> --platform meta`
- **Spend-Guard Gate:** `python3 tools/spend-guard.py budget --current <old> --proposed <new> --max-cap <cap>`

## Anti-Patterns (`WRONG` vs `CORRECT`)
| Scenario | ❌ FAIL (`WRONG`) | ✅ PASS (`CORRECT`) |
|---|---|---|
| **Benchmark Claims** | Quoting generic global CTR/CPA averages without account history or break-even math. | Computing exact `Break-Even ROAS = 1 / Margin` and `Target CPA` via `tools/calculator.py` first (`[[00-manba]]`). |
| **Budget Scaling** | Doubling (+100%) an active ad set's budget overnight and resetting the Learning Phase. | Scaling vertically by at most **+20% every 48–72 hours** (`tools/spend-guard.py`) or cloning winning angles horizontally (`[[learning-phase-qoidalari]]`). |
| **Audience Isolation** | Running cold prospecting (`TOF`) without excluding `Purchase 180d`, `Leads 30d`, and `Active DM 14d`. | Enforcing the 4-layer Exclusion Matrix via `tools/meta-audience.py architect` (`[[meta-auditoriya-arxitekturasi]]`). |
| **Placement Pruning** | Pausing high-volume placements (e.g., Instagram Reels) solely due to higher average CPA (*Breakdown Effect*). | Running `tools/ad-export-analyzer.py breakdown-effect` to evaluate marginal CPA impact (`[[meta-breakdown-effekti]]`). |
