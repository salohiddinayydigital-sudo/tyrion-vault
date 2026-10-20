---
name: mcp-va-multi-harness-integratsiya
description: "Tyrion v5.0 Native MCP Server (.mcp.json) va Multi-Harness Exporter (Claude Code, Cursor .mdc, Windsurf, Codex) arxitekturasi"
tags: [mcp, arxitektura, cursor, claude-code, ecc]
source: "affaan-m/ECC install-targets + pipeboard-co/meta-ads-mcp + googleads/google-ads-mcp (2026-10-18)"
updated: 2026-10-18
---

# 🔌 MCP SERVER VA MULTI-HARNESS INTEGRATSIYASI

## 1. Ichki STDIO MCP Server (`tools/tyrion-mcp-server.py`)
Tyrion v5.0 hech qanday tashqi kutubxonasiz (`stdlib` Python JSON-RPC 2.0) ishlaydigan shaxsiy **Model Context Protocol (MCP)** serveriga ega (`.mcp.json` ichida `tyrion-core` sifatida faol). U 7 ta asosiy dvigatelni AI agentlarga to'g'ridan-to'g'ri tool sifatida ochib beradi:
- `tyrion_meta_audience` — 4-qatlamli Meta Ads auditoriya va Exclusion matritsasi.
- `tyrion_breakdown_effect` — Marginal vs Average CPA tuzog'i tekshiruvi.
- `tyrion_creative_matrix` — 3x3 Andromeda kreativ matritsa va 3 tilli Hooklar.
- `tyrion_capi_utm` — Meta CAPI v22 SHA-256 payload, EMQ va Telegram Bot `<=64` belgi UTM.
- `tyrion_media_calculator` — Break-even CPA/ROAS va marja hisoblagichi.
- `tyrion_spend_guard` — 20% byudjet xavfsizlik darvozasi.
- `tyrion_brain_search` — 100 ta atomik qayd va 8 ta playbook bo'yicha 0-token qidiruv.

## 2. Tashqi Platforma MCP Serverlari (`.mcp.json`)
- **Meta Ads MCP (`pipeboard-co/meta-ads-mcp`):** `META_ACCESS_TOKEN` o'rnatilgach, jonli kampaniya va ad set o'qish uchun yoqiladi.
- **Google Ads MCP (`googleads/google-ads-mcp`):** Rasmiy Google Ads read-only GAQL serveri.

## 3. Multi-Harness Eksport (`tools/harness-export.py`)
`affaan-m/ECC` singari, Tyrion qoidalarini dublikat saqlamasdan istalgan AI muhitiga moslashtiradi:
```bash
python3 tools/harness-export.py --target cursor    # .cursor/rules/*.mdc
python3 tools/harness-export.py --target windsurf  # .windsurfrules
python3 tools/harness-export.py --target claude    # .claude/commands/*.md
```

**Bog'liq:** [[agent-os-qatlami]] · [[skill-router]] · [[token-gigiyenasi]] · [[uzluksiz-organish-instinktlar]]
