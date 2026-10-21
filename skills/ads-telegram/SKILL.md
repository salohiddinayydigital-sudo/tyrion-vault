---
name: ads-telegram
description: Audit, plan, draft, and optimize Telegram Ads campaigns across ads.telegram.org and Fragment. Covers channel targeting, 160-character copywriting formulas, CPM bidding, bot conversational funnels, server-side webhooks, and policy compliance.
triggers:
- telegram ads
- telegram reklama
- tg ads
- telegram bot voronka
- cpm telegram
- телеграм реклама
- телеграм эдс
- телеграм бот воронка
aliases:
- tg-ads
- telegram-funnel
- telegram-sponsored
domains:
- audit
- paid-media
- telegram
platforms:
- telegram
attached_agents: [audit-telegram]
related_skills:
- uzbekistan-market-intel
- ads-plan
- copywriting
references:
- skills/ads/references/telegram-audit.md
risk_level: low
output_contract: Telegram Ads audit & funnel architecture (160-char copy compliance, <=64-byte start= UTM, Bot -> CRM CVR)
---

# Telegram Ads Operating Playbook

## Procedure

1. **Intake & Verification**:
   - Determine buying currency (TON, Stars, or EUR via Fragment/authorized agency).
   - Identify target destination: Public Channel (`t.me/channel`), Bot (`t.me/bot`), specific post, or external website.
   - Define business objective: Channel Subscribers, Bot Leads, Website Traffic, or Direct Sales.
2. **Channel Research & Selection**:
   - Vet candidate public channels: verify subscriber count $\ge 1,000$, Engagement Rate on Reach (ERR) $\ge 15\%$, and organic view consistency.
   - Separate specific channel targets from broad topical categories.
3. **160-Character Copywriting**:
   - Write strictly within the 160-character limit.
   - Formulate distinct variations: Problem/Solution, Curiosity/Case Study, Direct Audience Callout.
   - Ensure moderation compliance: max 1 contextual emoji, no ALL CAPS, no sensationalist clickbait, no unverifiable income promises.
4. **Conversational Funnel & Bot Setup**:
   - Verify deep linking: `t.me/Bot?start=utm_source_campaign_angle`.
   - Test bot response speed: automated greeting and lead magnet delivery must fire in $<10$ seconds.
   - Ensure CRM webhook integration tracks `/start`, activation, lead, and sale.
5. **Auction Bidding & Pacing**:
   - Set initial CPM bid based on channel authority (start at benchmark floor + 20-30% to clear auction).
   - Implement daily spend caps to prevent rapid budget exhaustion.
6. **Delivery & Reporting**:
   - Present findings as a structured audit or launch Change Packet conforming to `rules/50-topshirish-dod.md`.

## Boundaries & Safety Gates

- Read-only default: never modify bids or campaigns in ad cabinets without explicit user confirmation (`rules/40-xavfsizlik-va-hisob.md`).
- Never evaluate Telegram Ads on click-through rate (CTR) alone; evaluate cost per qualified lead (CPQL) and closed revenue.
- Do not borrow global benchmarks: evaluate campaigns against the client's historical benchmarks and local conversion dynamics.

---

## Operator qatlami (Tyrion lokal bilimi)

### Amaliy bilim yadrosi
- Telegram Ads CPM auction operates on dynamic competitive bidding; zero impressions within 24h indicates bid starvation below floor.
- Channel-specific targeting yields 2-4x higher conversion efficiency compared to broad category targeting in Central Asian and CIS markets.
- All ad text must be natively written in target scripts (Uzbek Latin, Uzbek Cyrillic, or Russian); machine translation triggers high rejection rates and low engagement.
- Policy clearance: Telegram Ads moderation is strict on punctuation, formatting, and claims. Tone must be neutral, professional, and informative.

### Bog'liq manbalar
- `ads/references/telegram-audit.md`
- `wiki/telegram-voronka-va-email-minimum.md`
- `wiki/telegram-ads-platformasi.md`


## Deterministic CLI & Tooling Integration (`0 Token`)
Before generating recommendations or mutating plans for `ads-telegram`, execute the relevant Tyrion v5.0 deterministic checks:
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
