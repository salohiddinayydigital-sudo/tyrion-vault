---
name: ads-competitor
description: "Research competitor paid-ad presence, messaging, creative, formats, landing pages, keyword and auction signals, transparent ad libraries, and strategic gaps across supported platforms. Use for competitor ads, ad libraries, ad spy, competitive PPC analysis, competitor creative, Google Ads Transparency, Meta Ad Library, or paid-media competitor research."
attached_agents: [positioning-strategist, research-worker, source-verifier]
---

# Competitor Ad Intelligence

1. Confirm named competitors, market, geography, customer, objective, and decision.
2. Use official transparency libraries, public ads, auction data supplied by the
   operator, and other terms-compliant sources.
3. Record capture date, platform, placement, observable creative/message, landing
   destination, and source URL.
4. Separate direct observations from inferred audience, spend, performance, or
   strategy; never present estimates as account facts.
5. Cluster durable themes, formats, offers, funnel paths, and gaps without copying
   protected creative or text.
6. Return evidence-backed opportunities, risks, experiments, and source records.

Respect platform terms, robots and access controls, copyright, trademarks, and
privacy. Do not bypass authentication or scrape private account surfaces.

---

## Operator qatlami (Tyrion lokal bilimi)

### Amaliy bilim yadrosi
- Benchmark raqamlari pass/fail control emas — qaror akkaunt ekonomikasi, cohort va same-window ma'lumotlaridan; cross-industry mediandan farqi uchun akkaunt ayblanmaydi (benchmarks.md)
- Evidence kontrakti (9 maydon): source (publisher + URL + ledger ID), provenance, publication/retrieval sanasi, population, statistic, measurement (numerat/denominat/window/valyuta), time, fit, limits (benchmarks.md)
- Biror field noaniq bo'lsa benchmark `provisional`; platforma-published uplift `vendor-supplied`; case study umumiy baseline emas (benchmarks.md)
- Taqqoslash tartibi (toridan kengiga): 1) o'z akkaunt oldingi davri, 2) eksperiment/holdout, 3) first-party CRM cohort, 4) metodologiyasi oshkora peer cohort, 5) keng industry — faqat directional (benchmarks.md)
- Atributsiya window/valyuta/konversiya ta'rifi/funnel bosqichi turlicha manbalar normalizatsiya + disclosure'siz aralashtirilmaydi (benchmarks.md)
- CPA = spend/accepted conversions · ROAS = accepted value/spend · MER = business revenue/total spend; gross/net va spend tarkibi (fees/credits/taxes) oshkor bo'lishi shart (benchmarks.md)
- Gap (farq) — kuzatuv, diagnostika emas; tavsiya gapni akkaunt daliliga bog'laydi: marginal samaradorlik, query quality, kreativ decay, incrementality (benchmarks.md)
- Har taqqoslashda: observed qiymat, benchmark qiymati, cohort fit, source ID, confidence va qaror yoziladi (benchmarks.md)
- Taqiqlangan: population/statistik ta'rifsiz "top performer"/percentile da'volari, fiksatsiyalangan minimal budjet/konversion-count/creative-life thresholdlari universal haqiqat sifatida (benchmarks.md)

### Asosiy manbalar (yuklash tartibida)
- `ads/references/benchmarks.md`


## Deterministic CLI & Tooling Integration (`0 Token`)
Before generating recommendations or mutating plans for `ads-competitor`, execute the relevant Tyrion v4.0 deterministic checks:
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
