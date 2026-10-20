---
name: ads-create
description: "Create source-grounded paid-ad campaign concepts, messaging, copy, creative briefs, and production plans from a validated brand profile, campaign objective, platform requirements, and optional audit evidence. Triggers on: campaign brief, campaign concepts, create a campaign, ad concepts, ad copy, ad messaging, creative brief, headlines, descriptions."
attached_agents: [campaign-ideator, copy-writer, format-adapter]
---

# Campaign Concepts and Copy

1. Load the validated setup/brand profile, objective, audience, offer, proof,
   platform/placement requirements, policy context, and optional audit findings.
2. Separate factual claims, operator-approved claims, and creative hypotheses.
3. Generate materially distinct strategic concepts, not cosmetic rewrites.
4. For each concept, define insight, promise, proof, hook, narrative, CTA, objections,
   platform adaptations, destination, and experiment hypothesis.
5. Validate copy limits and policy against current platform references. Load only
   the active files among `ads/references/google-creative-specs.md`,
   `meta-creative-specs.md`, `youtube-creative-specs.md`,
   `linkedin-creative-specs.md`, `tiktok-creative-specs.md`, and
   `microsoft-creative-specs.md`; use the dated source ledger for every current
   specification claim.
6. Return a versioned creative brief and copy deck inside the run directory.

Do not invent testimonials, certifications, scarcity, prices, outcomes, or regulated
claims. Human review remains required before production or launch.

---

## Operator qatlami (Tyrion lokal bilimi)

### Amaliy bilim yadrosi
- Kreativ talablar format/placement/objective/geography/eligibility bo'yicha farqlanadi; "universal platforma spec jadvali" xavfli — turli placementlar talablari aralashtiriladi (platform-specs.md)
- Yechish tartibi: platforma+objective+format+placement+destination+geography+account UI yoziladi, mos platforma referensi ochiladi, volatile limitlar joriy official help/API'dan tekshiriladi (platform-specs.md)
- Manbalar ziddiyatda bo'lsa guess qilinmaydi: check `unknown`, ikkala qiymat saqlanadi, joriy preview/API so'raladi (platform-specs.md)
- Meta placement matritsasi: har Feed/Stories/Reels/carousel/video/messaging uchun official source ID+sana, ratio, dimension, file turi/hajmi, duration, copy maydonlari, safe area, crop/overlay, eligibility (meta-creative-specs.md)
- Meta: auto-placement, enhancements, catalog, music, text variation, image expansion enabled/eligible ekani tekshiriladi; har FB+IG placement preview qilinadi — overlay sirtga qarab o'zgaradi (meta-creative-specs.md)
- Bitta placement safe-zone qoidasi boshqasiga ko'chirilmaydi; "shu ratio universal yaxshi ishlaydi" da'vosi qilinmaydi; rasmni resize qilish — kreativ diversity emas (meta-creative-specs.md)
- Carousel: har karta alohida asset (o'z destination+copy), lekin narrativ kontinuity saqlanadi (meta-creative-specs.md)
- RSA (Google va Microsoft): 15 headline / 4 description gacha, headline maydoni 30 belgi — faqat RSA formatiga tegishli, cross-platform standart emas (platform-specs.md)
- Upload muvaffaqiyati policy approval/rendering isboti emas; "best practice" asset soni/davomiyligi compliance failurega aylantirilmaydi (platform-specs.md)

### UZ bozori
- Har til uchun matn alohida yoziladi (tarjima qilinmaydi); aralash auditoriyada ad setlar til bo'yicha bo'linadi (ozbekiston-konteksti.md)
- Hook xalq tilida, jargon emas: "Poytaxtda kvartira olmoqchimisiz?" (ozbekiston-konteksti.md)
- CTA "Telegramda yozing" — landing'da konversiya email'dan yuqori; lead -> Telegram DM/bot (ozbekiston-konteksti.md)
- Copyga ishonch signallari kiritiladi: sharhlar skrinshoti, mijoz soni, "30 kun kafolat", real jamoa suratlari (ozbekiston-konteksti.md)
- Til tanlovi: Toshkent B2B — ruscha; mintaqalar B2C — o'zbekcha lotin; kirill auditoriya alohida; yoshlar/IT — o'zbekcha + inglizcha aralash (ozbekiston-konteksti.md)

### Meta policy eslatmasi
- `memory.md` qoidasi: Meta policy tekshirilmagan matn berilmaydi — copy chiqishidan oldin FB/IG Advertising Standards bo'yicha tekshiruv majburiy (memory.md)

### Asosiy manbalar (yuklash tartibida)
- `ads/references/meta-creative-specs.md`
- `ads/references/platform-specs.md`
- `local/ozbekiston-konteksti.md`
- `memory.md`


## Deterministic CLI & Tooling Integration (`0 Token`)
Before generating recommendations or mutating plans for `ads-create`, execute the relevant Tyrion v5.0 deterministic checks:
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
