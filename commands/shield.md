---
description: TyrionShield xavfsizlik skaneri — sirlar (.env/tokenlar), hooklar, MCP, 36 agent va 62 skill himoyasini tekshirish
argument-hint: [scan | --json]
---

# /shield — TyrionShield Xavfsizlik Auditi

Vazifa: **$ARGUMENTS**

## Ishga tushirish

```powershell
py -3 tools/tyrion-shield.py scan
```

## Tekshiriladigan 5 qatlam

1. **Secrets & `.env` Exposure:** Butun ombor va `claude-ads-main/` ichida API kalitlar (`EAA...`, `sk-...`, Telegram bot tokenlari va `.env` fayllari) sizib chiqmaganini tekshiradi.
2. **Hooks & MCP Safety:** `hooks.json`, `.claude/settings.json` va `.mcp.json` fayllarida xavfli tarmoq chaqiruvlari yoki qotirilgan lokal yo'llar yo'qligini tekshiradi.
3. **Agent Charter Defense (35):** Barcha 36 agentda [[70-charter-baseline]] (Prompt Defense Baseline, `untrusted data` qalqoni va `skills:` ulanishi) mavjudligini tekshiradi.
4. **Skill Surface Safety (59):** Barcha skilllarda YAML frontmatter to'g'riligi va ikki tomonlama agent ulanishini tekshiradi.
5. **Spend-Guard & Mutation Gates:** [[40-xavfsizlik-va-hisob]] va `tools/spend-guard.py` 6 ta darvozasi faolligini tasdiqlaydi.
