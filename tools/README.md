---
name: tools-readme
description: Tyrion asboblari — har biri nima qiladi, qachon ishlatiladi (yagona jadval)
tags: [tools, asboblar, index]
source: "2026-09-16 ECC naqshi asosida qurilgan qatlam"
updated: 2026-09-16
---

# 🛠 TYRION ASBOBLARI

> Hammasi Python 3 + stdlib (faqat `PyYAML` ixtiyoriy — bor bo'lsa YAML qat'iy tekshiriladi).
> Har skript `--help` beradi; xato bo'lsa chiqish kodi 0 emas (avtomatlashtirishga yaroqli).

## Kundalik

| Asbob | Buyruq | Nima qiladi |
|-------|--------|-------------|
| **doctor** | `py -3 tools\doctor.py` | Butun tizim sog'lig'i: bilim, katalog, drift, botlar, graf, sirlar, testlar — bitta hisobot |
| **meta-audience** | `py -3 tools\meta-audience.py architect / interests / overlap / saturation` | **Meta Ads Audience Engine**: 4-qatlamli voronka, 8 nisha Interest/Solventnost filtri, Overlap va Saturation hisobi |
| **catalog** | `py -3 tools\catalog.py summary` | Tizimda nima bor (qayd, agent, skill, bot, asbob) — fayl tizimidan generatsiya |
| **brain-search** | `py -3 tools\brain-search.py search "so'z"` | **LLM'siz, 0 token** bilim qidiruvi — grafdan **oldin** shu |
| **skill-search** | `py -3 tools\skill-search.py brief "<vazifa>" --agent <nom>` | **0 token** skill routeri — agent ishini boshlashdan oldin unga ulangan skillni topadi |
| | `py -3 tools\skill-search.py agent <nom>` · `search "<vazifa>"` · `list` · `check` | agentga ulangan skilllar · qidiruv · butun reyestr · ulanish butunligini tekshirish |
| **skill-attach** | `py -3 tools\skill-attach.py set <skill> --agents <agent>` | Skill'ni agentga ulash — **ikki tomonlama** frontmatter (`attached_agents:` ↔ `skills:`), `--dry-run` bilan, idempotent |
| | `py -3 tools\skill-attach.py list` · `remove` · `set <skill> --standalone` | Ulanishlar ro'yxati · bitta agentdan uzish · agentsiz (konduktor) skill |
| **video-run** | `py -3 tools\video-run.py new --client <m> --topic "<mavzu>" --format 9x16` | Video ishi uchun **ish maydoni** (scaffold): `assets/ renders/ build.py props.json MANIFEST.md qa.md` — standart tuzilma, mavjudini ustiga yozmaydi |
| | `py -3 tools\video-run.py list` · `status <run_id>` · `new --force` | Run'lar ro'yxati · nima bor/nima yetishmayapti · skeletlarni yangilash (eskisi `_archive/`) |
| **brain-graph** | `py -3 tools\brain-graph.py build` | Grafni wikilinklardan quradi (**0 token, lahzali**) — graf eskirmaydi |
| **gy.cmd** | `tools\gy.cmd query "savol" --budget 1200` | Bilim grafidan javob (munosabat kerak bo'lganda) |

## Tekshiruv

| Asbob | Buyruq | Nima qiladi |
|-------|--------|-------------|
| **vault-audit** | `py -3 tools\vault-audit.py [--gate\|--write]` | Bilim qatlami: frontmatter, YAML, wikilink, orphan, Delivery Gate (`--gate`) va INDEX auto-fix (`--write`) |
| **tyrion-shield** | `py -3 tools\tyrion-shield.py scan` | **ECC AgentShield analogi**: sirlar (.env), hook/MCP, 36 agent Prompt Defense va 62 skill tekshiruvi |
| **instincts** | `py -3 tools\instincts.py list / add / promote / check` | **ECC Continuous Learning (`/learn`)**: tasdiqlangan marketing instinktlari reestri |
| **catalog check** | `py -3 tools\catalog.py check` | Katalog haqiqatga mos keladimi (farq bo'lsa xato kodi) |
| **catalog drift** | `py -3 tools\catalog.py drift` | Nusxalar kanonikdan farq qiladimi (agent/buyruq) |
| **hook dod** | `py -3 hooks\tyrion-hook.py dod` | Topshirish darvozasi: doctor + ingest, faqat deterministik dalil |
| **skill-search check** | `py -3 tools\skill-search.py check` | Skill ↔ agent ulanishi ikki tomonlama butunmi (uzilgan ulanish = xato kodi) |
| **testlar** | `py -3 -m unittest discover tests -v` | Asboblar uchun testlar |

## Tuzatish

| Asbob | Buyruq | Nima qiladi |
|-------|--------|-------------|
| **catalog build** | `py -3 tools\catalog.py build` | `manifests/catalog.json` ni qayta yozadi |
| **catalog sync-mirrors** | `py -3 tools\catalog.py sync-mirrors` | Nusxalarni kanonikdan qayta quradi (eskisi `archive/` ga) |
| **catalog sync-claims** | `py -3 tools\catalog.py sync-claims` | Hujjatlardagi raqamlarni katalogga moslashtiradi |
| **install-hooks** | `py -3 tools\install-hooks.py [--dry-run]` | Hook va buyruqlarni `.claude/` ga o'rnatadi (mavjudlarini o'chirmaydi) |

## Botlar

| Asbob | Buyruq | Nima qiladi |
|-------|--------|-------------|

## Qoida

1. **Kanonik manba bitta** — `catalog.py` doim fayl tizimini o'qiydi, qo'lda yozilgan ro'yxatga ishonmaydi.
2. **Nusxa qo'lda tahrirlanmaydi** — `.claude/agents/`, `.claude/commands/` generatsiya/ko'chirish natijasi.
3. **Hech narsa o'chirilmaydi** — eski nusxa `archive/` ga ko'chiriladi.

