---
name: ads-meta-audience
description: Design, audit, and optimize Meta Ads audience architecture for Andromeda 2 and Uzbekistan/global markets — 4-layer funnel, Detailed Targeting Accuracy Engine (6-status official API verification), Exclusion matrices, static vs auction overlap math, and audience saturation sensitivity modeling. Use when working with Meta Ads targeting, interests, behaviors, audiences, retargeting, lookalikes, exclusions, or audience fatigue.
triggers:
- detalniy targeting
- detailed targeting
- meta auditoriya
- interest qidirish
- overlap
- saturation
- lookalike
- retargeting
- solventnost
- детальный таргетинг
- интересы мета
- аудитория танлаш
aliases:
- detailed-targeting
- meta-targeting
- audience-architect
- lal
- retargeting
domains:
- audience
- targeting
- meta
platforms:
- meta
attached_agents: [audit-meta, campaign-ideator, creative-strategist, meta-audience-architect]
related_skills:
- ads-meta
- uzbekistan-market-intel
- ads-creative
references:
- skills/ads/references/meta-audit.md
- docs/DETAILED-TARGETING-ACCURACY.md
risk_level: low
output_contract: 4-Layer Meta Audience Architecture + 6-Status Verified Detailed Targeting Report (Zero Hallucinations)
---

# 🎯 Meta Ads Audience Architecture & Detailed Targeting Accuracy Skill

Build evidence-backed, non-cannibalizing Meta Ads audience structures powered by `tools/meta-audience.py`, `tools/meta-targeting-engine.py`, `docs/DETAILED-TARGETING-ACCURACY.md`, and [[meta-auditoriya-arxitekturasi]].

## When to Activate

- Designing cold, warm, and hot targeting structures for Meta Ads (Facebook & Instagram).
- Searching and validating **Detailed Targeting (Interests, Behaviors, Demographics)** without hallucinating non-existent interest names.
- Auditing audience overlap, retargeting windows, Lookalike (LAL) seed readiness, or missing exclusions (`M19–M24`).
- Calculating whether an audience size can sustain a proposed daily budget without rapid frequency saturation.

## Core Concepts

1. **Detailed Targeting Accuracy Rules (`tools/meta-targeting-engine.py`):**
   - Never present AI-guessed keywords or static `NICHE_TAXONOMY` strings as confirmed Meta options.
   - Every option must carry one of 6 strict statuses: `VERIFIED_AVAILABLE`, `FOUND_NOT_VALIDATED`, `UNAVAILABLE_OR_CONSOLIDATED`, `RELATED_UNVERIFIED`, `NOT_FOUND`, or `API_UNAVAILABLE`.
   - Preserve exact English/original `name` and `id` returned by Meta API (`GET /v26.0/search`, `/act_<id>/targetingsearch`, `/targetingsuggestions`, `/targetingvalidation`), deduplicating strictly by `(id, type)`.
   - Frame purchasing-power (*Solventnost*) signals (`Engaged Shoppers`, `Frequent International Travelers`, `Page Admins`, flagship devices) as **testable marketing hypotheses (`MARKETING_HYPOTHESIS`)**, never as guaranteed income filters.
2. **4-Layer Andromeda 2 Funnel (`architect`):**
   - **Layer 1 — Broad + Creative Signal Steering (TOF):** Geo + Age + Language isolation, letting the 3-second creative hook filter the auction.
   - **Layer 2 — Verified Detailed Targeting Stack & Solventnost Hypotheses (TOF):** Built strictly from `VERIFIED_AVAILABLE` (or `FOUND_NOT_VALIDATED`) API options; if live API is unavailable (`API_UNAVAILABLE`), clearly label candidate seeds as `RELATED_UNVERIFIED`.
   - **Layer 3 — First-Party (1P) Warm Retargeting (MOF):** `IG_Engaged_30d`, `Video_Viewers_50pct_14d`, `LeadForm_Opened_Not_Submitted_30d`, and `Web_Visitors_30d` (no fake minimum pool floors when traffic is `0`).
   - **Layer 4 — Value Lookalike & Hot BOF Closing:** 1% and 1–2% LAL built strictly from *qualified/paying* CRM records ($\ge 100$ events), plus `AddToCart_14d` / `Checkout_7d` closing sets.
3. **Exclusion Discipline & Overlap Cap:**
   - Every TOF ad set must exclude `Purchase_180d`, `CRM_Active_Clients`, and `LeadForm_Submitted_90d`.
   - Keep inter-ad-set Static Pool Overlap **$< 20\%$** of the smaller ad set (`20%–29.9%` = warning, $\ge 30\%$ = critical consolidation), while checking Ads Manager Delivery Insights for live Auction Overlap.

## Workflow

1. **Step 1 — Search & Validate Detailed Targeting Options:**
   ```bash
   python3 tools/meta-targeting-engine.py search --product "<mahsulot>" --niche <niche> --account-id <act_id> --json
   ```
2. **Step 2 — Generate 4-Layer Audience Blueprint (with Unit Economics):**
   ```bash
   python3 tools/meta-audience.py architect --niche <ecom|edu|real-estate|medical|b2b|beauty|auto|local> --daily-budget <USD> --aov <USD> --margin-pct <PCT> --geo <tashkent|regions|uzbekistan|global> --has-pixel --has-crm
   ```
3. **Step 3 — Verify Overlap & Saturation Sensitivity Window:**
   ```bash
   python3 tools/meta-audience.py overlap --size-a <N> --size-b <M> --shared <K>
   python3 tools/meta-audience.py saturation --audience-size <N> --daily-budget <USD> --cpm <CPM>
   ```

## Related Skills

- `ads-meta` · `ads-budget` · `ads-server-side-tracking` · [[meta-auditoriya-arxitekturasi]] · [[meta-ads-interest-api]]
