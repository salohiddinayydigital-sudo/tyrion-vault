---
name: sop-landing-matni
description: "SOP: landing page matnini noldan yozish — 9 kirish savoli, 10 qadam, chiqish artefakti va muvaffaqiyat mezonlari"
tags: [sop, matn, landing, kopirayter]
source: "claude-ads-main/local/raw/claudes-bilim/kopirayter/PLAYBOOKS.md (PB-1)"
updated: 2026-09-20
---

# SOP — Landing page matni (noldan)

> Bog'lanishlar: [[kopirayter-frameworklar]] · [[zaifdan-kuchli-matn]] · [[etiroz-javob-patternlari]] · [[ozbek-sotuv-matni-standarti]]

**Qachon:** yangi xizmat/mahsulot uchun landing kerak (sayt yo'q yoki qayta qurilyapti).

## Kirish ma'lumotlari — yo'q bo'lsa SO'RALADI (taxmin qilinmaydi)

1. Mahsulot/xizmat aniq nima? Nima kiradi?
2. Kim uchun? (yosh, shahar, biznes turi, lavozim)
3. Narx yoki narx oralig'i
4. Trafik qayerdan? (Instagram reklama / Google / Telegram kanal / og'zaki)
5. Mijoz kelgunicha muammoni bilarmidi?
6. Bor isbot: sharh, keys, portfolio, mijoz soni, sertifikat
7. Raqib kim va u nima deyapti?
8. Qaysi til? (o'zbek / rus / ingliz)
9. Asosiy konversiya harakati nima?

## Qadamlar

1. **Mijoz tilini yig'** — sharhlar, Telegram yozishmalari, savol-javoblar. Muammo bloki shu so'zlar bilan yoziladi, o'ylab topilmaydi.
2. **Xususiyat → Foyda → Natija jadvalini to'ldir** — kamida 6 qator. Bu matnning skeleti ([[zaifdan-kuchli-matn]]).
3. **10 ta sarlavha yoz** (har xil formulalardan) → 3 savolli sinov → eng yaxshi 3 tasi qoladi.
4. **9 blokni to'ldir:** Hero → Ijtimoiy dalil → Muammo → Yechim → Foyda → Isbot → Offer → E'tirozlar/FAQ → Yakuniy CTA.
   Har blokdan so'ra: "5 qarshilikdan qaysi biriga javob beryapti?" Javob bo'lmasa — blok o'chiriladi.
5. **E'tirozlarni joylashtir** — narx e'tirozi narx yonida, ishonch e'tirozi CTA yonida (FAQ'ga hammasi tashlanmaydi).
6. **CTA'lar** — bitta asosiy matn hamma joyda takrorlanadi + mikro-matn. Har 1.5-2 ekranda bitta CTA.
7. **O'zbek tili filtridan o'tkaz** — kalka, rasmiyatchilik, uzun jumla, bo'sh sifat.
8. **Checklist bo'yicha tekshir** ([[topshirish-cheklist-matn]]).

## Chiqish artefakti

```markdown
# {Loyiha} — landing matni
## Meta (til, auditoriya, trafik manbai, CTA)
## Sarlavha variantlari (A/B/C — sabab bilan, tavsiya belgilangan)
## Blok 1 — Hero (H1 / Sub / CTA / mikro-matn)
## Blok 2..9 (matn + 1 qator izoh)
## Xususiyat → Foyda → Natija jadvali
## Test rejasi (nima birinchi test, qaysi 2 variant)
```

## Muvaffaqiyat mezoni

- Har blok 5 qarshilikdan biriga javob beradi
- **0 ta bo'sh sifat** (audit jadvali bo'yicha tekshirildi)
- Kamida **3 ta aniq raqam**
- Sarlavha raqibning saytiga qo'yilsa to'g'ri kelmaydi
- Web-dasturchi qo'shimcha savol bermasdan sahifani qura oladi

## Manba

- `claude-ads-main/local/raw/claudes-bilim/kopirayter/PLAYBOOKS.md` PB-1
