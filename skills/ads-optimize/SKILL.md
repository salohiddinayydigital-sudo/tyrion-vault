---
name: ads-optimize
description: Diagnose and draft or explicitly apply paid-ad optimizations using evidence, financial constraints, experiments, and capability-gated adapters. Use for campaign optimization, budget reallocation, bid changes, pausing or archiving ads, requests to delete campaigns, search-term or negative-keyword actions, creative rotation, or improving CPA and ROAS.
triggers:
- optimizatsiya
- optimize
- kill keep scale
- byudjet oshirish
- masshtablash
- scaling
- оптимизация кампании
- масштабирование
- бюджетни ошириш
aliases:
- scale
- kill-keep-scale
- campaign-optimization
domains:
- optimization
- budget
- scaling
platforms:
- meta
- google
- telegram
- tiktok
- multi-platform
attached_agents: [audit-budget, audit-creative]
related_skills:
- ads-budget
- ads-math
- ads-monitor
references:
- skills/ads/references/bidding-strategies.md
- skills/ads/references/budget-allocation.md
risk_level: high
output_contract: Kill / Keep / Scale decision matrix with +20%/48h Spend-Guard check and rollback trigger
---

# Paid Media Optimization

Default to `--draft`.

1. Load the latest normalized snapshot, prior decisions, monitoring results,
   experiment state, conversion lag, economics, and platform capability manifest.
2. Identify the decision and causal evidence; do not optimize a metric in isolation.
3. Compare no-change, experiment, and mutation options, including learning, policy,
   tracking, inventory, and opportunity-cost effects.
4. Produce ranked recommendations with confidence and success measures.
5. Convert approved recommendations into mutation plans only through the main
   mutation gate.
6. Apply, verify, audit, and retain rollback only when the exact operation is
   enabled and remote state still matches the draft precondition.

Never use a fixed CPA multiple, budget ratio, benchmark, or novelty claim as sole
authorization to change an account.

## Destructive-action boundary

Refuse permanent deletion of campaigns, ad groups, ads, audiences, conversions,
or other account objects. Permanent deletion is outside the supported mutation
contract and cannot be made safe by confirmation. Offer reversible alternatives:
leave objects paused, archive where supported, apply labels, export a backup, and
define a retention or later-review date. Do not create or apply a delete plan.

Search-term actions require a search terms report, business-relevance evidence,
and an overblocking review. Without them, request the missing evidence and do not
invent or illustrate specific negative keywords.

---

## Operator qatlami (Tyrion lokal bilimi)

### Amaliy bilim yadrosi
- Health skorning yagona manbai production engine; prompt/agent/report uni qayta implement qilmaydi (scoring-system.md)
- 4 output alohida: health_score (0-100), evidence_coverage, regulatory_exposure (P0/P1), opportunities — letter grade yo'q, coverage + data window bilan birga (scoring-system.md)
- Control holatlari: pass / fail / unknown / not_applicable; unknown health'dan chiqib coverage'da qoladi, not_applicable ikkalasidan chiqadi (scoring-system.md)
- Severity og'irliklari: critical 5, high 3, medium 1, informational 0 — yangilik yoki strategik qiziqish uchun oshirilmaydi (scoring-system.md)
- Coverage: 80-100 graded · 60-79.99 provisional · <60 insufficient_evidence — yetarli dalilsiz health akkaunt bahosi sifatida berilmaydi (scoring-system.md)
- Meta referens profil: measurement 25, creative 25, structure 20, audiences 15, delivery 10, policy 5 — joriy v1 profillar disabled, runga og'irlik ko'chirilmaydi (scoring-system.md)
- Portfolio health: platforma spend share bilan og'irlanadi; spend yo'q — equal-weight + provisional; insufficient-evidence platforma agregatga kirmaydi, missing weight ko'rsatiladi (scoring-system.md)
- Automation tierlari T0 (manual) -> T4 (external agent write); akkaunt tier — eng yuqori avtoritet, lekin dimension xaritasi ham saqlanadi (automation-tier-classifier.md)
- "Automated" yorlig'i emas, haqiqiy delegatsiya klassifikatsiya qilinadi: goal/bidding/budget/audience expansion/placement/creative/structure/monitoring/external MCP — har biri alohida (automation-tier-classifier.md)

### UZ bozori
- Optimizatsiya me'yori — akkauntning O'Z tarixi (global benchmark emas) (ozbekiston-konteksti.md)
- Auditoriya qidiruv tili bo'yicha bo'linadi — tilga ajratilgan ad setlar segment sifatini oshiradi (ozbekiston-konteksti.md)
- Pikselsiz/CAPI'siz Meta hisobda atributsiya cheklangan — optimize qarorlari shu cheklov bilan baholanadi (ozbekiston-konteksti.md)

### Asosiy manbalar (yuklash tartibida)
- `ads/references/scoring-system.md`
- `ads/references/automation-tier-classifier.md`
- `local/ozbekiston-konteksti.md`
