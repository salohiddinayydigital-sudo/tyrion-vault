---
name: sub-agentlar
description: Sub-agentlar infratuzilmasi — .claude/agents/ kichik ixtisoslashgan agentlar (researcher, code-reviewer andozalari)
tags: [token, kontekst, infratuzilma, agentlar]
source: raw/2026-09-03-token-gigiyena-va-meta-mashinasi.md (§ Sub-agentlar infratuzilmasi)
updated: 2026-09-05
---

# Sub-agentlar infratuzilmasi

**Maqsad:** asosiy agentning kontekstini toza saqlash — katta ishni kichik, ixtisoslashgan agentlarga topshirish. Fayl joyi: `.claude/agents/`.

## Andoza 1 — Tadqiqotchi (researcher)

```markdown
---
name: researcher
model: claude-3-5-haiku-latest
tools: [read, glob, grep, web_search]
---
Sening vazifang katta hajmdagi hujjatlar va veb-manbalarni tahlil qilish.
Asosiy agentga butun matnni emas, faqat 150-200 so'zdan oshmaydigan
yuqori axborot zichligidagi xulosani qaytar.
```

## Andoza 2 — Kodni tekshiruvchi (code-reviewer)

```markdown
---
name: code-reviewer
model: claude-3-7-sonnet-latest
tools: [read]
---
Sening vazifang yozilgan kodni hech qanday xolis fikrsiz (zero-context
bilan) xavfsizlik, sintaksis va optimallik bo'yicha tekshirish.
Faqat topilgan kamchiliklar va aniq tuzatishlar ro'yxatini qaytar.
```

## Qoidalar

- Agent kichik model + kam vosita → kontekst byudjeti past, natija shartnomasi qat'iy (qisqa, zich, faqat topilmalar)
- Tejamkorlik mashtabi: 100,000 tokenli katta hujjat → asosiy agentga ~2,000 tokenli xulosa (50x); andozadagi 150–200 so'z cheklovi xulosa zichligini qo'riqlaydi
- Har bir sub-agent TTL 5 daqiqalik **alohida keshga** ega (asosiy sessiyadan mustaqil): [[prompt-caching]]
- Bu andozalar *o'rnatish qo'llanmasi* — `claude-ads-main/` ichida repo-local worker'lar boshqa mexanizm (repo o'z `.claude/agents/` da yashaydi, global o'rnatilmaydi)

Kontekstni asrashning umumiy qoidalari: [[token-gigiyenasi]]

Sub-agentga beriladigan ish situational kontekst sifatida ajratiladi: [[kontekst-ajratish]]. Katta ish sessiyalar oralig'idan o'tsa, natijani [[session-handoff]] orqali ko'chiring.
