---
name: ads-meta-audience
description: "Design, audit, and optimize Meta Ads audience architecture for Andromeda 2 and Uzbekistan/global markets — 4-layer funnel (Broad signal steering, Advantage+ interest stacks, 1P IG/Telegram/CAPI custom audiences, Value Lookalikes), Exclusion matrices, auction overlap math, and audience saturation modeling. Use when working with Meta Ads targeting, audiences, retargeting, lookalikes, exclusions, or audience fatigue."
attached_agents: [audit-meta, campaign-ideator, creative-strategist, meta-audience-architect]
---

# 🎯 Meta Ads Audience Architecture & Targeting Skill

Build evidence-backed, non-cannibalizing Meta Ads audience structures powered by `tools/meta-audience.py` and [[meta-auditoriya-arxitekturasi]].

## When to Activate

- Designing cold, warm, and hot targeting structures for Meta Ads (Facebook & Instagram).
- Auditing audience overlap, retargeting windows, Lookalike (LAL) seed quality, or missing exclusions (`M19–M24`).
- Selecting interest clusters, behaviors, or purchasing-power (*solventnost*) filters for Uzbekistan or international markets.
- Calculating whether an audience size can sustain a proposed daily budget without rapid frequency saturation.

## Core Concepts

1. **4-Layer Andromeda 2 Funnel (`architect`):**
   - **Layer 1 — Broad + Creative Signal Steering (TOF):** Geo + Age + Language isolation, letting the 3-second creative hook filter the auction.
   - **Layer 2 — Advantage+ Interest Stack & Purchasing Power (TOF):** Curated interest clusters paired with high-intent behaviors (`Engaged Shoppers`, `Frequent International Travelers`, `Page Admins`, `Flagship Devices`).
   - **Layer 3 — First-Party (1P) Warm Retargeting (MOF):** `IG_Engaged_30d` (critical when traffic goes to Telegram/Direct), `Video_Viewers_50pct_14d`, `LeadForm_Opened_Not_Submitted_30d`, and `Web_Visitors_30d`.
   - **Layer 4 — Value Lookalike & Hot BOF Closing:** 1% and 1–2% LAL built strictly from *qualified/paying* CRM records ($\ge 100$ events), plus `AddToCart_14d` / `Checkout_7d` closing sets.
2. **Geo & Language Isolation (`30-ozbekiston-konteksti`):**
   - Never mix Tashkent city and regional audiences in the same CBO campaign (cheaper regional CPM starves Tashkent delivery).
   - Separate Uzbek (Latin/Cyrillic) and Russian creatives into distinct ad sets.
3. **Exclusion Discipline & Overlap Cap:**
   - Every TOF ad set must exclude `Purchase_180d`, `CRM_Active_Clients`, and `LeadForm_Submitted_90d`.
   - Advantage+ Shopping (ASC) must lock `Existing Customer Budget Cap` at **25–30%**.
   - Keep inter-ad-set Auction Overlap **$\le 20\%$** of the smaller ad set.

## Workflow

1. **Step 1 — Generate Full Audience Blueprint:**
   ```powershell
   py -3 tools/meta-audience.py architect --niche <ecom|edu|real-estate|medical|b2b|beauty|auto|local> --daily-budget <USD> --geo <tashkent|regions|uzbekistan|global> --has-pixel --has-crm
   ```
2. **Step 2 — Select Interest Clusters & Behaviors:**
   ```powershell
   py -3 tools/meta-audience.py interests --niche <niche>
   ```
3. **Step 3 — Verify Overlap & Saturation Capacity:**
   ```powershell
   py -3 tools/meta-audience.py overlap --size-a <N> --size-b <M> --shared <K>
   py -3 tools/meta-audience.py saturation --audience-size <N> --daily-budget <USD> --cpm <CPM>
   ```
4. **Step 4 — Validate Budget & Learning Phase Math:**
   Ensure each active ad set receives $\ge (	ext{Target CPA} 	imes 50 / 7)$ daily budget (`tools/calculator.py meta-155`).

## Anti-Patterns (WRONG vs CORRECT)

- **FAIL: WRONG** — Building a 1% Lookalike audience from all raw Lead Form submissions (including spam/unqualified leads), teaching Meta's algorithm to optimize for low-quality form fillers.
- **PASS: CORRECT** — Filtering leads in CRM (AmoCRM/Bitrix24) first and feeding only `Qualified_Leads` or `Purchases` ($\ge 100	ext{–}500$ records via CAPI/CSV) as the Lookalike seed.

- **FAIL: WRONG** — Running 6 micro-interest ad sets on a $30/day budget with zero exclusions, causing 40% auction overlap and permanent `Learning Limited` status.
- **PASS: CORRECT** — Consolidating into 1 Broad ad set + 1 stacked Interest/Behavior ad set ($15/day each) with full `Purchase_180d` and `LeadForm_90d` exclusions.

## Best Practices

1. Always pair audience recommendations with matching creative angles (TOF Problem/Solution vs BOF Objection Crusher).
2. Cite exact tool output from `tools/meta-audience.py` in `outputs/<client>/<date>-meta-audience.md`.
3. Follow [[70-charter-baseline]]: if current account audience controls (`M19–M24`) are already healthy, return zero findings (`pass`).

## Related Skills

- `ads-meta` · `ads-budget` · `ads-server-side-tracking` · [[meta-auditoriya-arxitekturasi]] · [[meta-ads-interest-api]]
