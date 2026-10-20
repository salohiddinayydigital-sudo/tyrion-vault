---
description: Konversiya va telemetriya auditi — CAPI, Pixel EMQ, GTM va Telegram bot webhooklari
argument-hint: <mijoz>
---

# /tracking — Konversiya va telemetriya auditi

Vazifa: **$ARGUMENTS**

## Ijro tartibi:
1. **Meta Ads (`audit-tracking`):**
   - Brauzer Pixel vs Server CAPI event deduplikatsiyasi (`event_id` tekshiruvi)
   - Event Match Quality (EMQ) ballari (maqsad: $\ge 7.0$)
2. **Google Ads:**
   - Enhanced Conversions holati
   - 3 yo'nalishli konversiya: Rahmat sahifasi (URL contains), Saytdan qo'ng'iroq, Call asset
3. **Telegram Ads:**
   - Deep link parametrlari: `?start=utm_source_campaign_angle`
   - Botdan CRM'ga (AmoCRM, Bitrix24) webhooklar holati
4. **UTM arxitekturasi:**
   - Standart: `utm_source`, `utm_medium`, `utm_campaign`, `utm_content`

## Natija:
- Telemetriya kartasi va nosozliklarni tuzatish bo'yicha texnik yo'riqnoma
