---
description: Bilim grafidan tez javob — eng arzon bilim yo'li (butun vaultni o'qimasdan)
argument-hint: <savol>
---

# /savol — grafdan javob

Foydalanuvchi savoli: **$ARGUMENTS**

## Qadamlar

1. Grafdan so'ra (arzon yo'l — [[20-token-gigiyena]]):
   ```powershell
   python3 tools/brain-search.py query "$ARGUMENTS" --budget 1200
   ```
2. Graf javob bermasa: `INDEX.md` dan mos qatorni topib, **faqat o'sha qayd(lar)ni** o'qi.
3. Javobni ber: o'zbekcha, zich, har fakt yonida manba ([[00-manba]]).
4. Manba topilmasa — "ma'lumot yo'q" deb ayt, to'qima.

## Cheklovlar

- Butun `wiki/` ni yoppasiga o'qima.
- Graf javobini xom fakt deb hisoblama — asl qaydga havola bo'lsa ko'rsat.
- Javob yangi bilim bersa: `wiki/` ga qayd yozishni **taklif qil** (o'zing boshlamay).
