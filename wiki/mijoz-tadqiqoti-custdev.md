---
name: mijoz-tadqiqoti-custdev
description: "CustDev — mijoz intervyusi: kim bilan, nechta, savol bloklari (xarid odati, tanlov sababi, ishonch, qiyinchilik), ballash va topilmalarni rejaга aylantirish"
tags: [tadqiqot, mijoz, custdev, bozor]
source: "claude-ads-main/local/raw/kanal-bilim/26_Custdev.txt (haqiqiy CustDev savolnomasi + natijalar) + sop-raqobat-tahlili"
updated: 2026-09-20
---

# Mijoz tadqiqoti (CustDev)

> Bog'lanishlar: [[bozor-analizi-tizimi]] · [[cjm-mijoz-yoli]] · [[etiroz-javob-patternlari]] · [[sop-pozitsiyalash-offer-qurish]] · [[survey-funnel]]

CustDev — **taxminni faktga** aylantiradi. Bozor analizining eng qimmatli qismi: raqobatchi sharhlari tashqi, mijoz intervyusi esa ichki haqiqat.

## Qoidalar

- **5-7 mijoz** (ko'proq — yangi pattern chiqmaydi)
- Haqiqiy xaridor bilan: oxirgi 30-90 kunda sotib olgan
- **So'raladi, o'rgatilmaydi:** javobni oldindan aytib berma
- Yozib olinadi (ruxsat bilan); iqtiboslar **so'zma-so'z** saqlanadi

## Savol bloklari

| Blok | Savol (mohiyati) |
|---|---|
| **1. Xarid odati** | Qaysi magazinlarni tez-tez ishlatasiz va **nega**? Katta taniqli yoki kichik ixtisoslashgan? Nega? |
| **2. Oxirgi xaridlar** | Oxirgi **3 ta muvaffaqiyatli** xarid — qayerdan, nima uchun muvaffaqiyatli? |
| **3. Bizni qanday topdi** | Biz haqimizda **birinchi marta** qanday bildingiz? (kanal samaradorligi) |
| **4. Tanlov sababi** | Nega aynan bizdan oldingiz? Nimani taqqosladingiz? Muqobil nima edi? |
| **5. Qiyinchilik** | Buyurtma berishda nima qiyin bo'ldi? Nimani topa olmadingiz? |
| **6. Ishonch** | Nima ishonch berdi? Nima shubha uyg'otdi? ([[etiroz-javob-patternlari]]) |
| **7. Kanal qulayligi** | Telefon/Telegram orqali buyurtma qulaymi? Nega? |

**Ballash:** har javob **1-10** bilan baholanadi (masalan, qulaylik) — keyin o'rtacha bo'yicha ustuvorlik chiqadi.

## Xom natijadan topilmaga

1. Har javobni **iqtibos + ball** bilan yoz.
2. Takrorlanadigan patternlarni ajrat (kamida **2 mijoz** aytgan bo'lsa — signal).
3. Har pattern uchun: **sabab → tuzatish → mas'ul → muddat** jadvali.
4. Natijani [[cjm-mijoz-yoli]] ga ulang (qaysi bosqichda qaysi muammo).

## Haqiqiy natijalardan chiqqan patternlar (UZ/RU bozor)

🟡 **TAJRIBA** — bitta CustDev, kichik namuna; nishaga qarab tekshiriladi.

| Pattern | Tuzatish |
|---|---|
| **Sharhlar hal qiluvchi** — "Mustaqil resurslardagi sharhlar (juda muhim)" | Sharhlarni tashqi maydonchalarga chiqar (Google Maps, marketplace) |
| Tanilgan/ishonchli do'kon afzal | Portfolio, real manzil, jonli raqam ko'rinadigan joyda |
| **Mobil versiya muammosi** — telefondan ma'lumot olish noqulay | Mobil-first dizayn; kichik ekranda tekshirish |
| **Telefon raqami topilmaydi** | Raqamni ko'rinadigan joyga (hero/footer) |
| **Yetkazish jarayoni noaniq** | Sxema: qachon, qanday, treking |
| **To'lov ikonkalari** | Click, PayMe, Uzum, UzCard, Humo — ko'rsatilgan bo'lsin |
| Xarakteristikalar to'liq emas | Mahsulot blokiga to'liq spetsifikatsiya |
| Onlayn chat / tezkor javob kutiladi | Telegram/chat kanali; javob vaqti aniq |

## Artefakt

`CUSTDEV-<mijoz>.md`: savollar · javoblar (iqtibos+ball) · patternlar jadvali · tuzatishlar rejasi (mas'ul+muddat).

**Bu reja keyin:** landing tuzatishlari ([[sop-matn-auditi]]), taklif/offer ([[sop-pozitsiyalash-offer-qurish]]) va kreativ angellar ([[video-kreativ-tizimi]]) uchun kirish bo'ladi.

## Manba

- `claude-ads-main/local/raw/kanal-bilim/26_Custdev.txt`
