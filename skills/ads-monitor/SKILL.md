---
name: ads-monitor
description: Monitor paid-ad account pacing, delivery, performance, creative fatigue, tracking, policy, and data quality across supported platforms. Use for daily or weekly checks, anomaly review, budget pacing, post-launch verification, or campaign monitoring.
triggers:
- monitoring
- kunlik nazorat
- pacing check
- spend anomaly
- kpi tushib ketdi
- мониторинг рекламы
- кунлик назорат
aliases:
- pacing
- anomaly-detection
- daily-check
domains:
- monitoring
- audit
- budget
platforms:
- multi-platform
attached_agents: [audit-budget, audit-creative]
related_skills:
- ads-optimize
- ads-budget
references:
- skills/ads/references/scoring-system.md
risk_level: low
output_contract: Pacing, CPA/ROAS drift, and creative fatigue early-warning telemetry report
---

# Paid Media Monitoring

1. Load two or more normalized snapshots with compatible account, timezone,
   currency, metric, and attribution definitions.
2. Validate data freshness and finalization windows before comparing periods.
3. Separate expected learning, seasonality, reporting latency, and planned changes
   from unexplained anomalies.
4. Evaluate pacing, delivery, conversion quality, unit economics, creative fatigue,
   tracking health, policy status, and changed account objects.
5. Return observations, confidence, likely causes, required investigation, and
   decision thresholds. Do not mutate the account.
6. Persist a versioned monitoring bundle and link detected failures to regression
   or follow-up tasks.

Do not alert on percentage changes with trivial denominators or incomparable
windows. State when evidence cannot distinguish noise from a material change.

---

## Operator qatlami (Tyrion lokal bilimi)

### Amaliy bilim yadrosi
- Benchmarks are comparison evidence: use them to form a question, then decide from the advertiser's economics, cohort, and same-window account data (benchmarks.md).
- Creative fatigue is a sustained change versus a comparable baseline after accounting for mix and spend shifts, not a static table value (benchmarks.md).
- Frequency findings need the reach window and audience overlap defined, plus evidence that measured performance is deteriorating (benchmarks.md).
- Classify what authority is delegated - goal selection, bidding, budget and pacing, audience or query expansion, placements, creative generation, campaign creation, monitoring and pausing, external agent writes - not whether the campaign carries an "automated" label (automation-tier-classifier.md).
- Tiers run from T0 observed manual through T1 assisted, T2 bounded delegation, T3 broad platform delegation, to T4 external agent write; T4 demands the full mutation gate, least privilege, idempotency, independent verification, and incident response (automation-tier-classifier.md).
- The account tier is the highest active authority, but keep the dimension map; a summary tier alone is not decision-complete (automation-tier-classifier.md).
- Score only stable controls such as missing approval, absent ceilings, conflicting automation, unauthorized scope, broken monitoring, or no rollback; automation adoption and novelty are unscored context (automation-tier-classifier.md).
- Do not prescribe "more automation" or "more manual control" without a diagnosed account problem and a testable expected result (automation-tier-classifier.md).

### UZ bozori (agar tegishli bo'lsa)
- Seasonal windows - Ramazan evenings, Navruz, 1 September, December peak, summer - are expected demand shifts in UZ, not anomalies (ozbekiston-konteksti.md).
- Judge local accounts against their own history, never global benchmark tables (ozbekiston-konteksti.md).

### Asosiy manbalar (yuklash tartibida)
- ads/references/benchmarks.md
- ads/references/automation-tier-classifier.md


## Deterministic CLI & Tooling Integration (`0 Token`)
Before generating recommendations or mutating plans for `ads-monitor`, execute the relevant Tyrion v5.0 deterministic checks:
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
