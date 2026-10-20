---
name: ads-attribution
description: "Audit cross-platform attribution, conversion definitions, reporting windows, GA4, AdServices and AdAttributionKit, MMPs, browser and server events, offline conversions, and platform reconciliation. Use for attribution audit, attribution models, conversion windows, requests to add or total Meta and Google conversions, incompatible reporting-window aggregation, GA4 attribution, MMP review, AppsFlyer, Adjust, Branch, Singular, or cross-platform discrepancies."
attached_agents: [audit-tracking, tracking-specialist]
---

# Attribution Audit

1. Read the main `ads` contract and normalized account snapshots.
2. Declare the business conversion, value, data window, timezone, currency, and
   decision the attribution analysis must support.
3. Inventory every browser, server, platform, analytics, MMP, offline, and app
   attribution source with its identity, counting, deduplication, and privacy rules.
4. Reconcile comparable events and explain differences caused by eligibility,
   view-through rules, consent, modeled data, conversion lag, thresholds, or scope.
5. Separate measurement quality from platform-reported performance.
6. Return findings, contradictions, confidence, missing evidence, and a measurement
   improvement plan through the common JSON contract.

Do not assume one platform is ground truth, add incompatible reports together, or
recommend an attribution model without the operator's decision context.

## Comparability gate

Reject aggregation until the sources share, or are explicitly normalized to, the
same conversion event and value definition, attribution window, click/view scope,
counting method, deduplication identity, timezone, currency, attribution model,
and modeled-data treatment. Until then, report the values side by side with their
definitions; do not compute a total.

Example: Meta seven-day conversions and Google thirty-day conversions are
incompatible. Refuse to add them, reconcile windows and definitions first, and
only aggregate a newly comparable dataset.

---

## Operator qatlami (Tyrion lokal bilimi)

### Amaliy bilim yadrosi
- Tag/API borligi o'lchov aniqligini isbotlamaydi — business event, consent holati, browser va server yo'llari, platforma konfiguratsiyasi hamda CRM yozuvi mos kelishi shart (conversion-tracking.md)
- Kanonik event kontrakti: stable nomi, vaqt/timezone, unikal event ID, order/lead ID, valyuta + qiymat ta'rifi (refund/cancellation bilan), origin + dedup kaliti, consent holati, platforma conversion action roli/counting/window (conversion-tracking.md)
- Browser va server nusxalari platformaning hujjatlashtirilgan dedup maydonlarini bo'lishadi; retry idempotent, kech offline update ikkinchi sale yaratmasligi tekshiriladi (conversion-tracking.md)
- Platforma-atributsiya, analytics atributsiyasi, CRM/accounting natijasi va eksperiment smetasi alohida ko'rinishlar — qo'shilmaydi, windowlar va view-through oshkor qilinadi (conversion-tracking.md)
- Audit ketma-ketligi: bitta real test eventni user action -> browser -> server -> platforma -> dedup -> report -> CRM zanjirida kuzatish, lag-mature windowda event-date/proc-date bo'yicha solishtirish (conversion-tracking.md)
- Google consent-mode modeling eligibilitiyasi: to'g'ri consent mode/IAB TCF + 7 kun davomida kuniga ~700 ad click (country/domain guruhi) — Google xususiyati, universal budjet minimali emas (conversion-tracking.md)
- Kritik topilma kuzatilgan ta'sir talab qiladi: no primary event, tasdiqlangan double counting, ruxsatsiz sensitive data, noto'g'ri value/valyuta; faqat server-side integratsiyaning yo'qligi — coverage gap (conversion-tracking.md)
- Review quyidagilar yozilgandagina tugaydi: test qilingan eventlar/muhit/window, consent holati, payload dalili, platforma diagnostikasi, CRM reconciliation, gap, confidence, owner (conversion-tracking.md)

### UZ bozori
- Meta pikselsiz/CAPI'siz hisob — atributsiya cheklangan; bu holat mijozga ochiq aytiladi (ozbekiston-konteksti.md)
- Konversiya qiymati ta'rifi: mijozning Telegramda qolishi (email emas) — CVR va value shu hodisaga quriladi (ozbekiston-konteksti.md)
- Telegramdan qaytganlar uchun pikselsiz Meta'da qayta ko'rsatish mumkin emas — reconciliation va retargeting qamrovida hisobga olinadi (ozbekiston-konteksti.md)

### Asosiy manbalar (yuklash tartibida)
- `ads/references/conversion-tracking.md`
- `local/ozbekiston-konteksti.md`


## Deterministic CLI & Tooling Integration (`0 Token`)
Before generating recommendations or mutating plans for `ads-attribution`, execute the relevant Tyrion v5.0 deterministic checks:
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
