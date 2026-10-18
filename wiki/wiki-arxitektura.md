---
name: wiki-arxitektura
description: Karpathy uslubi — nega RAG emas oddiy markdown + wikilinks; raw/wiki ikki papkali bilim arxitekturasi
tags: [vault, karpathy, arxitektura, aios]
source: "raw/2026-09-03-meta-qoidalar-va-protokol.md (§ 3-QISM: Obsidian va Karpathy LLM Wiki)"
updated: 2026-09-03
---

# Wiki arxitektura — nega RAG emas, oddiy Markdown (Karpathy)

Andre Karpathy uslubi: **qimmat va xatolik beruvchi vektor bazalari o'rniga** oddiy `.md` fayllar + ularni wikilink havolalar bilan o'zaro bog'lash.

> Amaliy tarmoq namunasi: [[video-manbalar]] — xom manba (transkript) bilim qaydiga qanday ulanadi.

## Ikkita asosiy papka

| Papka | Nima | Vazifasi |
|-------|------|----------|
| `raw/` | O'zgartirilmagan asl manbalar (video matni, maqola, PDF) | Verbatim arxiv — faqat o'qish |
| `wiki/` | AI qayta ishlagan atomik, ixcham qaydlar | Qidiriladigan bilim |

## Nega ishlaydi

- AI faylni **to'g'ridan-to'g'ri o'qiydi** — RAG chunk/semantik qidiruv xatolari yo'q
- Fayl sathidagi marshrutlash: [[INDEX.md]] (MOC) → aniq qayd → kerak bo'lsa manba
- Xom va qayta ishlangan qatlam ajralgan → [[kontekst-ajratish]] qoidasi bajariladi
- 4 xato rejimi shu tuzilmada nazorat qilinadi: [[kontekst-xatolari]]
- Doimiy tekshiruv: [[haftalik-audit]]
