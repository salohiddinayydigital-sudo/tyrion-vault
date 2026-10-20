---
description: Mijoz hisoboti — natijalar, qarorlar, keyingi qadam (fayl bo'lib chiqadi)
argument-hint: <mijoz> [davr]
---

# /hisobot — mijoz hisoboti

Vazifa: **$ARGUMENTS**

## Oldindan

1. `journal/<mijoz>.md` — mijoz tarixi, oldingi qarorlar, holat.
2. `outputs/<mijoz>/` — oldingi natijalar (takror yozmaslik uchun).
3. Metrika qoidasi: blended ROAS + net free cash flow, break-even hisobidan
   ([[blended-roas-net-cash]]) — ROAS foizi yakuniy haqiqat emas.

## Hisobot tuzilishi

| Bo'lim | Nima |
|--------|------|
| Xulosa | 3 qator: holat, asosiy raqam, qaror |
| Raqamlar | davr · spend · natija · CPA/ROAS · o'zgarish (manba ko'rsatilgan) |
| Nima ishladi / ishlamadi | dalil bilan, taxminsiz |
| Qarorlar | kill / keep / scale — sababi bilan |
| Keyingi qadam | 1-3 ta aniq harakat, mas'ul, muddat |
| Cheklovlar | o'lchov yetishmovchiligi (Pixel/CAPI/UTM) ochiq aytiladi |

## Natija

`outputs/<mijoz>/<sana>-hisobot.md` + `journal/<mijoz>.md` ga qarorlar.
Katta hisobotdan oldin `release-verifier` tekshiruvi ([[50-topshirish-dod]]).
