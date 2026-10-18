---
name: ads-launch
description: "Draft or explicitly apply a paid-ad campaign launch through Claude Ads capability-gated adapters. Use for campaign creation, launch plans, publishing ads, activating campaigns, uploading creative, or requests to push a campaign live."
attached_agents: [launch-planner]
---

# Campaign Launch

Default to `--draft`.

1. Load the validated setup profile, account snapshot, campaign plan, creative
   manifest, platform capability manifest, policy findings, and tracking checks.
2. Refuse a draft that lacks account/object scope, objective, conversion, budget,
   dates, targeting, assets, destinations, measurement, or policy eligibility.
3. Produce a deterministic mutation plan with exact proposed objects, before/after
   state, blast radius, learning impact, owner, success measure, verification
   window, idempotency key, audit destination, and rollback.
4. For `--apply`, require the exact operation to be enabled and independently
   tested, then obtain explicit approval for that exact plan.
5. Apply the smallest reversible change, verify remote state, and preserve the
   immutable audit and rollback record.

Missing ceilings, stale account state, changed remote state, incomplete tracking,
failed policy review, or an unavailable adapter blocks apply. Permanent deletion is
not supported.

---

## Operator qatlami (Tyrion lokal bilimi)

### Amaliy bilim yadrosi
- Status/next deterministik yadrodan: `python -m claude_ads_core status|next --root . --as-of YYYY-MM-DD`; readiness proza'dan chiqarilmaydi, network call qilinmaydi (status-contract.md)
- `artifact-order-v1` bitta natija tanlaydi: unverified load-bearing claim -> stale load-bearing claim -> maturity blocker -> canonical release check -> disabled profile -> disabled capability -> past maturity (status-contract.md)
- Repository manifestlari + ixtiyoriy report — yagona evidence; missing/malformed input fail closed (status-contract.md)
- Write tool default disabled; apply shartlari: exact operation live-write-verified, aniq account/object ID + fresh normalized snapshot, before/after diff, owner approval (aynan o'sha plan uchun), idempotency key, audit destination, verification window, rollback (mcp-integration.md)
- Remote state `before`ga mos kelmasa plan qayta tuziladi; bir kampaniya/budjet/sana uchun berilgan approval boshqasiga o'tmaydi (mcp-integration.md)
- Noaniq write timeoutdan keyin ikkinchi applyga qadar idempotency key bilan remote state o'qiladi (mcp-integration.md)
- "Ishga tushir" kabi natural-language tasdiq aniq mutation plan uchun approval o'rnini bosmaydi; permanent deletion supported emas (mcp-integration.md)

### Asosiy manbalar (yuklash tartibida)
- `ads/references/status-contract.md`
- `ads/references/mcp-integration.md`


## Deterministic CLI & Tooling Integration (`0 Token`)
Before generating recommendations or mutating plans for `ads-launch`, execute the relevant Tyrion v4.0 deterministic checks:
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
