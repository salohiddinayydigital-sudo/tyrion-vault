---
name: detailed-targeting-accuracy
description: "Tyrion v5.0 Detailed Targeting Accuracy Engine — Architecture, official Meta Marketing API v26.0 endpoints, 6 verification statuses, caching, and testing guide"
tags: [meta-ads, targeting, api, accuracy, validation]
source: "tools/meta-targeting-engine.py + Meta Marketing API v26.0"
updated: 2026-10-20
---

# 🎯 Tyrion v5.0 — Detailed Targeting Accuracy Engine (`tools/meta-targeting-engine.py`)

## 1. Overview & Core Design Principle

When planning Meta Ads campaigns, AI systems frequently hallucinate plausible-sounding interest or behavior names derived from a product description that **do not exist** in Meta Ads Manager, or that Meta has deprecated or consolidated.

Tyrion's **Detailed Targeting Accuracy Engine** (`tools/meta-targeting-engine.py`, integrated into `tools/meta-audience.py`, `tools/tyrion-mcp-server.py`, and `tools/tyrion.py`) enforces a strict boundary between **official Meta API evidence** and **unverified AI/heuristic search ideas**:

- **Zero Hallucinated Interests:** AI-expanded synonyms (across Uzbek Latin, Uzbek Cyrillic, Russian, and English), static niche dictionaries (`NICHE_TAXONOMY`), and purchasing-power (*Solventnost*) ideas are treated strictly as **search queries** or **unverified hypotheses (`RELATED_UNVERIFIED`)** — never as confirmed Meta targeting options.
- **Exact Name & ID Preservation:** Official API results retain the exact `name` and `id` returned by Meta without machine translation or alteration.
- **ID + Type Deduplication:** Results are deduplicated strictly by `(id, type.lower())` rather than by `name`, preserving distinct Meta targeting entities that share similar or identical display names.
- **No Fabricated Reach Bounds:** `audience_size_lower_bound` and `audience_size_upper_bound` are populated **only** when explicitly returned by Meta's API (`None` otherwise).

## 2. Official Meta Marketing API Endpoints Used

The engine uses the configured `META_GRAPH_API_VERSION` (default `v26.0` from `.env` / environment) and supports four official read-only endpoints documented in the [Meta Marketing API Reference](https://developers.facebook.com/documentation/ads-commerce/marketing-api/audiences/reference/detailed-targeting):

| Endpoint | HTTP Path | Purpose & Scope | Required Parameters & Permissions |
|---|---|---|---|
| **Global Targeting Search** | `GET /{api-version}/search?type=adinterest` | Searches global ad interest catalog when no `ad_account_id` (`act_...`) is supplied ([Targeting Search Reference](https://developers.facebook.com/documentation/ads-commerce/marketing-api/audiences/reference/targeting-search)). | `q`, `type=adinterest`, `limit`, `locale`. Requires valid `META_ACCESS_TOKEN`. |
| **Account Targeting Search** | `GET /{api-version}/act_{ad_account_id}/targetingsearch` | Searches account-scoped detailed targeting options (interests, behaviors, demographics) returning `audience_size_lower_bound` and `audience_size_upper_bound` ([Ad Account Targetingsearch](https://developers.facebook.com/documentation/ads-commerce/marketing-api/reference/ad-account/targetingsearch)). | `q`, `limit`, `locale`. Requires `ads_read` or `ads_management` on `act_{ad_account_id}`. |
| **Targeting Suggestions** | `GET /{api-version}/act_{ad_account_id}/targetingsuggestions` | Returns Meta-recommended adjacent targeting options based on seed targeting IDs ([Ad Account Targetingsuggestions](https://developers.facebook.com/documentation/ads-commerce/marketing-api/reference/ad-account/targetingsuggestions)). | `targeting_list` (JSON array of `{"id", "type"}`), `limit`. Optional (`--suggestions`). |
| **Targeting Validation** | `GET /{api-version}/act_{ad_account_id}/targetingvalidation` | Validates whether specific targeting IDs are currently active and deliverable for the ad account, flagging deprecated or consolidated interests ([Ad Account Targetingvalidation](https://developers.facebook.com/documentation/ads-commerce/marketing-api/reference/ad-account/targetingvalidation)). | `targeting_list` (JSON array). Requires `ads_read` on `act_{ad_account_id}`. |

## 3. Meaning of the 6 Verification Statuses (`validation_status`)

Every targeting item or query in the output report carries exactly one of the following six statuses:

1. **`VERIFIED_AVAILABLE`**: Found in an official Meta Graph API search endpoint (`/search`, `targetingsearch`, or `targetingsuggestions`) **and** confirmed `valid: true` by `/{ad-account-id}/targetingvalidation`.
2. **`FOUND_NOT_VALIDATED`**: Found in an official Meta Graph API search endpoint (`id` and `name` are real), but account-level `/{ad-account-id}/targetingvalidation` has not been executed (for example, when `--account-id` was not provided or `--no-validate` was set).
3. **`UNAVAILABLE_OR_CONSOLIDATED`**: Official Meta API response (`targetingvalidation` or deprecation metadata) indicates the option is invalid (`valid: false`), deprecated, or consolidated into another option. When Meta provides replacement metadata, `validation_details.consolidated_into` links the old option to the new `{id, name, type}`.
4. **`RELATED_UNVERIFIED`**: A semantic suggestion, multilingual synonym, static `NICHE_TAXONOMY` seed, or `SOLVENTNOST_HYPOTHESES` item that has **not** been confirmed in Meta's official API. Always carries `is_verified_meta_option: False`.
5. **`NOT_FOUND`**: The search query was executed against the live Meta Graph API and returned `0` matching items. *Important:* `NOT_FOUND` means no result was returned for the executed query string; it is not an absolute proof that no related concept exists in Meta under a different taxonomy name.
6. **`API_UNAVAILABLE`**: Live Graph API verification could not be completed due to a missing `META_ACCESS_TOKEN`, HTTP `401` (unauthorized), HTTP `403` (insufficient permissions), HTTP `400` (bad request), HTTP `429` (rate limit exhausted after backoff), HTTP `5xx` (server error), network timeout, or malformed JSON. **When `API_UNAVAILABLE`, no static or AI-suggested option is ever marked `VERIFIED_AVAILABLE` or `FOUND_NOT_VALIDATED`.**

## 4. Search Result vs. Account Deliverability & Relevance Score

- **Search Result (`FOUND_NOT_VALIDATED`) vs. Deliverable Option (`VERIFIED_AVAILABLE`):** An interest appearing in global `/search?type=adinterest` may still be restricted in a specific ad account, region, or Special Ad Category (`HOUSING`, `EMPLOYMENT`, `CREDIT`, `ISSUES_ELECTIONS_POLITICS`). Always supply `--account-id act_...` to run `targetingvalidation` before launching campaigns.
- **`relevance_reason` Is AI Opinion, Not Meta Proof:** Every discovered option includes `relevance_reason` alongside `"relevance_is_ai_opinion_not_meta_proof": True`. Semantic relevance never substitutes for `validation_status`.
- **Purchasing-Power (*Solventnost*) Hypotheses:** Signals such as `Engaged Shoppers`, `Frequent International Travelers`, `Facebook Page Admins`, or flagship device models are labeled as `MARKETING_HYPOTHESIS` (`RELATED_UNVERIFIED` until verified via API), never as guaranteed income filters.

## 5. Fallback & Caching Behavior

- **Safe Offline Fallback:** When `META_ACCESS_TOKEN` is absent or the API fails, `live_check_status.status` is set to `API_UNAVAILABLE`, `verified_targeting_options` is empty (`[]`), `recommended_audience_combinations.status` is set to `NO_VERIFIED_OPTIONS_AVAILABLE`, and candidate search seeds are listed separately under `related_unverified_ideas`.
- **TTL Cache Provenance:** When `--cache-file <path>` is used, each entry stores `api_version`, `fetched_at_utc`, `fetched_epoch`, `ttl_seconds`, and `query_params`. If the cached entry's `api_version` differs from the current `META_GRAPH_API_VERSION` or its age exceeds `ttl_seconds`, the cache is rejected and never served as current verification.

## 6. CLI & MCP Usage

```bash
# 1. Search & validate with an Ad Account ID (runs targetingsearch + targetingvalidation)
python3 tools/meta-targeting-engine.py search \
  --product "Klassik erkaklar kostyumi" \
  --niche ecom \
  --customer-profile "Toshkentdagi 25-45 yoshli tadbirkorlar" \
  --account-id act_123456789 \
  --suggestions --json

# 2. Via meta-audience.py or Master CLI
python3 tools/meta-audience.py detailed-targeting --product "Стоматология имплантация" --niche medical --language ru --json
python3 tools/tyrion.py targeting search --product "Ko'chmas mulk novostroyka" --niche real-estate --special-ad-category HOUSING
```

## 7. Running Automated Tests

```bash
# Run the full offline unit & local-HTTP test suite (136+ tests, 0 live Meta account dependency)
python3 -m unittest discover tests -v

# Optional live integration smoke test (runs only when META_ACCESS_TOKEN and TYRION_RUN_LIVE_META_SMOKE=1 are set)
TYRION_RUN_LIVE_META_SMOKE=1 python3 -m unittest tests/test_tyrion_tools.py -k LiveMetaSmoke -v
```

## 8. Known Limitations

- **Live Account Validation Requires `ads_read`:** Without a live `META_ACCESS_TOKEN` and `act_<AD_ACCOUNT_ID>` granted `ads_read` permission, `/{ad-account-id}/targetingsearch`, `targetingsuggestions`, and `targetingvalidation` cannot be verified against a real Meta ad account; unit tests verify the protocol and edge cases against a local `ThreadingHTTPServer`.
- **Regional Reach Bounds:** `audience_size_lower_bound` and `audience_size_upper_bound` returned by `targetingsearch` reflect global or default locale bounds unless scoped via `reachestimate` / `delivery_estimate` with full geo-targeting specs.

**Related:** [[meta-ads-interest-api]] · [[meta-auditoriya-arxitekturasi]] · [[40-xavfsizlik-va-hisob]] · [[00-manba]]
