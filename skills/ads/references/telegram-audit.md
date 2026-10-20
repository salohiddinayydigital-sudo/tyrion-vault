# Telegram Ads Audit Reference

This reference specifies evidence controls, account structures, targeting models, copy specifications, and measurement standards for the official **Telegram Ads** platform (`ads.telegram.org` / Fragment).

---

## 1. Scope & Applicability

Telegram Ads is a privacy-first, direct-response and channel-growth advertising platform operating on public Telegram channels and bots.

Before auditing or recommending Telegram Ads:
- Identify account currency (TON, Telegram Stars, or EUR via Fragment/authorized resellers).
- Identify campaign destination (`t.me/channel`, `t.me/bot`, specific `t.me/post`, or external web URL).
- Confirm daily budget cap, maximum CPM bid, target language, and geographic target.

---

## 2. Core Audit Controls (T01 - T15)

### Channel & Audience Quality
- **T01 — Target Channel Affinity & Subscriber Quality:**
  - Evaluates whether hand-picked public channels have active, real subscribers (>1,000 subscribers required by platform).
  - Engagement Rate (ERR = Views per post / Total subscribers) should be >15%.
  - Dead channels with inflated bot subscriber counts or sudden unorganic spikes must be excluded.
- **T02 — Specific Channels vs Broad Topics:**
  - *Pass:* Specific channel targeting is utilized for core conversion campaigns.
  - *Risk:* Over-reliance on broad topical categories (e.g., general "Finance" or "IT") without specific channel whitelisting causes budget leakage.
- **T03 — Channel Language & Geographic Alignment:**
  - Ensures ads in Uzbek or Russian are targeted only to channels whose primary audience and language match.
  - Exclude irrelevant regional channels.

### Ad Copy & Creative Formatting
- **T04 — 160-Character Strict Limit:**
  - Text must strictly be $\le 160$ characters (including spaces).
  - Must include a clear Value Proposition + Explicit Call to Action.
- **T05 — Content Moderation & Policy Compliance:**
  - **No Clickbait:** Exclamatory sensationalism ("SHOCKING", "YOU WON'T BELIEVE") triggers immediate rejection.
  - **Capitalization:** ALL CAPS words are prohibited unless they are registered trademarks or standard acronyms (e.g., B2B, AI, CRM).
  - **Emoji Policy:** Max 1 emoji per ad, strictly relevant to context; no repetitive or flashy emoji sequences.
  - **Truth in Advertising:** No unverifiable claims, income guarantees ("Earn $10k/month"), or exaggerated superlatives ("The #1 best in the world").

### Conversational Funnel & Telemetry
- **T06 — Deep Linking Architecture:**
  - Every ad pointing to a bot must pass structured campaign parameters:
    `https://t.me/BrandBot?start=utm_source_campaign_angle`
- **T07 — Bot Response Velocity:**
  - Automated welcome message and promised lead magnet must fire within $<10$ seconds of clicking `/start`.
  - Drop-off occurs rapidly if bot latency exceeds 15 seconds.
- **T08 — Server-Side Telemetry & Event Webhooks:**
  - Since Telegram does not support third-party tracking pixels, the bot backend must send webhooks to CRM / Analytics for:
    1. `/start` (Entry / Impression-to-Lead)
    2. Lead Magnet Download (Activation)
    3. Contact Form / Phone Submission (MQL)
    4. Sales Qualification (SQL)
    5. Payment / Deal Closure (Revenue)

### Bidding, Pacing & Unit Economics
- **T09 — CPM Auction Optimization:**
  - Monitor CPM bid vs winning impression share.
  - High-demand channels require competitive bids (€2.50 - €5.00+ CPM / 1-3+ TON).
  - Low-bid starvation: if ad has 0 impressions after 24h, bid is below auction clearing threshold.
- **T10 — Daily Spend Guard & Pacing:**
  - Daily spend limit must be set to prevent rapid exhaustion in massive channels.

---

## 3. High-Converting 160-Character Copy Formulas

1. **Problem $\to$ Direct Solution:**
   `Qimmat marketingdan charchadingizmi? Telegram Ads orqali har bir lid narxini 2x arzonlashtiring. Bepul audit oling:`
2. **Social Proof $\to$ Curiosity:**
   `Toshkentdagi 40+ kompaniya qanday qilib Telegram botdan oyiga $50,000+ sotuv qildi? Case study'ni o'qing:`
3. **Direct Callout $\to$ Value Hook:**
   `Targetologlar uchun: Andromeda va Google Ads bo'yicha 84 ta tayyor SOP va amaliy darslik. Botdan yuklab oling:`
