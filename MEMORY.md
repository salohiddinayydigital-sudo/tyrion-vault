# 🧠 TYRION — OPERATOR XOTIRASI (BOOT FILE)

> **Chegara:** Ushbu fayl har sessiya boshida o'qiladi — **90 qatordan oshmasligi shart** (`doctor.py` nazorat qiladi).
> Batafsil qoidalar `rules/` da, bilimlar `wiki/` da saqlanadi.

## §1. Til va Uslub Qonuni (`rules/10-til-va-uslub.md`)
- Javob tili: **O'zbek (lotin)**. Texnik atamalar (`Pixel`, `CAPI`, `ROAS`, `CPA`, `learning phase`, `ad set`, `hook`, `offer`) inglizcha qoladi.
- Kirishsiz, zich, jadval va ro'yxat asosida. Mijoz reklama matnlari 3 tilda (uz lotin / kirill / rus) **alohida** yoziladi (tarjima emas).

## §2. Tezkor Orkestratsiya va Asboblar (`AGENTS.md`)
- **Bilim qidirish (0 token):** `py -3 tools/brain-search.py search "<so'z>"` → `tools/gy.cmd query "<savol>"` → `INDEX.md`.
- **Skill tanlash (0-qadam):** `py -3 tools/skill-search.py brief "<vazifa>" --agent <agent_nomi>`.
- **Matematika va Xavfsizlik:** `py -3 tools/calculator.py ...` va `py -3 tools/spend-guard.py ...`.
- **Tizim va Xavfsizlik Auditi:** `py -3 tools/doctor.py --quick` va `py -3 tools/tyrion-shield.py scan`.

## §3. O'zbekiston Bozori Asoslari (`rules/30-ozbekiston-konteksti.md`)
1. **Asosiy voronka:** Meta/Instagram Ads + Telegram Ads → **Telegram bot / DM → CRM (AmoCRM/Bitrix24)**. Email voronka B2C da ishlamaydi.
2. **To'lov tizimlari:** Payme, Click, Uzum Bank, Humo/UzCard (bo'lib to'lash / nasiya konversiyani 2x oshiradi).
3. **Mavsumiylik:** Ramazon/Hayit, Navro'z, Sentabr (o'quv mavsumi), Dekabr (yil yakuni).
4. **Benchmark qoidasi:** Global CTR/CPC/ROAS ko'chirilmaydi; faqat akkauntning o'z tarixi va break-even matematikasi asos bo'ladi.

## §4. Faol Loyihalar Ko'rsatkichi (`rules/60-loyiha-papkasi.md`)
- Namuna/Demo loyiha: `examples/demo-brand/` (Meta Andromeda 1-5-5, Google Coliseum, Telegram Ads sinov paketi).
- Real mijoz loyihalari: `clients/<slug>/` (`BRIEF.md`, `journal.md`, `assets/`, `outputs/`, `MANIFEST.md`).

## §5. Aktiv Gipotezalar (Bet Ledger)
| ID | Platforma | Gipoteza | Mezon (Target) | Holat |
|----|-----------|----------|----------------|-------|
| B01 | Meta Ads | 1-5-5 ABO Sandbox orqali 3 ta yangi burchak sinovi | FTIR >= 60%, CPA <= Break-even | Faol |
| B02 | Google Ads | Coliseum high-intent exact/phrase + PMax brand exclusion | Wasted spend < 10%, ROAS >= 3.0x | Faol |
| B03 | Telegram Ads | Saralangan >15% ERR kanallar + `?start=utm` bot voronka | Bot start >= 65%, CPL <= Target | Faol |

## §6. Saboqlar va Instinktlar (`manifests/instincts.json` · `/learn`)
1. **YAML va JSON yo'l xatosi (2026-09-16):** Frontmatter va JSON ichida `"path\to\vault"` yozilsa `\t` TAB belgisiga aylanib faylni jim buzadi — har doim `/` (`D:/tyrion`) ishlatilsin.
2. **Mirror va Katalog Drift (2026-09-20):** Qo'lda yozilgan agent/skill/wiki sonlari eskiradi — har o'zgarishdan so'ng `py -3 tools/catalog.py sync-mirrors` va `sync-claims` ishga tushirilsin.
3. **Meta ASC Cheklovi (2026-09-11):** Advantage+ Shopping kampaniyasida Existing Customer Cap 25-30% qilib belgilamasa, algoritm byudjetni issiq auditoriya retargetingiga sarflab yuboradi.
4. **Google PMax Kannibalizatsiyasi (2026-09-11):** PMax kampaniyalarida Brand Exclusions yoqilmasa, brend qidiruv trafigini o'zlashtirib ROAS'ni sun'iy shishiradi.
5. **Telegram Ads 160 Belgi Qonuni (2026-09-16):** Telegram rasmiy reklamalarida <=160 belgi, ko'pi bilan 1 ta emoji va ALL CAPS'siz yozish moderatsiya va CTR uchun majburiy.
6. **Secret Xavfsizligi (2026-10-17):** `.env` fayllari hech qachon arxiv yoki git ichida qolmasligi shart; `tyrion-shield.py` orqali doimiy tekshiriladi.
