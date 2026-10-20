---
name: skill-router
description: "Skill router — agent ishni boshlashdan oldin 'skill talash so'rovi' chiqaradi va faqat o'ziga ulangan skill bo'yicha ishlaydi; ulanish frontmatter orqali, tekshiruv tools/skill-search.py bilan"
tags: [skill, agent, router, protokol]
source: "2026-09-21 Tyrion ishi (video-editor + 2 skill); tools/skill-search.py sinovlari"
updated: 2026-09-21
---

# Skill router (agent ↔ skill ulash protokoli)

> Bog'lanishlar: [[sop-xarita]] · [[20-token-gigiyena]] · [[AGENTS.md]] · [[50-topshirish-dod]]

## Muammo

Skill papkalari 4 xil joyda yotadi (`skills/`, `.agents/skills/`,
`.claude/skills/`, `.hermes/skills/`) va **qaysi skill qaysi agentga ulanganligi hech qayerda
yozilmagan** edi. Natijada agent ishni "eslab qolgan" uslubda boshlardi: mos skill bor bo'lsa ham
yuklanmasdi, ikki agent bir xil ishni har xil tartibda qilardi.

## Yechim — ikki tomonlama ulanish (attach)

```yaml
# skill: skills/video-editing/SKILL.md
attached_agents: [video-editor]
triggers: [montaj, edit qil, kesib ber, ...]     # qidiruv kuchaytirgichi

# agent: agents/video-editor.md
skills: [video-editing, video-motion-graphics]
```

`tools/skill-search.py check` ikki tomonni solishtiradi: skillda `attached_agents` bor-u agentda
`skills:` yo'q bo'lsa (yoki fayl umuman yo'q bo'lsa) — **uzilgan ulanish** deb xato qaytaradi.
Sabab: bir tomonlama ulanish jim buziladi — skill yangilanadi, agent uni topmaydi, ish skillsiz
davom etadi va buni hech kim sezmaydi.

## Ish tartibi (agent uchun majburiy 0-qadam)

1. E'lon: `Skill so'rovi: "<vazifa>" · agent: <nom>`
2. Qidiruv (0 token, LLM'siz, ish papkasi `D:/tyrion`):
   `py -3 tools\skill-search.py brief "<vazifa>" --agent <nom>`
3. Chiqqan `fayl:` yo'lidagi `SKILL.md` o'qiladi va **faqat shu tartib** bo'yicha ishlanadi
   (`qo'shimcha:` ko'rsatgan `references/*.md` — kerak bo'lganda).
4. Mos skill topilmasa (chiqish kodi 1) — **ish boshlanmaydi**: conductor'ga `needs_input`
   qaytariladi. Skillsiz taxminiy ish — taqiqlanadi.

Nega so'rov **chiqariladi**: qidiruv natijasi ko'rinib turadi — conductor va foydalanuvchi qaysi
skill bo'yicha ishlanayotganini biladi; xato routing darhol seziladi.

## Buyruqlar

| Buyruq | Nima qiladi |
|---|---|
| `skill-search.py brief "<vazifa>" --agent <nom>` | agentga ulangan skilllardan eng mosini tanlaydi (so'rov bloki + `fayl:`) |
| `skill-search.py agent <nom>` | agentga ulangan skilllar ro'yxati (ulanishni tekshirish) |
| `skill-search.py search "<vazifa>"` | butun reyestr bo'ylab qidiruv (agent tanlanmagan holat) |
| `skill-search.py list [--layer operator]` | reyestr ko'rinishi |
| `skill-search.py check` | ikki tomonlama ulanish + frontmatter nazorati (doctor ham chaqiradi) |
| `skill-attach.py set <skill> --agents <agent...>` | **ulash** — ikki tomonni ham yozadi (`--dry-run` bilan sinab ko'rish mumkin) |
| `skill-attach.py set <skill> --standalone` | agentsiz skill (konduktor darajasidagi skill, masalan `tyrion`) |
| `skill-attach.py remove <skill> --agent <nom>` | bitta agentdan uzish |
| `skill-attach.py list` | operator skilllar va ularning agentlari |

Chiqish kodlari: `0` — topildi/butun · `1` — topilmadi yoki uzilgan ulanish · `2` — argument xatosi.

Qidiruv vazni: nom (8) → trigger butun so'z (8) → trigger qismi (4) → tavsif (3) → tana (≤2.5),
so'ng **IDF** ko'paytmasi — reyestrda ko'p skillda uchraydigan so'z ("reels", "video") kamroq,
faqat bittasiga xos so'z ("animatsion", "kinetik") ko'proq vazn beradi. Sabab: regressiyada
"animatsion reels yasab ber" so'rovi `video-editing` ga ketib qolgan edi ([[50-topshirish-dod]]).

## Joriy holat (2026-09-21)

- **21 operator skill:** 20 tasi agentga ulangan, 1 tasi `standalone` (`tyrion` — konduktor darajasi).
- **13 agent** skill oladi: `video-editor` (2) · `copy-writer` (4) · `campaign-ideator` (2) ·
  `research-worker` (2) · `seo-auditor` (2) va boshqalar.
- **33 platforma skill** (`skills/ads-*`) ulanish talab qilmaydi — ularni
  `ads/SKILL.md` orchestration routeri boshqaradi.
- Nazorat: `py -3 tools\doctor.py` → "Skill reyestri" qatori (ulanishlar soni va uzilishlar).

## Qoidalar

- **Nusxa emas, havola:** agent charterida skill mazmuni takrorlanmaydi — faqat ulanish yoziladi.
- Yangi skill qo'shilsa: papka `SKILL.md` bilan + `attached_agents` + agentda `skills:` + `check` o'tishi.
- Skill tavsifi (`description`) va `triggers` — qidiruv sifati shu yerga bog'liq; erkin tarzda
  "after effects", "montaj qil" kabi **foydalanuvchi aytadigan so'zlar** yoziladi.
- Har ish oxirida: `py -3 tools\skill-search.py check` va `py -3 tools\doctor.py` — skill qatlami
  sog'ligi boshqa qatlamlar kabi nazoratda ([[50-topshirish-dod]]).

## Bog'liq

- Kanonik agent shartnomasi: [[AGENTS.md]] §2 (Skill router qatori), §6 (ish tartibi), §7 (tekshiruv)
- Operator xotirasi: `MEMORY.md` §2 qoida 10, §4 avto-skill xaritasi
- Misol: `agents/video-editor.md` → `.agents/skills/video-editing`, `.agents/skills/video-motion-graphics`
