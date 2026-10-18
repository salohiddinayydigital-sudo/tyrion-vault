---
name: ads-test
description: "Design and evaluate paid-ad experiments with hypotheses, randomization units, sample-size and duration assumptions, guardrails, platform experiment tools, analysis, and decision rules. Use for A/B test, split test, experiment design, hypothesis, statistical significance, sample size, test duration, or experiment readout."
attached_agents: [audit-creative, creative-strategist]
---

# Paid Media Experiment

1. State the decision, causal hypothesis, treatment, control, randomization unit,
   population, primary metric, guardrails, minimum effect, and stopping rule.
2. Check platform constraints, overlapping experiments, conversion lag, seasonality,
   interference, and measurement quality.
3. Calculate sample and duration from declared assumptions; disclose approximations.
4. Change one decision surface unless the design explicitly estimates interactions.
5. Pre-register exclusions, quality checks, analysis, and decision thresholds.
6. For readout, verify assignment integrity and data completeness before estimating
   effect and uncertainty.
7. Return setup or readout in versioned JSON with a plain-language decision.

Do not repeatedly peek and stop on a favorable result, call underpowered noise a
winner, or generalize beyond the tested population.

---

## Operator qatlami (Tyrion lokal bilimi)

### Amaliy bilim yadrosi
- Skor/health — production engine authority; eksperiment readoutida ham coverage + data window bilan birga beriladi (scoring-system.md)
- Coverage statuslar: graded / provisional / insufficient_evidence — underpowered dalil winner e'lon qilinishiga yo'l qo'ymaydi (scoring-system.md)
- Dedup qoidasi: bitta kanonik risk — bitta scored control; root tracking failure + har bir symptom alohida penalty sifatida skorlanmaydi (scoring-system.md)
- Rekomendatsiya skor investigationni prioritetlaydi, o'zgarishni avtorizatsiya qilmaydi: finding + confidence + sample size + conversion lag + mutation gate (scoring-system.md)
- Benchmark raqamlari savol manbai, pass/fail control emas — qaror advertiser ekonomikasi va cohort ma'lumotlaridan (benchmarks.md)
- Eng kuchli taqqoslash: o'z akkaunt oldingi davri (comparison order 1-o'rin) — eksperimentda ham baseline to'liq davrlardan, same duration + lag maturity (benchmarks.md)
- Vendor uplift foizlari expected account outcome sifatida berilmaydi; "top performer"/percentile da'volari population va statistika ta'rifisiz yozilmaydi (benchmarks.md)
- Kam hajmli segment uncertain deb qaytariladi — industry average bilan to'ldirilmaydi; aralashtirilgan window/valyuta manbalar normalize qilinmasa aralashtirilmaydi (benchmarks.md)

### Asosiy manbalar (yuklash tartibida)
- `ads/references/scoring-system.md`
- `ads/references/benchmarks.md`


## Deterministic CLI & Tooling Integration (`0 Token`)
Before generating recommendations or mutating plans for `ads-test`, execute the relevant Tyrion v4.0 deterministic checks:
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
