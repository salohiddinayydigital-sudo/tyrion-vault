---
name: utm
description: "Meta/Google dinamik UTM shablonlari, Telegram Bot <=64 belgi deep-link (?start=) va Meta CAPI v26.0 SHA-256 payload + EMQ ballini generatsiya qilish"
---

# `/utm` — Meta CAPI v22 Payload, EMQ va Telegram Bot UTM Generator

Foydalanuvchi `/utm [url yoki bot]` deb chaqirganda:

1. **Dinamik UTM va Telegram Bot Deep-Link (`<=64` belgi chegarasi bilan):**
   ```bash
   python3 tools/capi-utm-builder.py utm --url "<landing_url>" --platform <meta|google|telegram> --campaign "<kampaniya_nomi>" --bot "<telegram_bot_username>"
   ```
2. **Meta Conversions API (CAPI v26.0) SHA-256 Payload va EMQ Balli:**
   ```bash
   python3 tools/capi-utm-builder.py capi-payload --event "Lead" --phone "+998901234567" --email "mijoz@mail.uz" --city "tashkent" --value 150 --order-id "CRM_1001"
   ```
3. **Qoida:** Browser Pixel va Server CAPI bir xil `event_id` yuborishi (`deduplication >= 95%`) va Event Match Quality (`EMQ >= 6.5/10`) bo'lishini tekshiring ([[40-xavfsizlik-va-hisob]]).
