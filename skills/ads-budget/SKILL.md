---
name: ads-budget
description: "Plan and review paid-media budgets, bidding, pacing, marginal return, forecasts, CPA, ROAS, MER, LTV:CAC, constraints, and allocation across supported platforms. Use for ad budget allocation, media budget, bidding strategy, scaling, spend pacing, budget forecast, ROAS target, or investment tradeoffs."
attached_agents: [audit-budget, launch-planner]
---

# Budget and Bidding

1. Establish objective, conversion value, gross margin, cash constraints, sales
   capacity, attribution uncertainty, seasonality, and platform minimum evidence.
2. Normalize spend and outcomes to comparable windows and definitions.
3. Calculate break-even boundaries and show formulas, inputs, uncertainty, and
   sensitivity cases.
4. Distinguish committed baseline, controlled experiments, and reserve capacity.
5. Compare hold, reallocate, scale, reduce, or experiment options using marginal
   evidence rather than blended averages alone.
6. Return a decision-complete plan with platform/campaign amount, timing, owner,
   guardrails, success measure, and rollback trigger.

Rules such as 70/20/10, fixed CPA multiples, fixed budget-to-CPA ratios, and fixed
percentage scaling are optional heuristics, never universal authorization.

---

## Operator qatlami (Tyrion lokal bilimi)

### Amaliy bilim yadrosi
- Core math: CPA = spend / accepted conversions; ROAS = accepted conversion value / spend; break-even CPA = contribution per accepted conversion; break-even ROAS = 1 / contribution margin rate; marginal CPA and ROAS use incremental spend and conversions (budget-allocation.md).
- Use net accepted value where returns, fraud, cancellations, duplicate leads, or sales rejection are material; never infer profit from platform ROAS alone (budget-allocation.md).
- Missing owner-approved ceilings blocks an account write; missing economics makes the plan provisional (budget-allocation.md).
- Allocation order: reserve non-negotiable commitments, protect campaigns with causal or strong same-account marginal-contribution evidence, fund bounded experiments (hypothesis, minimum detectable effect, decision date, stop conditions), hold a contingency only for a defined use, then reallocate from the weakest marginal opportunity (budget-allocation.md).
- Any proven/growth/experiment split is operator policy, not a default; record the chosen split and rationale in the run manifest (budget-allocation.md).
- Scale only when data has matured through the relevant lag, tracking/consent/policy/inventory/landing are healthy, marginal performance is inside the owner-approved boundary, the change is eligible, volatility is absorbable, and a before/after measure, verification window, and rollback trigger exist (budget-allocation.md).
- No universal safe scaling percentage exists - size changes from platform simulations, account history, conversion cycles, and blast-radius limits (budget-allocation.md).
- Do not pause solely because spend crosses a fixed multiple of target CPA; first check conversion lag, tracking outages, low sample size, downstream lead quality, seasonality, and experiment need (budget-allocation.md).
- Immediate containment is for an owner-defined runaway-spend ceiling, policy or legal exposure, broken destination, confirmed tracking corruption, or unauthorized delivery - prefer the smallest reversible action (budget-allocation.md).
- Bidding strategy is chosen from objective, value signal, delivery constraint, and measurement quality; Google Smart Bidding labels (Target CPA, Target ROAS, Maximize conversions, Maximize conversion value) optimize at auction time and vary by campaign type; repair corrupted measurement before changing the bidder (bidding-strategies.md).

### UZ bozori (agar tegishli bo'lsa)
- Allocation must respect seasonal demand windows: Ramazan evenings, Navruz (21 March), 1 September (education/clothing/tech), December (largest sales month), summer (real estate, travel, weddings) (ozbekiston-konteksti.md).
- UZ price sensitivity is high, but showing value beats discounting; compare against the account's own history, not global benchmarks (ozbekiston-konteksti.md).

### Asosiy manbalar (yuklash tartibida)
- ads/references/budget-allocation.md
- ads/references/bidding-strategies.md


## Deterministic CLI & Tooling Integration (`0 Token`)
Before generating recommendations or mutating plans for `ads-budget`, execute the relevant Tyrion v4.0 deterministic checks:
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
