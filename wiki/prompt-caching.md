---
name: prompt-caching
description: Prompt caching mexanizmi — 10x arzon cache read, TTL (1 soat / 5 daqiqa), cache breakers
tags: [token, mexanizm, narx]
source: raw/2026-09-03-token-gigiyena-va-meta-mashinasi.md (§ Prompt Caching)
updated: 2026-09-03
---

# Prompt caching

Claude har so'rovda suhbat tarixini qayta o'qiydi — lekin keshdagi tokenlarni o'qish ancha arzon.

## Narx va muddat

- **Cache read = 10x arzon** (keshdagi token yangi kiritilgan token narxining ~1/10)
- **TTL — Claude Code terminali:** 1 soat. Uzun tanaffus → kesh butunlay o'chadi (uncached), tarix to'liq narxda qayta o'qiladi
- **TTL — API va sub-agentlar:** 5 daqiqa (standart)

## Cache breakers (keshni nollaydi)

- `/model` almashtirish — har modelning o'z alohida keshi bor
- `model opus plan` — reja ↔ bajarish o'rtasida model almashishi keshni o'chiradi

## Amaliy natija

1 soatdan ortiq tanaffus qilmaslik, sessiya o'rtasida model almashtirmaslik → muntazam [[session-handoff]] protsedurasini qo'llash. Qolgan xaklar: [[token-gigiyenasi]]. Sub-agentlar alohida (qisqa) keshga ega: [[sub-agentlar]]
