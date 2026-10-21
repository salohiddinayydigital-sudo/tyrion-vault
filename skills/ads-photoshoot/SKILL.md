---
name: ads-photoshoot
description: 'Generate rights-cleared paid-ad product photography variants from an authorized source image and validated brand profile. Triggers on: product photo, product photography, virtual photoshoot, photoshoot, enhance product image, studio shot, lifestyle shot, lifestyle product image, floating product image, ingredient shot.'
triggers:
- mahsulot fotosessiyasi
- product photoshoot
- ai photoshoot
- ' mahsulot rasmi'
- предметная съемка
- фотосессия товара
aliases:
- product-photo
- photoshoot-brief
domains:
- creative
- design
- ecommerce
platforms:
- meta
- instagram
- ecommerce
- multi-platform
attached_agents: [visual-designer]
related_skills:
- ads-generate
- web-design-guidelines
references:
- skills/ads/references/image-providers.md
risk_level: low
output_contract: Shot list, lighting/composition brief, and placement aspect-ratio specs
---

# Product Photography Variants

1. Confirm rights to the product image and collect the validated brand profile,
   product facts, intended placements, provider capability, cost ceiling, and output
   root.
2. Preserve product geometry, packaging, logos, labels, color, and material unless
   the operator explicitly approves a change.
3. Define distinct production hypotheses such as studio, contextual use, ingredient
   story, scale/detail, or lifestyle; do not imply unsupported product outcomes.
4. Generate approved aspect ratios and record source hashes, prompt version,
   provider/model, cost, output hashes, and dimensions.
5. Validate product fidelity, visual defects, safe zones, accessibility, and policy.
6. Store assets and manifest atomically inside the run directory.

Human review is mandatory. Do not create deceptive before/after evidence, people or
endorsements without authorization, or regulated claims from visual implication.

---

## Operator qatlami (Tyrion lokal bilimi)

### Amaliy bilim yadrosi
- Claude Ads default image provider/model/narx/rate limit promise qilmaydi — capability discovery har run'da, amalda ishlatilgani yoziladi (image-providers.md)
- Providerning ratio supporti ad platforma upload talabini o'rnatmaydi — validated placement matritsasi bilan taqqoslanadi (image-providers.md)
- Prompt normalized owner-approved maydonlardan: subject/action/environment/composition (placement specdan), brand style + exclusions, disclosure/accessibility/rights (image-providers.md)
- Konfidensial brand asset/personal data tashqi providerga approvaldan keyingina; rights-cleared reference `CLAUDE_ADS_INPUT_ROOT` ostida, faqat relative path (image-providers.md)
- Reference image chegarasi: absolute/traversal/symlink va >20 MiB rad; PNG subset (bounded, 8-bit, non-interlaced grayscale/RGB, optional alpha) — palette/16-bit/interlaced/JPEG avval konvert qilinadi (image-providers.md)
- Throttling/transient xato — providerning dokumentlangan retry qoidasi, aniq attempt + cost ceiling ichida; auth/billing/policy/schema xatosi operator harakatini talab qiladi, auto-retry loop emas (image-providers.md)
- Output: unique run directory, collision-resistant nom, atomic write; har asset uchun hashes, checksum, dimensions, cost, provenance, safety, human approval (image-providers.md)
- Shipped JSON/reportga raw prompt, credentials, resolved absolute path yozilmaydi; prompt hash yonida canonical `[redacted: raw prompt is ephemeral and is not persisted]` summary (image-providers.md)

### UZ bozori
- 90%+ trafik mobil — vertikal/telefon formatlari asosiy yo'nalish (ozbekiston-konteksti.md)
- Kreativda ishonch signallari 2-3 soniyada ko'rinishi kerak — kompozitsiya qarorlarida hisobga olinadi (ozbekiston-konteksti.md)

### Asosiy manbalar (yuklash tartibida)
- `ads/references/image-providers.md`
- `local/ozbekiston-konteksti.md`


## Deterministic CLI & Tooling Integration (`0 Token`)
Before generating recommendations or mutating plans for `ads-photoshoot`, execute the relevant Tyrion v5.0 deterministic checks:
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
