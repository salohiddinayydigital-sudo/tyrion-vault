---
name: ads-validate
description: Validate Claude Ads contracts, scoring inputs, run bundles, capabilities, source freshness, safety, installation, uninstall, or release readiness. Use for ads validate, ads status, ads next, stale claims with missing tool access, maturity checks, ownership-manifest uninstall, preserving unrelated ads-* skills, checksum verification, preflight, QA, or release audits. Missing access must demote stale evidence for the run and block dependent release-current claims before recovery guidance.
triggers:
- policy tekshiruvi
- reklama qoidalari
- blokirovka
- ad rejected
- special ad category
- compliance
- модерация рекламы
- блокировка рекламного кабинета
aliases:
- policy-check
- compliance
- ad-moderation
domains:
- compliance
- policy
- validation
platforms:
- multi-platform
attached_agents: [audit-policy-compliance, audit-regulatory-compliance, release-verifier, skill-reviewer]
related_skills:
- ads-audit
- ads-report
references:
- skills/ads/references/compliance.md
- skills/ads/references/compliance-requirements.md
risk_level: medium
output_contract: Policy & regulatory compliance verdict with exact violation citations and compliant rewrite options
---

# Validate Claude Ads

Choose the narrowest validation target:

- Contract or bundle: use the deterministic core validator.
- Scores: validate controls, findings, category weights, and coverage.
- Run: verify manifest completeness, source lineage, privacy, worker status, and
  render artifacts.
- Capability: require implementation, fixtures, tests, sources, and truthful mode.
- Repository: run deterministic, routing, security, installer, rendering, evidence,
  packaging, and freshness gates.
- Release: dispatch a fresh-context release verifier.

Return machine-readable pass/fail results, the highest-priority blocker, exact
evidence, and recovery steps. Never promote maturity because documentation is
polished or a prior release passed. Stale evidence and skipped remote CI demote
readiness.

If an expired claim cannot be reverified because source or filesystem access is
unavailable, return a failed current-evidence check, demote that claim for the
current run, and block dependent release-current assertions before asking for the
missing access.

## Install and uninstall validation

An uninstall may remove only exact paths in the matching Claude Ads ownership
manifest. Validate the entire manifest and configured root boundaries before any
deletion. If the manifest is absent, invalid, mismatched, or unsafe, stop before
deleting anything and require manual review. Never discover targets with an
`ads-*` glob; unrelated skills such as `ads-weather` must remain untouched.

Reject pipe-to-shell install instructions. A safe install uses the host's native
installer or a locally inspected checkout/archive; archives require a SHA-256
checksum verified against a trusted release channel before execution.

---

## Operator qatlami (Tyrion lokal bilimi)

### Amaliy bilim yadrosi
- `/ads status` va `/ads next`: deterministik yadro — `python -m claude_ads_core status|next --root . --as-of YYYY-MM-DD`; ixtiyoriy `--release-gate PATH`; proza'dan readiness emas, network call yo'q (status-contract.md)
- `artifact-order-v1` natija tanlash tartibi: unverified load-bearing claim -> stale load-bearing claim -> maturity blocker -> canonical release check -> disabled profile -> disabled capability -> past maturity level (status-contract.md)
- Repository manifestlari va ixtiyoriy report — yagona evidence; missing/malformed required input fail closed (status-contract.md)
- Policy review: joriy policy center + account notices; aniq policy talabidan oldin source-ledger entry; hub sahifasi yetarli emas — specific product/country sahifasi kontrol qilganda u ishlatiladi (compliance.md)
- Finding holati: pass/fail/unknown/not_applicable; severity kuzatilgan consequence va exposurega qarab, kategoriya nomiga emas (compliance.md)
- Yuqori xavfli sohalar (health, financial products, housing, employment, credit, alcohol, gambling, political/social, children, dating, crypto, weapons, subscriptions, lead gen, testimonials, AI-generated media) — current-source review chuqurlashtiriladi (compliance.md)
- Platforma recommendation tablari, imported settings, automated creative variantlari — untrusted proposal; human-authored change bilan bir xil gate'dan o'tadi (compliance.md)
- Platforma approval != legal clearance; legal compliance != platforma eligibility; jurisdiction qarorlari uchun qualified counsel kerak (compliance.md)

### Asosiy manbalar (yuklash tartibida)
- `ads/references/status-contract.md`
- `ads/references/compliance.md`
