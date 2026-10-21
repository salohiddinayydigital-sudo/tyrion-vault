---
name: ads-plan
description: Create a professional paid-advertising strategy covering objectives, economics, platform selection, campaign architecture, audiences, budget, creative, measurement, experiments, governance, rollout, and reporting. Use for ad plan, media plan, PPC strategy, paid-social strategy, campaign architecture, advertising roadmap, or channel planning.
triggers:
- marketing strategiya
- media plan
- to'liq marketing strategiyasi
- kampaniya rejasi
- voronka loyihalash
- маркетинговая стратегия
- медиаплан
- маркетинг стратегияси
aliases:
- media-plan
- marketing-strategy
- funnel-plan
domains:
- strategy
- planning
- funnel
platforms:
- multi-platform
attached_agents: [campaign-ideator, content-planner, launch-planner]
related_skills:
- ads-budget
- ads-meta-audience
- product-marketing
- offers
- uzbekistan-market-intel
references:
- skills/ads/references/thinking-framework.md
- skills/ads/references/budget-allocation.md
risk_level: medium
output_contract: End-to-end Paid Media & Funnel Strategy Plan (Channel Mix, Audience Layers, Creative Matrix, Unit Economics, KPIs)
---

# Paid Media Plan

1. Read the setup profile, business economics, evidence, current account state, and
   relevant industry template as optional input.
2. Define objective, customer, offer, conversion, value, constraints, geography,
   regulated category, time horizon, and success criteria.
3. Evaluate channel roles and exclusions from first principles; do not require every
   supported platform. For a channel outside the twelve-platform contract, load
   `ads/references/additional-platforms.md` and return a research lead unless
   its current buying, eligibility, measurement, and creative evidence is present.
4. Specify campaign architecture, audience strategy, creative system, budget and
   pacing, measurement, experiments, policy controls, and operating cadence.
5. Phase prerequisites before launch, learning, optimization, and scale.
6. Assign every action an owner, timing, dependency, guardrail, evidence, success
   measure, and rollback or exit condition.
7. Return canonical JSON and render the requested human plan.

A plan is advisory. It becomes an account change only through launch or optimize
mutation gates.

---

## Operator qatlami (Tyrion lokal bilimi)

### Amaliy bilim yadrosi
- Budjet business constraint va marginal evidence'dan taqsimlanadi; fixed platforma mix, minimal oylik spend yoki universal scaling step bilan boshlanmaydi (budget-allocation.md)
- Kirish talablari: accepted outcome, margin + variable cost, cash/credit/monthly/daily/platform/campaign ceiling, owner-approved target CPA, conversion lag, joriy spend/value/confidence; ceiling yo'q — write blok, ekonomika yo'q — plan provisional (budget-allocation.md)
- Core math: break_even_CPA = contribution per accepted conversion; break_even_ROAS = 1/contribution_margin_rate; marginal CPA/ROAS incremental asosda; profit platforma ROASidan infer qilinmaydi (budget-allocation.md)
- Taqsimlash: 1) majburiy commitment + measurement, 2) ijobiy marginal contribution dalilli kampaniyalar, 3) bounded eksperimentlar (hypothesis, MDE, decision date, stop), 4) contingency faqat aniq ishlatilishi bo'lsa, 5) reallocation — eng zaif MARGINAL opportunitydan (eng yomon CPA emas) (budget-allocation.md)
- "Proven/growth/experiment" split — operator siyosati, default emas; tanlangan split va rationale run manifestga yoziladi (budget-allocation.md)
- Scale sharti: data lag orqali mature, tracking/consent/policy/inventory/landing sog'lom, marginal natija owner boundary ichida, eligibility, cash-volatility absorption, before/after + verification window + rollback mavjud (budget-allocation.md)
- Pause qarori: spend fixed CPA multiple oshdi — yolg'iz sabab emas; avval conversion lag, outage, sample, lead quality, seasonality, eksperiment ehtiyoji tekshiriladi (budget-allocation.md)
- Benchmark raqamlari pass/fail control emas; eng tor taqqoslash — o'z akkaunt oldingi davri, eksperiment/holdout ikkinchi (benchmarks.md)

### UZ bozori
- Kanal ustuvorligi: Telegram 1 (biznes kommunikatsiya), Instagram 2 (B2C), YouTube uzun-forma ishonch, Facebook katta yosh + ba'zi B2B (bir kabinet), TikTok yoshlar, LinkedIn juda tor — faqat xalqaro/IT B2B (ozbekiston-konteksti.md)
- Voronka: Meta Ads (FB/IG) -> Telegram DM/bot -> Payme/Click/naqd; email ketma-ketlik o'rniga Telegram voronkasi (kanal + bot + shaxsiy DM) (ozbekiston-konteksti.md)
- Mavsum: Navro'z (21-mart) kuchli oyna, 1-sentabr ta'lim/kiyim/texnika, dekabr — eng katta savdo oyi, Ramazon kechqurun aktivlik, yoz — ko'chmas mulk/sayohat/to'y (ozbekiston-konteksti.md)
- Auditoriya aralash bo'lsa reklama to'plamlari til bo'yicha bo'linadi (bir ad set o'zbekcha, biri ruscha); 3 til alohida yoziladi (ozbekiston-konteksti.md)
- Telegramdan qaytganlarni pikselsiz Meta'da qayta ko'rsatib bo'lmaydi — retargeting strategiyasi lead'ni Telegramda ushlab qolishga quriladi (ozbekiston-konteksti.md)
- Benchmark'lar global emas — akkauntning O'Z tarixi bilan solishtiriladi (ozbekiston-konteksti.md)

### Asosiy manbalar (yuklash tartibida)
- `ads/references/budget-allocation.md`
- `ads/references/benchmarks.md`
- `local/ozbekiston-konteksti.md`


## Deterministic CLI & Tooling Integration (`0 Token`)
Before generating recommendations or mutating plans for `ads-plan`, execute the relevant Tyrion v5.0 deterministic checks:
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
