---
name: uzbekistan-market-intel
description: "O'zbekiston raqamli reklama bozori intellekti — Toshkent va viloyatlar auditoriya segmentatsiyasi, 3 tilli (O'zbek lotin, kirill, rus) mentalitet, Telegram Bot/ManyChat/AmoCRM voronkasi, Payme/Click/Uzum Nasiya psixologiyasi va to'lov qobiliyati (solventnost) filtrlari. Use when planning, auditing, or writing ads for Uzbekistan businesses."
attached_agents: [audit-meta, audit-telegram, campaign-ideator, copy-writer, meta-audience-architect]
---

# Uzbekistan Market Intelligence (`uzbekistan-market-intel`)

## When to Activate
- Planning, auditing, or scaling Meta Ads, Telegram Ads, Google Ads, or TikTok Ads for Uzbekistan (`Tashkent` or regional markets).
- Designing lead generation or e-commerce funnels using **Telegram Bots**, **ManyChat Instagram DM automation**, and **AmoCRM / Bitrix24**.
- Structuring offers with local BNPL / installment systems (**Uzum Nasiya, Alif Nasiya, Payme, Click, ZoodPay**).
- Filtering high-ticket audiences (*Novostroyka*, Private Schools, Clinics, B2B, Auto, Furniture) for purchasing power (*solventnost*).

## Core Market Rules
1. **Telegram-First Funnel Architecture:** Email drip campaigns have `<2%` open rates in B2C Uzbekistan. Always route traffic to `Instagram DM (ManyChat keyword)` or `Telegram Bot (?start=utm_payload)` -> `Share Contact` -> `AmoCRM` -> `Call within 15 minutes`.
2. **Geographic Split (Never Mix in One Ad Set):**
   - **Tashkent City:** Higher CPM ($2.50–$6.00+), higher AOV, strong bilingual demand (`UZ` + `RU` in separate ad sets).
   - **Regions (Samarkand, Fergana, Andijan, Namangan, Bukhara, etc.):** Lower CPM ($0.80–$2.20), massive reach; if mixing with Tashkent in CBO/Broad without exclusions, Meta will spend 80% of budget on cheap regional impressions with lower purchasing power.
3. **3-Language Native Copywriting (`[[10-til-va-uslub]]`):**
   - Never machine-translate Russian ad copy into Uzbek. Write native Uzbek (Latin), Uzbek (Cyrillic for 35+ audience), and Russian hooks separately.
4. **BNPL / Installment Framing:** For any offer `>$50`, displaying the monthly installment price via **Uzum Nasiya / Alif Nasiya** (`"Oyiga atigi 149,000 so'mdan — boshlang'ich to'lovsiz"`) lifts conversion rate by `1.6x–2.4x`.

## Anti-Patterns
- **WRONG:** Running a single Uzbekistan-wide Campaign optimizing for "Link Clicks" (`Traffic`) to a slow website form.
- **CORRECT:** Separating Tashkent and Regions into dedicated Conversion/Lead Ad Sets with `Pixel + CAPI` or Instant Form (2 qualifying questions) + Telegram Bot warmup.

## Related Skills & Playbooks
- `skills/ads-meta-audience/SKILL.md`
- `playbooks/meta-ads-1k-10k-uz.md`
- `playbooks/telegram-bot-amocrm-voronka.md`


## Deterministic CLI & Tooling Integration (`0 Token`)
Before generating recommendations or mutating plans for `uzbekistan-market-intel`, execute the relevant Tyrion v4.0 deterministic checks:
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
