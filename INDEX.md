---
name: INDEX
description: Vault xaritasi (MOC) — wiki bilimlar, raw manbalar, hujjatlar, qo'shish qoidasi
tags: [index, vault, moc]
source: mybrain spec (2026-09-03)
updated: 2026-09-16
---

# 🗂 MYBRAIN — MUNDARIJA (MOC)

> **O'qish:** bilim izlashda yoki yangi qayd yozishdan oldin (takror bormi?). Boot'da to'liq wiki o'qilmaydi — [[CLAUDE.md|router]] + [[AGENTS.md|shartnoma]] + shu fayl kifoya.
> **Qoida:** yangi wiki qayd → shu jadvalga havola qo'shish **majburiy**. Havolasiz fayl = yo'qolgan fayl.

## Tuzilma xaritasi

| Joy | Nima | Holat |
|-----|------|-------|
| `wiki/` | Atomik, wikilink bog'langan bilim qaydlari (100) | faol |
| `raw/` | Xom manbalar (verbatim arxiv) | faqat o'qish |
| `vedio bilimlar/` | Video transkriptlar — xom manba: `vedio bilimlar/youtubedagilar/` (16 fayl, ingest manbasi) | faqat o'qish |
| `AGENTS.md` | **Kanonik agent shartnomasi** — qatlamlar, agentlar, ish tartibi | boot |
| `CLAUDE.md` | Router — yo'l xaritasi (avtomatik yuklanadi) | <=300 qator |
| `README.md` | Tyrion nima, tez boshlash, papkalar xaritasi | kirish |
| `rules/` | Doim amal qiladigan qoidalar (7 qoida + indeks) | kanonik |
| `commands/` | Tez buyruqlar (`/savol`, `/audit`, `/kreativ`, `/hisobot`, `/bot`, `/doctor`) | kanonik |
| `hooks/` | Deterministik nazorat (brief · ingest · DoD) | faol |
| `manifests/` | `catalog.json` — hamma narsaning reestri | **generatsiya** |
| `tests/` | Asboblar testlari (stdlib `unittest`) | faol |
| `LOG.md` | Har bir o'zgarish tarixi | tepaga qo'shiladi |
| `templates/` | Fayl andozalari (`wiki-qayd.md`) | yangi qayd yozishda |
| `audits/` | Haftalik audit hisobotlari (`report-YYYY-MM-DD.md`) | hafta oxirida |
| `archive/` | Arxivlangan material — hech narsa o'chirilmaydi | kerak bo'lganda |
| `graphify-out/` | Bilim grafi (`graph.json`, `GRAPH_REPORT.md`) — generatsiya | `tools/gy.cmd` orqali |
| `claude-ads-main/` | Ijro dvigateli: 35 charter, 33 + 21 skill (`.agents/skills/` — `video-editing`, `video-motion-graphics`), playbooklar, `local/` (UZ), `outputs/` | alohida yuritiladi |

### ⭐ Asosiy yo'nalishlar (2026-09-20 — ustuvor uch)
| Qayd | Nima haqida |
|------|-------------|
| [[meta-katta-byudjet-scaling]] | **Katta byudjet:** marginal CPA/ROAS matematikasi, 6 shartli scale darvozasi, vertikal/gorizontal qadamlar, pause intizomi, change packet |
| [[video-kreativ-tizimi]] | **Video kreativ:** hook/tana/CTA arxitekturasi, 9 format, test tartibi, spec darvozasi, fatigue, AI pipeline |
| [[video-skript-shablonlari]] | 9 format uchun to'ldiriladigan skript shablonlari (`{hook}`/`{proof}`/`{CTA}`) |
| [[bozor-analizi-tizimi]] | **Bozor tahlili:** 10 tamoyilli fikrlash intizomi, Ads Library g'olib oqimi, RAQOBAT.md artefakti, UZ tuzatishlar |
| [[mijoz-tadqiqoti-custdev]] | **CustDev:** savol bloklari, ballash, topilmalarni rejaга aylantirish (haqiqiy natijalar) |
| [[ozbekiston-raqamli-bozor]] | **Bozor raqamlari (sanali):** internet 89%, FB/IG ~15 mln, erkak 67%, 18-34 asosiy |

## Bilimlar bazasi (wiki/)

### Token va kontekst gigiyenasi
| Qayd | Nima haqida | Manba |
|------|-------------|-------|
| [[token-gigiyenasi]] | 18 amaliy xak: sessiya, MCP (~17–18k token), batching, plan, 60% qoidasi | 2026-09-03-token-gigiyena-va-meta-mashinasi.md |
| [[prompt-caching]] | Cache read 10x arzon, TTL 1 soat / 5 daqiqa, cache breakers | shu manba |
| [[session-handoff]] | Kontekst to'lganda 150 so'z xulosa → /clear → yangi sessiya | shu manba |
| [[sub-agentlar]] | .claude/agents/ kichik agentlar (researcher, code-reviewer andozasi) | shu manba |

### Meta Ads mashinasi (Owen Rensland)
| Qayd | Nima haqida | Manba |
|------|-------------|-------|
| [[shown-appointments]] | Pay-per-result model: $147/$297 shown uchrashuv, 1-1-1 qoidasi | shu manba |
| [[more-better-new]] | Hormozi o'sish dastagi — More/Better/New qarorlari | shu manba |
| [[survey-funnel]] | 3–4 savol → kontakt → HighLevel taqvimi; Speed to Lead 5 daqiqa | shu manba |
| [[meta-ads-sozlamalari]] | Leads, broad targeting, faqat feed'lar, $30–50/kun, learning phase, Pixel hodisalari | shu manba |
| [[meta-ads-interest-api]] | Graph API v19.0 orqali qiziqishlar (interests) tadqiqoti — read-only agent vositasi, token foydalanuvchi tomonidan kiritiladi | foydalanuvchi konfiguratsiyasi (2026-09-07) |
| [[kreativ-sikl]] | Statik + narx langari, haftalik avtonom refresh (MetaMCP + Higgsfield), fatigue | shu manba |
| [[sotuv-va-retention]] | Speed to Lead (80% qulash), 8 aloqa, "silence feels like a scam", 30 uchrashuv qoidasi | 2026-09-03-meta-qoidalar-va-protokol.md |
| [[meta-ads-library-tadqiqot]] | Ads Library competitive research — active ads/impressions/30-60 kun, watermark yechimi | 2026-09-03-meta-ads-library-workflow.md |
| [[ad-iteration]] | O'z g'olib mezonlari (ROAS>2x, $5k/30kun), 6 variant/5 daqiqa, AI prompt shabloni | shu manba |
| [[mijoz-ishga-tushirish]] | ⭐ Mijoz kuni SOP — preflight, onboarding, kampaniya, voronka, hisobot | wiki qoidalar yig'indisi |

### Video bilimlar (youtubedagilar ingest — 2026-09-11)

> 16 ta video transkriptdan 23 ta atomik qayd (wiki 18→41). Xom transkriptlar `vedio bilimlar/youtubedagilar/`da — o'zgartirilmaydi. Manba: har qayd frontmatter'ida.
> **MOC:** [[video-manbalar]] — qaysi video qaysi qaydni tug'dirgani (16 transkript tarmoqqa ulangan).

### Meta algoritm va kampaniya tuzilmalari
| Qayd | Nima haqida |
|------|-------------|
| [[andromeda-scalability-signal]] | Andromeda 2 signal (efficiency + scalability) — scaling devori, yangi round = yangi ad set |
| [[meta-kampaniya-tuzilmalari]] | ABO/CBO/1-1-1/1-5-5/ASC katalogi, testing+scaling split, "struktura operatsiyadan keyin" |
| [[learning-phase-qoidalari]] | ~50 konversiya/hafta, reset qiladigan o'zgarishlar, 3–5 ad set chegara |
| [[akkaunt-audit-xatolari]] | Auditdagi takroriy xatolar: haddan tashqari tweak, over-segmentatsiya, charchagan ad set |
| [[blended-roas-net-cash]] | Kuzatiladigan to'g'ri metrika — blended ROAS + net free cash flow, break-even ROAS |
| [[scaling-cheklovlari]] | TAM shift, eksponent o'sish = yangi angle/audience/offer, tayyor fond sharti |

### Kreativ va offer
| Qayd | Nima haqida |
|------|-------------|
| [[content-is-targeting]] | Kreativ o'zi targeting — avatar+angle=concept, angellar alohida masshtablanadi |
| [[kreativ-hit-rate]] | Hit rate formulasi (>5% kampaniya byudjeti), sifat > hajm |
| [[funnel-2-kreativ-format]] | Faqat 2 format: TOF problem-solution + BOF objection |
| [[unique-mexanizm]] | Reklama anatomiyasi: avatar → muammolar → solution × unique mechanism |
| [[taklif-tuzilishi]] | Offer = value exchange + timing + risk profile; BOGO matematikasi |
| [[brend-kreativ-strategiyasi]] | Dizayndan oldin strategiya — 5 savol, discovery, big idea |

### Lead va strategiya
| Qayd | Nima haqida |
|------|-------------|
| [[lead-magnet-turlari]] | 3 tur lead magnet — capture 3-5x oshadi, traffic oshmasdan |
| [[lead-magnet-yetkazish-nomlash]] | 4 yetkazish usuli, headline talabni 2-10x o'zgartiradi, CTA formulasi |
| [[funnel-filtr-qoidalari]] | Funnel = filter: friction vs lead sifati muvozanati |
| [[cjm-mijoz-yoli]] | CJM shablon: 5 bosqich × 6 qator; qaysi bosqichda qaysi matn turi kerak |
| [[proof-promise-qoidasi]] | Promise unikal emas, proof unikal — proof kontinuumi |
| [[birinchi-100k-yol-xaritasi]] | Birinchi $100K — 6 qadam, 10,000 iteratsiya |
| [[ajralib-turish-kobalt-ferrari]] | Top 5% blogger 95% bozorni oladi — xarizma + nusxalanmas storytelling |

### Google Ads va AI pipeline
| Qayd | Nima haqida |
|------|-------------|
| [[google-ads-search-kampaniya-qollanma]] | Search kampaniya noldan: tuzilma, match types, negative keywords, 3 conversion action |
| [[google-ads-kolisey-kalit-sozlari]] | 80/20 fractal: transactional "Coliseum" kalit so'zlar 64% natija |
| [[google-ads-raqobat-brendi]] | Raqobatchi brend nomlariga bidding — qoidalari va chegaralari |
| [[google-ads-avtomatlashtirish]] | Kampaniya turi tanlash, tROAS minimal hajmi, enhanced conversions (SHA256), Consent Mode v2 |
| [[bozor-trend-kreativi]] | Winning creative 3-manbali AI pipeline, market trends, FB Ads MCP kunlik ro'yxat |
| [[instagram-kontent-uchburchagi]] | 20% shaxsiy / 70% mutaxassislik / 10% sotuv — blog platosidan chiqish |

### Sifat va metod (2026-09-20 — claudes-bilim ingest)
| Qayd | Nima haqida |
|------|-------------|
| [[dalil-tasnifi]] | Da'vo tasnifi: FAKT/TAJRIBA/FIKR/REKLAMA, manba rubrikasi 1-5, ziddiyat tartibi, noaniqlik |
| [[sifat-darajasi]] | Topshirish chegarasi: 5-yillik mutaxassis sinovi, 8 ta qabul qilinmaydigan chiqish, universal 6 band |

### Strategiya, iqtisod va test
| Qayd | Nima haqida |
|------|-------------|
| [[pozitsiyalash-dunford]] | April Dunford: 5+1 komponent, ICP vs persona, negativ ICP, pozitsiyalash bayonoti |
| [[unit-iqtisodiyot-formulalari]] | CAC/CPL/LTV/ROAS/POAS/MER, break-even va target ROAS, LTV:CAC chegaralari |
| [[voronka-metrikalari]] | TOFU/MOFU/BOFU, AARRR, diagnostika qoidasi, benchmarklarni ehtiyotkor ishlatish |
| [[narxlash-va-narx-psixologiyasi]] | 5 narxlash modeli, tier dizayni, anchoring/decoy/left-digit mexanikasi, kafolat turlari |
| [[ab-test-mexanikasi]] | Namuna hajmi formulasi, kichik trafik alternativasi, testni buzadigan 5 xato |

### Kopirayter va matn
| Qayd | Nima haqida |
|------|-------------|
| [[kopirayter-frameworklar]] | 5 qarshilik, PAS/AIDA/BAB/4P/FAB/PASTOR, tanlash jadvali, sarlavha sinovi |
| [[zaifdan-kuchli-matn]] | 26 juftlik zaif→kuchli jadvali va matn audit usuli ("demak nima?" testi) |
| [[etiroz-javob-patternlari]] | 6 e'tiroz ("qimmat", "ishonmayman", ...) va javob patternlari |
| [[ijtimoiy-dalil-tartibi]] | Ishonch kuchi 1-10 tartibi, sharh yozdirish shabloni |
| [[cialdini-7-printsip]] | 7 ta ta'sir printsipi — mexanikasi, tajriba isboti, matnda qo'llash |
| [[reklama-matn-limitlari]] | Meta Feed, RSA va PMax belgi limitlari + learning phase ta'siri |
| [[ozbek-sotuv-matni-standarti]] | Murojaat, ruscha kalkalar, ritm, uch tilli bozor, mahalliy ishonch signallari |
| [[telegram-voronka-va-email-minimum]] | Telegram voronka strukturasi + email deliverability (SPF/DKIM/DMARC, spam chegarasi) |
| [[telegram-ads-platformasi]] | Telegram Ads rasmiy platformasi (Fragment/ads.telegram.org), kanallar, 160 belgi, bot voronkasi |

### SOP — ish protokollari (2026-09-20 — claudes-bilim playbook/checklist)
| Qayd | Nima haqida |
|------|-------------|
| [[sop-xarita]] | ⭐ **Router**: vazifa → qaysi SOP yuklanadi (agentlar shu yerdan boshlaydi) |
| [[sop-pozitsiyalash-offer-qurish]] | ⭐ PoYDEVOR: muqobillar → farqlar → ICP → toifa → Value Equation → offer jumlasi |
| [[sop-raqobat-tahlili]] | Ochiq manbalar, mijoz sharhlari, bo'sh joyni topish, bitta farqlanish o'qi |
| [[sop-voronka-loyihalash]] | Bosqichlar zanjiri, Telegram ustuvorligi, eng tor joy, nazorat paneli |
| [[sop-kampaniya-rejalash]] | Iqtisod oldin, platforma tanlash, konversiya hodisasi, test va to'xtatish qoidalari |
| [[sop-kampaniya-diagnostika]] | Avval iqtisod; belgi→sabab→harakat jadvali; bitta jumlali raqamli diagnoz |
| [[sop-narxlash-paket-qurish]] | Uch chegara, model tanlash, 3 paket + langar, risk yechimi |
| [[sop-oylik-hisobot]] | Kanal raqamlari, voronka taqsimoti, 3 harakat, biznes tilida |
| [[sop-landing-matni]] | 9 kirish savoli → 10 qadam → artefakt; 0 bo'sh sifat mezoni |
| [[sop-matn-auditi]] | Diagnostika jadvali, P0/P1/P2, oldin→keyin, xabar mosligi |
| [[sop-meta-reklama-matni]] | 5 variant 5 burchakdan, belgi chegaralari, bir vaqtda test qoidasi |
| [[sop-ketma-ketlik-yozish]] | Email/Telegram: welcome/nurture/launch/win-back, bitta maqsad qoidasi |
| [[sop-uzun-sotuv-sahifasi]] | PASTOR, offer stacking, tekshiriladigan kafolat, "kim uchun emas" |
| [[sop-mahsulot-tavsifi]] | "Demak nima?" testi, struktura, shablon, marketplace birinchi jumlasi |
| [[sop-brend-ovozi]] | 3 o'q shkalasi, 12+ "shunday/shunday emas" juftlik, kanal moslashtirish |
| [[topshirish-cheklist-matn]] | Matn ishi: A-I bo'limlar (~50 band) — bitta "yo'q" = tugallanmagan |
| [[topshirish-cheklist-strategiya]] | Strategiya ishi: A-H bo'limlar — iqtisod, offer, voronka, reklama, narx |

## Tizim qatlami (qoida, buyruq, hook)

| Qatlam | Nima | Fayl |
|--------|------|------|
| **Shartnoma** | Qatlamlar, 36 agent, orkestratsiya, tamoyillar | [[AGENTS.md]] |
| **Qoidalar** | Manba · til · token · UZ kontekst · xavfsizlik · DoD · loyiha papkasi | [[rules/README]] |
| 00 | Manba majburiyati — raqam to'qilmaydi | [[00-manba]] |
| 10 | Til va uslub — o'zbekcha, atamalar inglizcha | [[10-til-va-uslub]] |
| 20 | Token gigiyenasi | [[20-token-gigiyena]] |
| 30 | O'zbekiston konteksti | [[30-ozbekiston-konteksti]] |
| 40 | Xavfsizlik va hisob (read-only, draft+tasdiq) | [[40-xavfsizlik-va-hisob]] |
| 50 | Topshirish darvozasi (DoD) | [[50-topshirish-dod]] |
| **Buyruqlar** | `/savol` `/audit` `/kreativ` `/hisobot` `/bot` `/doctor` | `commands/` |
| **Hook'lar** | Sessiya holati · ingest nazorati · topshirish darvozasi | [[hooks/README]] |
| **Asboblar** | doctor · catalog · skill-search · gy.cmd · vault-audit · tyrion-mcp-server | [[tools/README]] |
| **Skill router** | Agent ishni boshlashdan oldin skill talash so'rovi; skill ↔ agent ikki tomonlama ulanish | [[skill-router]] |

## Vault tizimi (arxitektura + AIOS audit)
| Qayd | Nima haqida | Manba |
|------|-------------|-------|
| [[wiki-arxitektura]] | Karpathy uslubi — nega RAG emas markdown; raw/wiki qatlami | 2026-09-03-meta-qoidalar-va-protokol.md |
| [[kontekst-xatolari]] | Hallucination'ning 4 sababi: Poisoning, Bloat, Confusion, Clash (+ profilaktika) | 2026-09-03-aios-xatoliklar-va-audit.md |
| [[kontekst-ajratish]] | Expertise (doimiy) vs Situational (vaziyatli) — just-in-time yuklash | shu manba |
| [[haftalik-audit]] | Read-only haftalik audit → audits/report-YYYY-MM-DD.md | shu manba |
| [[agent-os-qatlami]] | ⭐ Tyrion agent-OS qatlami (2026-09-16) — AGENTS.md, rules/, commands/, hooks/, katalog, doctor; ECC'dan olingan naqshlar va rad etilganlari | affaan-m/ECC tahlili (raw/2026-09-16) |

## Xom manbalar arxivi (raw/)

- `raw/2026-09-03-token-gigiyena-va-meta-mashinasi.md` — token gigiyena + sub-agentlar + Meta mashinasi + DoD (verbatim)
- `raw/2026-09-03-mybrain-vault-spec.md` — vault qayta tuzish speki (verbatim)
- `raw/2026-09-03-aios-xatoliklar-va-audit.md` — 4 xato sababi + kontekst ajratish + haftalik audit (verbatim)
- `raw/2026-09-03-meta-qoidalar-va-protokol.md` — Media buying, Sales & Retention, caching, Karpathy, MCP, protokol (verbatim)
- `raw/2026-09-03-meta-ads-library-workflow.md` — Meta Ads Library workflow (Sam Piliero brief'i + tahlil)
- `raw/2026-09-16-ecc-naqshlar-tahlili.md` — ECC (affaan-m/ECC v2.2.1) → Tyrion: ko'chiriladigan naqshlar tahlili, 396 qator ([[agent-os-qatlami]] manbasi)
- Qoidalar: `raw/README.md`

## Hujjatlar

- [[AGENTS.md|Agent shartnomasi]] — kanonik: qatlamlar, agentlar, ish tartibi · [[README.md|Kirish]] — Tyrion nima, tez boshlash
- [[CLAUDE.md|Router]] — bosh yo'naltiruvchi · [[LOG.md|Harakatlar tarixi]] — nima qilindi, qachon
- Arxiv: [[archive/README|archive/]] — code skill'lar va eski charter nusxalari (hech narsa o'chirilmaydi)
- Qo'shni tizim: `claude-ads-main/local/wiki/index` (repo ichki wiki) · `claude-ads-main/local/meta-playbook-uz` (Meta $1k playbook)

## Bilim qo'shish qoidasi (ingest protokoli)

1. Bitta fayl — bitta tushuncha (aralash fayl yo'q)
2. Frontmatter: `name`, `description`, `tags`, `source`, `updated` — qiymatda `:` bo'lsa qo'shtirnoqqa ol; **qo'shtirnoq ichida `\` ishlatilmaydi** (`\t` qiymatni jim buzadi — yo'l uchun `/` yoziladi); andoza: `templates/wiki-qayd.md`
3. Kamida 2 ta wikilink havola — shu jadvalga qo'shiladi
4. Yangi xom manba → `raw/` ga (verbatim), tahlil → `wiki/` ga
5. Tugagach: `LOG.md` tepasiga 1 qator sana+harakat

**Nazorat:** `py -3 tools\vault-audit.py` (0 muammo) · `py -3 tools\doctor.py` (0 xato) · `py -3 hooks\tyrion-hook.py ingest`
| [[uzluksiz-organish-instinktlar]] | ECC continuous-learning naqshi asosida Tyrion instinktlar tizimi — kampaniya saboqlarini yig'ish, ishonch balli (1-5) bilan baholash va wiki/memory qatlamiga ko'tarish | raw/2026-09-16-ecc-naqshlar-tahlili.md + affaan-m/ECC continuous-learning-v2 (2026-10-17) |
| [[verification-loop-6-bosqich]] | Marketing auditi, kreativ va kampaniya o'zgarishlarini topshirishdan oldin 6 bosqichli deterministik tekshiruv zanjiri (ECC verification-loop adaptatsiyasi) | raw/2026-09-16-ecc-naqshlar-tahlili.md §6 + rules/50-topshirish-dod.md (2026-10-17) |
| [[meta-auditoriya-arxitekturasi]] | Meta Ads Andromeda 2 auditoriya arxitekturasi — 4 qatlamli voronka (Broad, Interest Stack, 1P Custom Audience, Value LAL), Exclusion matritsasi, Overlap va Saturation matematikasi | tools/meta-audience.py + wiki/meta-kampaniya-tuzilmalari.md + wiki/andromeda-scalability-signal.md (2026-10-18) |
| [[b2b-xizmatlar-strategiyasi]] | B2B xizmatlar (agentlik, konsalting, IT, marketing) uchun reklama strategiyasi — video transkriptdan | kanal-bilim/27 (Screen Recording transkript, sifat o'rtacha) |
| [[bosh-agent-protokoli]] | \"Bosh agent yo'q\" muammosiga yechim — conductor kim, workerlar bilan chegara, plan approval, clean shutdown | operator taqdim etgan CEO/orchestrator 4 tamoyili (2026-09-07) + ads/SKILL.md#Worker-orchestration tahlili |
| [[brend-pozitsiyalash]] | Brend strategiya — brend vs marketing farqi, brend mohiyati, logo/rang sirlari (Sevara Asamova + brend tanilish) | kanal-bilim/06, 07 (PDF/TXT konvert) |
| [[custdev-shablonlar]] | CustDev intervyu shablonlari — tayyorgarlik checklist, tovarlar/xizmatlar savolnomasi, hisobot namunasi | kanal-bilim/26 (Custdev.xlsx konvert) |
| [[kontent-formulalari]] | Hooklar, Reels formatlari, kontent rubrikalari — kontent yaratish formulalari | kanal-bilim/01, 03, 04 (PDF konvert) |
| [[metrikalar-formulalari]] | Marketing metrikalari formulalari (ROI, ROAS, ROMI, CPP, CAC, CR) + SMS case raqamlari | kanal-bilim/10, 15 (TXT konvert) |
| [[nisha-playbooklar]] | Nishalar bo'yicha tayyor strategiyalar — atir, sport zal, avtoservis, mehmonxona, xususiy maktab | kanal-bilim/05, 16, 17, 18, 20, 23 (PDF/TXT konvert) |
| [[optimitzaetsiya-va-case]] | Real tajriba cases — CPL 2x arzon, tezkor loyiha SOP, yuqori chek mijozlar, budget qoidalari, bloggerlar ro'yxati | kanal-bilim/08, 11, 13, 14, 19, 21 (TXT konvert) |
| [[mcp-va-multi-harness-integratsiya]] | Tyrion v5.0 Native MCP Server (.mcp.json) va Multi-Harness Exporter (Claude Code, Cursor .mdc, Windsurf, Codex) arxitekturasi | affaan-m/ECC install-targets + pipeboard-co/meta-ads-mcp + googleads/google-ads-mcp (2026-10-18) |
| [[meta-breakdown-effekti]] | Meta Ads 'Breakdown Effect' (Marginal vs Average CPA) — nega o'rtacha CPA baland ko'ringan placement yoki segmentni o'chirish umumiy natijani buzadi | Meta Official Breakdown Effect Documentation + mathiaschu/meta-ads-analyzer tahlili (2026-10-18) |
