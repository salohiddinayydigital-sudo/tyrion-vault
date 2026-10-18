---
name: token-gigiyenasi
description: Token va kontekst gigiyenasi — 18 amaliy xak (sessiya, MCP, batching, plan, /context, handoff)
tags: [token, kontekst, gigiyena]
source: raw/2026-09-03-token-gigiyena-va-meta-mashinasi.md (§ Token va kontekst gigiyenasi)
updated: 2026-09-03
---

# Token va kontekst gigiyenasi

**Muammo:** har yangi so'rovda butun suhbat tarixi boshidan qayta o'qiladi → xarajat oshadi, javob sifati pasayadi (*loss in the middle*). Mashtab: 30-xabarga borganda bitta so'rov 15,000+ tokenga yetishi mumkin.

## Amaliy xaklar

1. **Yangi mavzu → yangi sessiya:** vazifa tugagach `/clear` bering
2. **MCP gigiyenasi:** har ulangan MCP server har so'rovda ~17 000–18 000 token egallaydi — keraksizlarini uzing, og'ir MCP o'rniga CLI vositalari
3. **Batching:** 3 ta alohida xabar → bitta xabarga jamlang
4. **Xato → tahrirlash:** yangi tuzatish yozishdan ko'ra eski xabarni tahrirlab qayta generatsiya qiling
5. **Plan Mode:** jiddiy topshiriqdan oldin — 1 daqiqalik reja noto'g'ri kod uchun ketadigan tokenlardan asraydi
6. **60% qoidasi:** kontekst 60% ga yetganda tozalang (`/context` bilan kuzating); avto-ixchamlashtirish 95% da ishga tushadi — bu vaqtda sifat allaqachon buzilgan
7. **/compact o'rniga Session Handoff** (pastga qarang)

**Mexanizm:** [[prompt-caching]] · **Kontekst to'lganda:** [[session-handoff]] · **Kontekstni himoyalash:** [[sub-agentlar]]
