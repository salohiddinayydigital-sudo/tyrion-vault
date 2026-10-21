<p align="center">
  <img src="./assets/tyrion-banner.svg" alt="Tyrion AI Paid Media OS Banner" width="100%" />
</p>

# 🧠 TYRION v5.0 — AI PAID MEDIA & TARGETOLOGY OPERATING SYSTEM

[![Version](https://img.shields.io/badge/version-5.0.0--ecc-7C3AED.svg)](./CHANGELOG.md)
[![Architecture](https://img.shields.io/badge/architecture-Single--Root%20ECC-blue.svg)](./AGENTS.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](./LICENSE)
[![Security: TyrionShield](https://img.shields.io/badge/TyrionShield-6%2F6%20Passing-brightgreen.svg)](./SECURITY.md)

<!-- tyrion:catalog agents=36 skills=62 wiki=100 playbooks=9 contexts=6 commands=18 rules=9 tools=29 -->

**Tyrion v5.0 (Calibrated & Live-Telemetry Edition)** — `affaan-m/ECC` (*Everything Claude Code*) arxitekturasi asosida qurilgan **yagona ildizli (Single-Root)** raqamli reklama, targetologiya va growth-marketing operatsion tizimi.

Barcha **36 ta ixtisoslashgan agent**, **62 ta platforma va marketing skilli**, **9 ta amaliy nisha playbooki**, **6 ta dinamik kontekst rejimi**, **18 ta slash buyruq**, **Bilim: atomik qaydlar (100)** va **29 ta 0-token deterministik Python CLI asbob** yagona, kalibrlangan va real ma'lumotlarga bog'langan arxitekturaga birlashtirilgan.

## ✨ Tyrion v5.0 Arxitekturasi (Nima o'zgardi?)

```text
tyrion/
├── AGENTS.md                 # Kanonik Agent Shartnomasi (Claude Code, Cursor, Codex, Windsurf)
├── CLAUDE.md                 # Tezkor Router (<=100 qator, 0-token boot)
├── MEMORY.md                 # Operator Xotirasi, O'zbekiston Konteksti va Aktiv Bet Ledger (<=90 qator)
├── INDEX.md                  # Yagona Bilim Xaritasi (MOC)
├── agents/                   # 36 ta Kanonik Agent Charteri (100% skill ulangan + Prompt Defense)
├── skills/                   # 62 ta Kanonik Skill (36 platforma + 26 operator + 39 reference fayl)
├── commands/                 # 18 ta Slash Buyruq (/audit, /auditoriya, /kreativ, /voronka, /eksport, /utm...)
├── contexts/                 # 6 ta ECC Dynamic Context Mode (audit, launch, scale, creative, uzbekistan + README)
├── playbooks/                # 9 ta Tayyor Nisha va Platforma Playbooki (Meta $1k-$10k, E-com, Ta'lim, Ko'chmas mulk...)
├── rules/                    # 9 ta Buzilmas Qoida (00-manba .. 70-charter-baseline + README)
├── wiki/                     # 100 ta Atomik Bilim Qaydi (Andromeda 2, Meta Audience, Google Coliseum, 16 SOP)
├── tools/                    # 29 ta 0-Token Deterministik CLI Asbob (boshqaruv markazi: tools/tyrion.py)
├── hooks/                    # Deterministik Lifecycle Hooklar (SessionStart, PreToolUse, PostToolUse, Stop)
├── templates/                # 6 ta Tayyor Hisobot, Brief va Launch Shablonlari
├── examples/                 # Demo Mijoz Ish Maydoni va Real Graph API v26.0 JSON namunasi
├── manifests/                # Avto-generatsiya Reestrlari (catalog.json, instincts.json)
└── tests/                    # Avtomatlashtirilgan Unit-Testlar To'plami (stdlib unittest — 100% qamrov)
```

## 🚀 1. Yagona Master CLI (`tools/tyrion.py`)

Tyrion v5.0 barcha hisob-kitob, auditoriya loyihalash, jonli Meta Ads telemetriya sinxronizatsiyasi, kreativ matritsa va xavfsizlik tekshiruvlarini **0 token** sarflab bajaradigan markaziy CLI dvigatelga ega:

```bash
# Tizimning umumiy holati va buyruqlar menyusi
python3 tools/tyrion.py status

# Universal Auto-Router: oddiy tildagi vazifadan agent, skill va workflow'ni avtomatik tanlash
python3 tools/tyrion.py route "Meta reklamamdan kelayotgan lidlar sifatsiz, sababini top"

# Butun tizim sog'lig'ini tekshirish (14 qatlam)
python3 tools/tyrion.py doctor

# TyrionShield v5.0 6-qavatli statik xavfsizlik, AST va governance skaneri
python3 tools/tyrion.py shield
```

## 🎯 2. Kalibrlangan Meta Ads Audience & Live Insights Studio (`tools/meta-audience.py` · `tools/meta-insights-sync.py`)

Meta Andromeda 2 algoritmi uchun **7 ta kalibrlangan modul** (ishonchlilik intervallari, taxminlar izohi va [Meta Graph API v26.0](https://developers.facebook.com/docs/graph-api/changelog/version26.0/) integratsiyasi bilan):

```bash
# 1) Unit-ekonomikaga (AOV, marja, CVR) tayangan 4-Qatlamli arxitektura va Exclusion matritsasi
python3 tools/meta-audience.py architect --niche real-estate --daily-budget 150 --aov 45000 --margin-pct 25 --lead-to-sale-cvr 3.5 --geo tashkent --has-pixel --has-crm

# 2) 8 nisha bo'yicha qiziqishlar + O'zbekiston Solventnost filtrlari + Graph API v26.0 qidiruvi
python3 tools/meta-audience.py interests --niche edu
python3 tools/meta-audience.py interests --niche ecom --query "shopping" --live
python3 tools/meta-targeting-engine.py search --niche real-estate --query "interyer" --query "новостройки" --account-id act_123456789

# 3) Static Pool Overlap (<20% yagona chegara qoidasi) va Live Auction Overlap farqi
python3 tools/meta-audience.py overlap --size-a 180000 --size-b 120000 --shared 25000

# 4) Auditoriya sig'imi, Frequency va charchash oynasi (Conservative / Baseline / Optimistic)
python3 tools/meta-audience.py saturation --audience-size 220000 --daily-budget 80 --cpm 3.5 --days 14 --active-reach-ratio 0.60

# 5) Haqiqiy trafikka tayangan Retargeting Oynalari (--no-telegram-bot qo'llab-quvvatlanadi)
python3 tools/meta-audience.py retargeting --aov 250 --daily-visitors 400 --ig-engagers 12000 --video-viewers 18000 --no-telegram-bot

# 6) Lookalike (LAL) Heuristic Seed Readiness Score (0-100) va 1%-5% pog'onali hajm hisobi
python3 tools/meta-audience.py lookalike --seed-size 1200 --seed-type purchase_ltv --country UZ

# 7) Jonli Meta Ads akkauntidan (Graph API v26.0 /act_<id>/insights) statistikalarni tortish va audit qilish
python3 tools/meta-insights-sync.py pull --account-id act_123456789 --level adset --date-preset last_7d --target-cpa 15
python3 tools/meta-insights-sync.py pull --from-raw-json examples/demo-brand/assets/meta_graph_insights_raw.json --target-cpa 15
```

## 🎨 3. Andromeda 2 Creative & Hook Studio (`tools/creative-matrix.py` · `/kreativ`)

```bash
# 3x3 Angle x Format kreativ sinov matritsasi + Uzum/Alif Nasiya narx ankori
python3 tools/creative-matrix.py matrix --niche ecom --product "Klassik erkaklar kostyumi" --price 160

# 3 tilda (O'zbek lotin, O'zbek kirill, Rus) 3 soniyalik Hook variantlari
python3 tools/creative-matrix.py hooks --niche edtech --offer "3 oyda IELTS 7.0 kafolati bilan"

# Hook Rate, Hold Rate va FTIR bo'yicha kreativ charchoq (Fatigue) diagnostikasi
python3 tools/creative-matrix.py fatigue --hook-rate 21.0 --hold-rate 14.5 --ctr-drop-pct 28.0 --frequency 2.9 --ftir 51.0
```

## 🗂️ 4. Mijoz Ish Maydoni Scaffolder (`tools/client-workspace.py` · `/mijoz`)

Yangi mijoz kelganda 1 ta buyruq bilan Break-even ROAS, Target CPA, 70/20/10 byudjet, 4-qatlamli Meta Auditoriya xaritasi va 3x3 Kreativ Matritsani o'z ichiga olgan tayyor ish maydonini yaratadi:

```bash
python3 tools/client-workspace.py new --client "nur-residence" --niche real-estate --budget 3000 --aov 45000 --margin-pct 25 --geo tashkent
```

## ⚡ 5. 18 ta Tezkor Slash Buyruq (`commands/`)

| Buyruq | Vazifasi |
|---|---|
| `/start` | Yangi sessiya yoki loyiha onboardingi (`MEMORY.md` + kontekst rejimi) |
| `/audit` | Meta, Google, Telegram, TikTok va b. bo'yicha 360° manbali akkaunt auditi |
| `/auditoriya` | Meta Ads 4-qatlamli auditoriya, Exclusion, Overlap (<20%), Saturation, LAL va Retargeting studiyasi |
| `/kreativ` | Andromeda 2 3x3 kreativ matritsa, 3 soniyalik Hook va Reels skriptlar |
| `/voronka` | Meta/TG Ads → ManyChat / Telegram Bot → Lead Magnet → AmoCRM voronka arxitektori |
| `/eksport` | Meta/Google CSV/JSON eksportlari, Graph API v26.0 Insights va Breakdown Effect tahlili |
| `/utm` | Meta CAPI v26.0 SHA-256 PII normalizatsiyasi, EMQ skoring va Telegram Bot (`<=64` belgi) UTM generatori |
| `/budget` | Break-even CPA/ROAS, Meta 1-5-5 Sandbox, Google Coliseum va Telegram voronka matematikasi |
| `/scale` | Kill / Keep / Scale qaror dvigateli, +20% byudjet qoidasi va Learning Phase himoyasi |
| `/raqobatchi` | Raqobatchilar va Meta Ads Library (Longevity, Hook, Offer, Funnel) tahlili |
| `/mijoz` | 1 buyruqda mijoz uchun tayyor `BRIEF`, `AUDIENCE-MAP`, `CREATIVE-MATRIX` yaratish |
| `/tracking` | Meta Pixel + CAPI (`event_id`), EMQ, GA4, GTM va Telegram Bot UTM tekshiruvi |
| `/hisobot` | Haftalik/oylik ROI, ROAS, ROMI, CAC va MER mijoz hisoboti |
| `/savol` | 100 ta wiki qayd va 9 ta playbook ichidan 0-token javob qidirish |
| `/sop` | 16 ta qadamma-qadam marketing va targetologiya SOP'larini chaqirish |
| `/learn` | Kampaniya saboqlarini `manifests/instincts.json` va `MEMORY.md` ga muhrlash |
| `/shield` | TyrionShield v5.0 6-qavatli statik xavfsizlik va AST skaneri |
| `/doctor` | Butun tizimning 14-nuqtali diagnostikasi |

## 🛠️ O'rnatish (Claude Code / Cursor / Codex / Windsurf)

```bash
# macOS / Linux
./install.sh

# Windows PowerShell
.\install.ps1
```
