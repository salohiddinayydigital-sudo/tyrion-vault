---
name: ads-report
description: "Render Markdown, HTML, or PDF paid-advertising reports from a validated Claude Ads JSON run bundle. Use for ads report, client report, audit PDF, executive audience reporting, or exporting prior audit and plan results."
attached_agents: [release-verifier]
---

# Render Paid Media Reports

1. Accept a validated versioned report bundle, never loose worker prose.
2. Confirm run completeness, evidence coverage, privacy class, branding choice,
   requested audience, and output formats.
3. Render all formats from the same canonical data and deterministic templates.
4. Preserve findings, confidence, evidence references, contradictions, missing
   inputs, actions, owners, and measurement windows.
5. Run structural checks, then visual/layout checks for HTML and PDF.
6. Write atomically inside the run directory and update its manifest.

Do not include credentials, customer lists, private paths, raw research, internal
agent transcripts, or promotional copy unless the operator explicitly enabled
branding. Never hide partial or insufficient-evidence status in an executive
summary.

---

## Operator qatlami (Tyrion lokal bilimi)

### Amaliy bilim yadrosi
- Benchmarks are comparison evidence, not pass/fail controls; never penalize an account merely for differing from a cross-industry median (benchmarks.md).
- Before quoting an external benchmark record source, provenance, publication, population, statistic, measurement, time, fit, and limits; if a conclusion-changing field is unknown, label the benchmark `provisional` (benchmarks.md).
- Compare in the narrowest defensible order: same-account prior comparable period, own experiment or holdout, first-party CRM or revenue cohort, comparable peer cohort with disclosed methodology, then broad industry benchmark labeled directional only (benchmarks.md).
- Never blend sources with different attribution windows, currencies, conversion definitions, or funnel stages without normalizing and disclosing the conversion (benchmarks.md).
- Distinguish CPA = spend / accepted conversions, ROAS = accepted conversion value / spend, and MER = business revenue / total advertising spend; platform ROAS and business MER are not interchangeable (benchmarks.md).
- Every score is published with its coverage status and data window - no letter grades; unknown critical controls still appear in the priority output when total coverage is above 80% (scoring-system.md).
- Coverage statuses: 80-100% graded, 60-79.99% provisional, below 60% insufficient evidence - never present it as an account grade (scoring-system.md).
- Every benchmark comparison reports the observed account value, benchmark value, cohort fit, source ID, confidence, and the decision it informs; a gap is an observation, not a diagnosis (benchmarks.md).
- Never present fixed minimum monthly budgets, vendor uplift percentages, or percentile claims without a population and statistic definition as expected account outcomes (benchmarks.md).

### UZ bozori (agar tegishli bo'lsa)
- Compare local accounts against their own history; global benchmark tables do not transfer (ozbekiston-konteksti.md).
- Season-adjust comparisons: December is the largest sales month, 1 September drives education/clothing/tech, and Ramazan runs on evening activity (ozbekiston-konteksti.md).

### Asosiy manbalar (yuklash tartibida)
- ads/references/benchmarks.md
- ads/references/scoring-system.md


## Deterministic CLI & Tooling Integration (`0 Token`)
Before generating recommendations or mutating plans for `ads-report`, execute the relevant Tyrion v4.0 deterministic checks:
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
