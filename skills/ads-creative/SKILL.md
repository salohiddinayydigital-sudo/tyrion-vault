---
name: ads-creative
description: "Audit paid-ad copy, images, video, hooks, concepts, format coverage, platform-native fit, message match, creative fatigue, accessibility, and policy across supported platforms. Use for creative audit, ad creative, creative fatigue, creative diversity, ad copy review, video review, image review, or production priorities."
attached_agents: [audit-creative, creative-strategist, format-adapter]
---

# Creative Audit

1. Inventory assets by concept, hook, offer, format, placement, audience, date, and
   performance window; cosmetic resizes are not distinct concepts.
2. Load only active-platform specifications and current policy sources.
3. Evaluate attention, clarity, brand/offer evidence, platform-native execution,
   accessibility, destination match, format/safe-zone compliance, and disclosure.
4. Diagnose fatigue only from time-series delivery and response evidence, not age
   alone.
5. Keep creative quality, format compliance, and measured performance separate.
6. Return prioritized refresh or experiment briefs with hypothesis, audience,
   format, owner, success measure, and evidence.

Do not claim a universal refresh cadence, creative count, sound behavior, or
performance threshold. Preserve human review for emotional and cultural judgment.

---

## Operator qatlami (Tyrion lokal bilimi)

### Amaliy bilim yadrosi
- Joriy copy/asset/placement/policy cheklovlari registry orqali yechiladi: platforma -> joriy source ID; authoritative — `control-plane/manifests/source-ledger.json` (locator, retrieval date, refresh holati) (creative-source-registry.md)
- Faqat orchestration packetda nomlangan platforma/placement yechiladi; placement/field/locale/policy qoidasi yo'q, eskirgan yoki ziddiyatli bo'lsa `needs_input` (creative-source-registry.md)
- Bir platforma limiti boshqa platformadan yoki oldingi run'dan infer qilinmaydi; guidance/example/observed performance mandatory thresholdga aylantirilmaydi (creative-source-registry.md)
- Joriy source provider capabilityni isbotlamaydi — asset tekshirilishidan oldin runtime capability alohida tasdiqlanadi (creative-source-registry.md)
- Voice-to-style xaritalash hipoteza beradi, deterministik emas: approved assetlar, accessibility, kultura, audience va brief ustun turadi (voice-to-style.md)
- 6 o'q: formal_casual, rational_emotional, bold_subtle, traditional_innovative, expert_accessible, playful_serious — har biri Low/Mid/High range uchun vizual deskriptorlar (voice-to-style.md)
- Qo'llash: skorlarni olish -> kandida deskriptorlarni contradiction/stereotype/inaccessible/cultural-xavfga tekshirish -> dalil zaif bo'lsa kamida 2 material-distinct yo'nalish (voice-to-style.md)
- Natijadagi [STYLE] bitta hipoteza — brand identifikatsiyasi isboti yoki natija kafolati emas; tanlangan yo'nalish + owner approval kreativ manifestga yoziladi (voice-to-style.md)

### UZ bozori
- Ishonch signallari kreativda 2-3 soniyada ko'rinishi kerak: video-sharh, raqamlar (ozbekiston-konteksti.md)
- Video-sharh matnli sharhdan kuchli; real jamoa suratlari — stok emas (ozbekiston-konteksti.md)
- Mobil birinchi: 90%+ trafik telefondan — kreativ vertikal, matn qisqa (ozbekiston-konteksti.md)

### Meta policy eslatmasi
- FB/IG kreativ/copy review'da ham `memory.md` qoidasi ishlaydi: Meta policy tekshirilmagan matn berilmaydi (memory.md)

### Asosiy manbalar (yuklash tartibida)
- `ads/references/creative-source-registry.md`
- `ads/references/voice-to-style.md`
- `local/ozbekiston-konteksti.md`
- `memory.md`


## Deterministic CLI & Tooling Integration (`0 Token`)
Before generating recommendations or mutating plans for `ads-creative`, execute the relevant Tyrion v5.0 deterministic checks:
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
