# Changelog

All notable changes to **Tyrion** are documented in this file.

## [4.0.0] - 2026-10-18 — Single-Root ECC Architectural Overhaul

### Added
- **Unified Master CLI (`tools/tyrion.py`)**: Single entrypoint routing across `status`, `doctor`, `shield`, `audience`, `creative`, `client`, `calc`, `guard`, `search`, `skills`, `instincts`, `catalog`, `graph`, and `audit`.
- **Meta Ads Audience Studio v4.0 (`tools/meta-audience.py`)**: Added 3 new deterministic engines (`retargeting` dynamic 3d/7d/14d/30d/180d window builder, `lookalike` Seed Quality Score 0-100 & UZ 1%-5% reach ladder, and `diagnose` metric-chain bottleneck analyzer) alongside `architect`, `interests`, `overlap`, and `saturation`.
- **Andromeda 2 Creative Matrix & Hook Studio (`tools/creative-matrix.py`)**: Deterministic 3x3 Angle x Format matrix builder (`matrix`), 3-language Hook generator (`hooks` in Uzbek Latin, Uzbek Cyrillic, and Russian), and creative fatigue radar (`fatigue`).
- **Client Workspace Scaffolder (`tools/client-workspace.py` & `/mijoz`)**: Instant 1-command client workspace generator producing pre-calculated `BRIEF.md`, `AUDIENCE-MAP.md`, `CREATIVE-MATRIX.md`, `TRACKING-CHECKLIST.md`, and `journal.md`.
- **ECC Dynamic Context Modes (`contexts/`)**: Added 5 task-specific operating modes (`audit-mode.md`, `launch-mode.md`, `scale-mode.md`, `creative-mode.md`, `uzbekistan-market.md`).
- **First-Class Playbooks Library (`playbooks/`)**: Added 8 comprehensive Uzbekistan & Global vertical playbooks (`meta-ads-1k-10k-uz.md`, `nisha-ecommerce-uz.md`, `nisha-talim-kurslar.md`, `nisha-kochmas-mulk.md`, `nisha-tibbiyot-klinika.md`, `nisha-b2b-avtoservis.md`, `nisha-atir-fitness-horeca.md`, `telegram-bot-amocrm-voronka.md`).
- **New Agent & Skill**: Added `agents/meta-audience-architect.md` (36th agent) and `skills/uzbekistan-market-intel/SKILL.md` (62nd skill).
- **4 New Slash Commands (`commands/`)**: Added `/voronka`, `/scale`, `/raqobatchi`, and `/mijoz` (16 total commands).

### Changed & Removed (Radical Simplification)
- **Eliminated Split-Brain `claude-ads-main/` Sub-Repository (`6.9 MB` removed)**: Consolidated all agents (`agents/`), skills (`skills/`, including `skills/ads/` conductor and 39 platform references), operator memory (`MEMORY.md`), and local Uzbekistan wiki notes (`wiki/`, now 98 notes) directly into the canonical root.
- **Removed Legacy Clutter**: Deleted `vedio bilimlar/`, `HERMES.md`, `raw/`, `audits/`, `archive/`, and `COMMANDS-QUICK-REF.md`.
