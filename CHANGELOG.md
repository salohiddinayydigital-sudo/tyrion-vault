# Changelog

All notable changes to **Tyrion** are documented in this file.

## [5.0.0] - 2026-10-20 — Calibrated Recommendation Engine, Live Meta Insights Sync & Single-Source Parity

### Added
- **Detailed Targeting Accuracy Engine (`tools/meta-targeting-engine.py`, `docs/DETAILED-TARGETING-ACCURACY.md` & MCP `tyrion_meta_detailed_targeting`)**:
  - Zero-hallucination 6-status verification system (`VERIFIED_AVAILABLE`, `FOUND_NOT_VALIDATED`, `UNAVAILABLE_OR_CONSOLIDATED`, `RELATED_UNVERIFIED`, `NOT_FOUND`, `API_UNAVAILABLE`).
  - Multi-endpoint Meta Marketing API v26.0 integration (`/search?type=adinterest`, `/{ad-account-id}/targetingsearch`, `/{ad-account-id}/targetingsuggestions`, `/{ad-account-id}/targetingvalidation`) with `paging.next` pagination, `(id, type)` deduplication, multilingual query expansion (`uz_latin`, `uz_cyrillic`, `ru`, `en`), and TTL cache validation.
- **Live Meta Ads Insights Connector (`tools/meta-insights-sync.py` & MCP `tyrion_meta_live_insights`)**: Pulls live campaign, ad set, and ad telemetry from [Meta Graph API v26.0](https://developers.facebook.com/docs/graph-api/changelog/version26.0/) (`/act_<id>/insights`) or validates raw Graph API JSON exports (`actions`, `action_values`), normalizes conversions/revenue, and pipes them into `ad-export-analyzer.py`.
- **Confidence Intervals & Model Disclosures (`tools/meta-audience.py`)**:
  - `saturation` now accepts `--active-reach-ratio` and `--measured-freq-7d`, outputs `estimated_fatigue_window_days` (`conservative_early_fatigue_day`, `baseline_fatigue_day`, `optimistic_late_fatigue_day`), and includes `model_disclosure` (`HEURISTIC_PRIOR_MODEL` vs `MEASURED_ACCOUNT_DATA`).
  - `architect` now derives `target_cpa` from unit economics (`--aov`, `--margin-pct`, `--lead-to-sale-cvr`) or user targets, and labels fallback estimates as `PROVISIONAL_HEURISTIC_FALLBACK` inside `evidence_and_assumptions`.
  - `lookalike` now exposes `heuristic_seed_readiness_score_100` with explicit disclosure (`is_meta_internal_score: False`).
- **Python AST & Dead-Code Scanner (`tools/tyrion-shield.py`)**: Added 6th check verifying zero syntax errors and zero unreachable statements across all Python modules, removed `tests/` from `SKIP_DIRS`, and added `scope_and_limitations` disclosure.

### Fixed & Changed
- **Fixed 3 Concrete Bugs in `tools/meta-audience.py`**:
  1. Removed 16 lines of unreachable dead code after `return` in `query_live_graph_api`.
  2. Added `--no-telegram-bot` / `--has-telegram-bot false` CLI flags in `retargeting`.
  3. Removed artificial `100/500/1000/200` minimum pool floors in `calc_retargeting` when source traffic is `0` (now returns `0` pool size and `INSUFFICIENT_RETARGETING_POOL`).
- **Unified 20% Audience Overlap Threshold**: Standardized `calc_overlap` warning threshold to `20.0%` (`<20%` = `HEALTHY_ISOLATION`, `20%–29.9%` = `MODERATE_OVERLAP`, `>=30%` = `CRITICAL_COLLISION`) matching all documentation, and added explicit distinction between `STATIC_AUDIENCE_POOL_INTERSECTION` and live auction delivery overlap.
- **Upgraded Default Meta Graph API Version to `v26.0`**: Updated `.env.example`, `tools/meta-audience.py`, `tools/capi-utm-builder.py`, and `tools/meta-insights-sync.py` to default to `v26.0` and dynamically interpolate `META_GRAPH_API_VERSION`.
- **Single-Source Version & Inventory Parity (`v5.0.0`)**: Synchronized all version strings (`v5.0.0`) and inventory counts (`36` agents, `62` skills, `100` wiki notes, `18` commands, `9` playbooks, `6` contexts, `29` tools) across all manifests, docs, and scripts.

## [4.0.0] - 2026-10-18 — Single-Root ECC Architectural Overhaul

### Added
- **Unified Master CLI (`tools/tyrion.py`)**: Single entrypoint routing across `status`, `doctor`, `shield`, `audience`, `creative`, `client`, `calc`, `guard`, `search`, `skills`, `instincts`, `catalog`, `graph`, and `audit`.
- **Meta Ads Audience Studio (`tools/meta-audience.py`)**: Added deterministic engines (`retargeting`, `lookalike`, and `diagnose`) alongside `architect`, `interests`, `overlap`, and `saturation`.
- **Andromeda 2 Creative Matrix & Hook Studio (`tools/creative-matrix.py`)**: Deterministic 3x3 Angle x Format matrix builder (`matrix`), 3-language Hook generator (`hooks`), and creative fatigue radar (`fatigue`).
- **Client Workspace Scaffolder (`tools/client-workspace.py` & `/mijoz`)**: Instant 1-command client workspace generator.
