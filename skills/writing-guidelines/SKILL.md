---
name: writing-guidelines
description: Review docs/prose for Writing Guidelines compliance. Use when asked to "review my docs", "check writing style", "audit prose", "review docs voice and tone", or "check this page against the writing handbook".
triggers:
- yozish uslubi
- writing style
- aniq matn
- tone of voice
- стиль текста
- правила письма
aliases:
- style-guide
- clarity-rules
domains:
- copywriting
- editing
platforms:
- multi-platform
attached_agents: [copy-writer]
related_skills:
- copy-editing
- copywriting
references: []
risk_level: low
output_contract: Style-checked, fluff-free professional marketing prose
---

# Writing Guidelines

Review files for compliance with Writing Guidelines.

## How It Works

1. Fetch the latest guidelines from the source URL below
2. Read the specified files (or prompt user for files/pattern)
3. Check against all rules in the fetched guidelines
4. Output findings in the terse `file:line` format

## Guidelines Source

Fetch fresh guidelines before each review:

```
https://raw.githubusercontent.com/vercel-labs/writing-guidelines/main/command.md
```

Use WebFetch to retrieve the latest rules. The fetched content contains all the rules and output format instructions.

## Usage

When a user provides a file or pattern argument:
1. Fetch guidelines from the source URL above
2. Read the specified files
3. Apply all rules from the fetched guidelines
4. Output findings using the format specified in the guidelines

If no files specified, ask the user which files to review.

---

## Asosiy qoidalar (offline xulosa)

> Manba: `https://raw.githubusercontent.com/vercel-labs/writing-guidelines/main/command.md` — WebFetch yuklandi (2026-09-04). To'liq audit uchun hali ham yuqoridagi URL'dan yangi qoidalar yuklanadi; quyida manbadagi eng muhim qoidalarning offline xulosasi.

1. Har sahifa rejaga ega; `meta.contentType` e'lon qilinadi: Tutorial, How-to, Reference, Conceptual, Troubleshooting yoki Landing (manba: Planning & content type)
2. Sarlavha foydalanuvchi savoliga qarab (user-shaped), xususiyat nomiga qarab emas; sahifa bitta ish qiladi (tutorial yoki how-to, uchtasi birdan emas) (manba: Planning & content type)
3. Faol nisbat: "by monkeys" testi; to'g'ridan-to'g'ri `you` — "the user" emas; qadamlar buyruq maylida (manba: Voice & tone)
4. Jumlalar <20 so'z (maqsad); qisqartmalar (you'll) issiqlik uchun rag'batlantiriladi; hozirgi zamon (manba: Voice & tone)
5. `we` faqat qasddan qilingan harakatlar uchun ("we recommend"), "you" o'rnini bosmaydi; ritorik savollar taqiq (manba: Voice & tone)
6. Taqiqlangan so'zlar: `easy`, `simple`, `quick` (o'quvchiga bosim o'qiydi); `very`, `just`, `really` — to'ldiruvchi (manba: Banned words)
7. Weasel so'zlar (`significantly`, `many`, `often`, `typically`) aniq raqamga almashtiriladi; noaniq miqdor yo'q — raqam manbasi bilan beriladi (manba: Concision)
8. Em dash `—` tinish sifatida taqiq — nuqta/vergul/ikki nuqta ishlatiladi; jingalak tirnoq `“ ”`; ellipsis `…` — uch nuqta `...` emas (manba: Punctuation & typography)
9. Sarlavhalar sentence case (H1–H3): "Configure environment variables"; nav label title case; kichik sarlavhalar tavsifli, generic emas ("Caveats" yetarli emas) (manba: Headings)
10. Har sahifa 1 paragraf TL;DR bilan ochiladi; har katta bo'lim xulosa jumlasi bilan ochiladi (manba: Structure)
11. Paragraflar 2–4 jumla; 3+ ro'yxat shaklli element bo'lsa — ro'yxatga aylantiriladi va `:` bilan kiritiladi (manba: Lists)
12. Akronimlar birinchi ishlatishda to'liq yoziladi (CSP = Content Security Policy); har atama birinchi uchrashuvda aniqlanadi va bog'lanadi (manba: Structure, Links)
13. Bold — UI elementi yoki kritik fakt uchun, urg'u uchun emas; path/kod/identifierlar inline code bilan (manba: Emphasis)
14. Kod bloklari: language tag; ≤25 qator (uzuni proza bilan bo'linadi); ≤80 ustun; yuklama qatorlar highlight qilinadi; har kod bloki prozada tushuntiriladi (manba: Code)
15. Placeholderlar `snake_case` va tavsifli (`your_access_token_here`); `<TOKEN>`, `xxx`, ALL_CAPS taqiq (manba: Placeholders)
16. Hajmlar: probel + katta harf (`64 KB`, `200 ms`); soniya yalang'och (`30s`) (manba: Data sizes & units)
17. AI-tell'lar taqiqlanadi: o'tgan bo'limni takrorlovchi ochilishlar, stop-start mayda jumlalar, spec-sheet ovozi (`provides`), artefakt personifikatsiyasi, andoza framing (manba: AI-generated tells)
18. Link anchor matni manzilni nomlaydi — bare URL va `here`/`link` taqiq (manba: Links)
19. AI ish oqimi: avval qo'lda plan; model taklif qiladi — inson hal qiladi; yakuniy inson review majburiy; AI ishlatilgani PR'da ochiladi (manba: AI workflow)
20. Pul/narx sahifalari: haddan ortiq detal ("too much" ga xato qilish), jadvallar, o'quvchi modelni biladi deb taxmin qilmaslik (manba: Money & pricing pages)

---

## Operator qatlami (Tyrion lokal bilimi)

> Bu bo'lim — Tyrion (Saloxiddin, O'zbekiston targetolog agentligi) uchun lokal moslashuv. Vendor metodika o'zgarishsiz.

### Qachon ishlatiladi (UZ triggerlari)
- "matn uslubini tekshir" · "hujjatni audit qil" · "voice/tone qoidasini qo'lla" · "bu matn yaxshi yozilganmi" · "writing review ber"

### UZ amaliyot qoidalari (manbalardan)
1. Raqam gigiyenasi: tekshirilmagan raqam yozilmaydi — bilinmasa "ma'lumot yo'q" deb yoziladi (manba: `memory.md` §2 qoida 1)
2. Javob va hujjatlar o'zbekcha (lotin) yoziladi, texnik atamalar inglizcha qoldiriladi (manba: `memory.md` §1 — til qoidasi)
3. Til segmenti toza saqlanadi: o'zbek-lotin/kirill/rus matnlari alohida yoziladi, tarjima yo'li bilan aralashtirilmaydi (manba: `local\ozbekiston-konteksti.md` §3)
4. Bozor matnlarida jargon emas, xalq tili: hook/matn "Poytaxtda kvartira olmoqchimisiz?" uslubida bo'lishi tekshiriladi (manba: `local\ozbekiston-konteksti.md` §3)
5. Reklama matni tekshirilganda qo'shimcha darvoza: Meta policy tekshiruvidan o'tmagan matn "tayyor" deb tasdiqlanmaydi (manba: `memory.md` §2 qoida 5)
6. Miqdoriy da'vo bahosida global benchmark emas — akkauntning o'z tarixi bilan solishtirish qoidasi esda (manba: `local\ozbekiston-konteksti.md` §7.6)

### Bog'liq lokal fayllar
- `memory.md` — til va raqam qoidalari (repo ildizi)
- `local\ozbekiston-konteksti.md` — til segmentlari, xalq tili qoidasi (repo ildizi)
- `local\meta-playbook-uz.md` — benchmark ogohlantirishi
- `wiki/index.md` — vault qaydlari xaritasi (vault: `wiki`)
