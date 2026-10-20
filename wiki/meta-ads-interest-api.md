---
name: meta-ads-interest-api
description: "Meta/Facebook Ads Graph API v26.0 Detailed Targeting Accuracy Engine (`/search`, `targetingsearch`, `targetingsuggestions`, `targetingvalidation`) va 6-statusli aniqlik tizimi"
tags: [meta-ads, api, interests, auditoriya, targeting, validation]
source: "tools/meta-targeting-engine.py + tools/meta-audience.py + Meta Marketing API v26.0 (2026-10-20)"
updated: 2026-10-20
---

# 📘 Meta Ads Detailed Targeting Accuracy Engine & API (`v26.0`)

> **⚠️ Qat'iy Aniqlik va Xavfsizlik Qoidasi ([[40-xavfsizlik-va-hisob]] · [[00-manba]]):**
> * **Hech qachon AI taxmini yoki statik ro'yxatni Meta'dagi real targeting opsiyasi sifatida ko'rsatmang!**
> * Har bir variant rasmiy API dalili va 6 ta aniqlik holatidan (`VERIFIED_AVAILABLE`, `FOUND_NOT_VALIDATED`, `UNAVAILABLE_OR_CONSOLIDATED`, `RELATED_UNVERIFIED`, `NOT_FOUND`, `API_UNAVAILABLE`) biri bilan tamg'alanishi shart.
> * Reklama kampaniyalarini o'chirish, yoqish yoki byudjetni o'zgartirish **QAT'IYAN TAQIQLANADI** (faqat read-only qidiruv va tekshiruv).

## 🔑 1. Rasmiy Meta Marketing API Endpointlari (`v26.0`)

| Endpoint | Yo'l (`META_GRAPH_API_VERSION=v26.0`) | Vazifasi |
|---|---|---|
| **Global Search** | `GET /v26.0/search?type=adinterest&q=<query>` | Reklama akkaunt ID si bo'lmaganda global qiziqishlar qidiruvi (`FOUND_NOT_VALIDATED`). |
| **Account Targeting Search** | `GET /v26.0/act_<id>/targetingsearch?q=<query>` | Akkaunt doirasida interest, behavior va demografiya qidiruvi (`audience_size_lower_bound` / `upper_bound` bilan). |
| **Targeting Suggestions** | `GET /v26.0/act_<id>/targetingsuggestions?targeting_list=<json>` | Topilgan rasmiy ID'lar asosida Meta tavsiya qilgan o'xshash targeting variantlari. |
| **Targeting Validation** | `GET /v26.0/act_<id>/targetingvalidation?targeting_list=<json>` | Variantning ayni vaqtda yaroqli (`VERIFIED_AVAILABLE`) yoki eskirgan/birlashtirilgan (`UNAVAILABLE_OR_CONSOLIDATED`) ekanini tekshiradi. |

## 🏷️ 2. 6 ta Aniqlik Holati (`validation_status`)

- **`VERIFIED_AVAILABLE`**: Rasmiy API dan topilgan va `targetingvalidation` da `valid: true` bilan tasdiqlangan.
- **`FOUND_NOT_VALIDATED`**: Rasmiy API dan topilgan (original `name` va `id` mavjud), ammo `targetingvalidation` bajarilmagan.
- **`UNAVAILABLE_OR_CONSOLIDATED`**: Rasmiy API variantning eskirgani yoki boshqa variantga birlashtirilganini bildirgan (`consolidated_into` orqali yangi variantga bog'lanadi).
- **`RELATED_UNVERIFIED`**: Statik `NICHE_TAXONOMY` urug'lari, ko'p tilli sinonimlar yoki `SOLVENTNOST_HYPOTHESES` — Meta API da tasdiqlanmagan!
- **`NOT_FOUND`**: Bajarilgan qidiruv so'rovi bo'yicha rasmiy API dan `0` ta natija qaytdi (bu tushuncha Meta'da umuman yo'qligining mutlaq isboti emas, faqat shu so'rovda topilmadi).
- **`API_UNAVAILABLE`**: Token yo'q, `401/403` ruxsat xatosi, `429` limit yoki tarmoq uzilishi. Bu holatda hech bir statik nom `VERIFIED_AVAILABLE` deb ko'rsatilmaydi.

## 💎 3. O'zbekiston To'lov Qobiliyati (Solventnost) Gipotezalari (`MARKETING_HYPOTHESIS`)

Quyidagi signallar **tasdiqlangan daromad filtri emas**, balki kampaniyada A/B sinov orqali tekshiriladigan marketing gipotezalaridir ([[30-ozbekiston-konteksti]]):
1. **`Engaged Shoppers`** — onlayn xarid tugmasini bosganlar faolligi gipotezasi.
2. **`Frequent International Travelers`** — chet elga safar qiluvchilar gipotezasi.
3. **`Mobile Device: Flagship / iPhone Pro Series`** — qurilma modeli gipotezasi (nasiyaga olingan bo'lishi mumkin).
4. **`Facebook Page Admins` / `Small Business Owners`** — B2B qaror qabul qiluvchilar gipotezasi.

## 💻 4. CLI va MCP Ishlatish

```bash
# 1. To'liq 6-statusli Detailed Targeting qidiruvi va tekshiruvi
python3 tools/meta-targeting-engine.py search --product "Klassik erkaklar kostyumi" --niche ecom --account-id act_123456789 --suggestions

# 2. Ko'p tilli (O'zbek lotin, Kirill, Rus, Ingliz) so'rovlar bilan
python3 tools/meta-audience.py detailed-targeting --product "Стоматология Ташкент" --niche medical --language ru --json
```

**Bog'liq:** [[meta-auditoriya-arxitekturasi]] · [[meta-ads-sozlamalari]] · [[meta-kampaniya-tuzilmalari]] · [[content-is-targeting]]
