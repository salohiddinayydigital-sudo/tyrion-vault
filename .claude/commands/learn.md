---
description: Uzluksiz o'rganish — sessiya yoki kampaniyadan tasdiqlangan instinkt (qoida/saboq) ajratib olish va xotiraga muhrlash
argument-hint: [list | add | promote <id>]
---

# /learn — Uzluksiz O'rganish va Instinktlar (ECC Continuous Learning)

Vazifa: **$ARGUMENTS**

## Nima qiladi

Kampaniya auditi, A/B sinov, kreativ sprint yoki texnik nosozlikdan olingan tasdiqlangan saboqni **atomik instinkt** sifatida `manifests/instincts.json` reestriga yozadi va ishonch balli ($\ge 4/5$) yetganda `MEMORY.md` §6 yoki `wiki/` ga ko'taradi ([[uzluksiz-organish-instinktlar]]).

## Buyruqlar

```powershell
# Mavjud instinktlarni ko'rish
py -3 tools/instincts.py list

# Yangi instinkt qo'shish (confidence 1..5)
py -3 tools/instincts.py add --id <slug> --domain <meta|google|telegram|kreativ|tracking|tizim> --trigger "<qachon>" --action "<nima qilinadi>" --evidence "<manba>" --confidence 4

# Yuqori ishonchli (>=4) instinktni memory.md §6 ga ko'tarish
py -3 tools/instincts.py promote <id>
```

## Qoidalar

1. **Manbasiz instinkt yozilmaydi** — har bir instinktda `evidence` (akkaunt eksporti, test natijasi yoki wiki qayd) bo'lishi shart ([[00-manba]]).
2. **Tasodifiy tebranish qoida emas** — kamida statistik ahamiyatli namuna bo'lgandagina `confidence >= 4` beriladi.
