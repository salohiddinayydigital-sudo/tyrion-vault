---
name: ads-math
description: "Calculate and model paid-media CPA, CPL, CPC, CPM, ROAS, MER, break-even targets, contribution margin, LTV:CAC, impression-share opportunity, budgets, forecasts, and experiment economics. Use for PPC math, ad calculator, break-even analysis, ROAS calculator, CPA calculator, budget forecast, LTV CAC, or MER."
attached_agents: [audit-budget]
---

# Paid Media Financial Model

1. Identify the decision and collect units, currency, period, tax/refund treatment,
   margin, attribution basis, and uncertainty.
2. Show the formula and map every input to an operator value or cited artifact.
3. Validate denominators, sign, missing values, incompatible windows, and unit
   conversions.
4. Calculate base, downside, and upside cases where uncertainty affects the decision.
5. Keep platform-attributed revenue, blended business revenue, cash flow, and
   contribution margin distinct.
6. Return machine-readable inputs, formulas, outputs, sensitivities, and decision
   implications.

Never fabricate missing financial inputs, hide division-by-zero, or present a point
forecast without its assumptions.

---

## Operator qatlami (Tyrion lokal bilimi)

### Amaliy bilim yadrosi
- CPA = spend/accepted conversions · ROAS = accepted value/spend · MER = business revenue/total spend; platforma ROAS va business MER turli savollarga javob — almashinadigan emas (benchmarks.md)
- Revenue gross/net ekani va spend tarkibi (fees, credits, taxes) har hisobda oshkor bo'lishi shart (benchmarks.md)
- Baseline faqat to'liq davrlardan (outage chiqarilgan); comparison same duration + conversion-lag maturity; delta = (comparison - baseline) / baseline (benchmarks.md)
- Har benchmark uchun 9 maydon evidence kontrakti; noaniq field -> `provisional`; vendor uplift foizi expected outcome sifatida berilmaydi (benchmarks.md)
- Metric interpretatsiyasidan oldin savol: CTR — qaysi impression/click ta'rifi va placement; CVR — qaysi conversion/denominator/lag/consent; ROAS — value source, returns, cohort (benchmarks.md)
- Segmentatsiya faqat qaror uchun yetarli observation bo'lganda; kam hajmli segment uncertain deb ko'rsatiladi, industry average bilan to'ldirilmaydi (benchmarks.md)
- Taqqoslash narrowest bosqichdan boshlanadi: o'z akkaunt oldingi davri birinchi o'rinda (benchmarks.md)
- Taqiqlangan: fixed monthly minimal byudjet "platforma talabi" sifatida, fixed CPA/frequency/creative-life/budget-to-CPA threshold universal haqiqat sifatida (benchmarks.md)

### UZ bozori
- Benchmark'lar global emas — akkauntning O'Z tarixi bilan solishtiriladi (ozbekiston-konteksti.md)
- CPA hisobida konversiya qiymati = mijozning Telegramda qolishi (email emas) (ozbekiston-konteksti.md)

### Asosiy manbalar (yuklash tartibida)
- `ads/references/benchmarks.md`
- `local/ozbekiston-konteksti.md`


## Deterministic CLI & Tooling Integration (`0 Token`)
Before generating recommendations or mutating plans for `ads-math`, execute the relevant Tyrion v5.0 deterministic checks:
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
