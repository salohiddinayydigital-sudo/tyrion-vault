---
name: bosh-agent-protokoli
description: "\"Bosh agent yo'q\" muammosiga yechim — conductor kim, workerlar bilan chegara, plan approval, clean shutdown"
tags: [orkestratsiya, conductor, agents, protokol]
source: operator taqdim etgan CEO/orchestrator 4 tamoyili (2026-09-07) + ads/SKILL.md#Worker-orchestration tahlili
updated: 2026-09-07
---

# 🧭 BOSH AGENT (CONDUCTOR) PROTOKOLI

## Muammo

Repo'da 33 ta worker (`.claude/agents/`) bor, lekin operator ularni boshqaradigan
aniq "bosh agent"ni ko'rmaydi — natijada tizim "bor lekin tartibsiz" his qilinadi.

## Aslida bosh agent bor — u yashirin

`ads/SKILL.md` ning birinchi qatori: *"Act as the conductor for a source-grounded
paid-media operating system."* — ya'ni **asosiy Claude Code sessiyasining o'zi**
`/ads` skill yuklanganda conductor (bosh agent) roliga kiradi. Worker'lar hech
qachon bir-biri bilan ishlamaydi — faqat conductor ular bilan ishlaydi (`ads/SKILL.md`
§ Worker orchestration: "Use one conductor and bounded workers"). [🟢 FAKT — repo kodida yozilgan]

Muammo texnik emas — **ko'rinish** muammosi: bu rol hech qayerda operator uchun
ovoz chiqarib e'lon qilinmaydi. Pastdagi 5 ta tuzatish shu bo'shliqni yopadi.

## 5 tamoyil — moslashtirilgan holda

Operator taqdim etgan tamoyillar (video/kurs manbali, framework nomi noma'lum)
mavjud arxitekturaga solishtirildi:

### 1. Goal & Team Size — bor, kuchaytirildi
`ads/SKILL.md` Operating order #1 allaqachon talab qiladi: maqsad, byudjet,
platforma aniqlansin. **Qo'shimcha qoida:** conductor har fan-out oldidan bitta
qatorda e'lon qiladi — `Maqsad: <X> · Jamoa: <N worker, nomlari>`. Shu orqali
operator har safar "kim ishlayapti"ni ko'radi.

### 2. File Territory — allaqachon strukturaviy yechilgan
Video'dagi muammo (agentlar bir-birining faylini o'chirib yuborishi) bu repoda
umuman yuzaga kelmaydi, chunki **worker'lar fayl yozmaydi** — faqat schema-valid
`result` obyekti qaytaradi conductor'ga (`ads/SKILL.md`: *"workers never write the
final report"*). Fayl yozish huquqi FAQAT conductor'da (`.claude-ads/runs/<run-id>/`,
`journal/<mijoz>.md`, `outputs/`). "Fayl hududi" belgilash shart emas — kirish
huquqi arxitektura darajasida cheklangan. [🟢 FAKT]

### 3. Direct Messaging — ❌ QABUL QILINMADI
Sabab: Claude Code'dagi subagent (`Agent` tool) bir martalik chaqiriladi — ishni
bajaradi, natija qaytaradi, tugaydi. Ikki worker bir-biriga to'g'ridan-to'g'ri
xabar yubora olmaydi (bu qobiliyat shu harnessda yo'q). Video'dagi "direct
messaging" boshqa freymvork (masalan maxsus Agent SDK loop yoki ko'p sessiyali
tizim) uchun bo'lgan bo'lishi mumkin — bu yerga TO'G'RI KELMAYDI. [⚠️ FIKR]

Qaror: conductor-vositachi model saqlanadi (worker → conductor → worker), xuddi
`wiki/bosh-agent-protokoli.md` da tasdiqlangan patterndek. Bu qaror
**qat'iy** — qayta taklif qilinmasin, sabab shu yerda yozilgan.

### 4. Plan Approval Mode — kengaytirildi
Avval: faqat hisob o'zgarishida (`mutation gate`) draft+tasdiq bor edi
(`memory.md` §2 qoida 8). **Endi:** >1 worker fan-out qilinadigan HAR ishda
(masalan `/ads create`, `/ads launch`, `/ads optimize`) conductor avval qisqa
reja beradi — maqsad + jamoa + kutilayotgan chiqish fayllari — va operator
tasdig'ini kutadi. Faqat **audit/research** (`/ads audit`, `/ads research
refresh`) avtomatik davom etadi — ular hisobga yozmaydi, xavfsiz.

### 5. Clean Shutdown — yangi qo'shildi
Sessiya oxirida conductor tekshiradi:

- [ ] `.claude-ads/runs/<run-id>/` — manifest + barcha artefaktlar yozilganmi
- [ ] `journal/<mijoz>.md` — kill/keep/scale qarori sababi bilan yozilganmi (agar bo'lsa)
- [ ] Yangi saboq bo'lsa — `memory.md` §6 SABOQLAR darhol yangilanadi
- [ ] Kredensial/token/PII natija fayllarida yo'qligi tasdiqlangan
- [ ] Operator'ga qisqa yakun: nima qilindi, qayerda, keyingi qadam

## Yangi mijoz oqimi (avtomatik)

Operator "yangi mijoz: X" desa (yoki mijoz nomi birinchi marta chiqsa), conductor
**so'ramasdan** shu ketma-ketlikni bajaradi:

1. `journal/_SHABLON.md` dan nusxa → `journal/YYYY-MM-DD-<mijoz>.md` ochiladi
2. `outputs/<mijoz>/` papkasi ochiladi (kreativ, hisobot, eksport shu yerga tushadi —
   `outputs/README.md` qoida 4 endi **standart**, ixtiyoriy emas)
3. Shablondagi 6 savol so'raladi (mahsulot, maqsad, geo/til, destination, byudjet, CPL/CPA)
4. Vazifa turiga qarab kerakli worker(lar) va skill(lar) **o'zi** tanlanadi (§4 xarita,
   AVTO-SKILL qoidasi) — operator qaysi agent/skill kerakligini aytishi shart emas
5. >1 worker kerak bo'lsa — Plan Approval (yuqorida §4) ishga tushadi
6. Kampaniya tugaganda: jurnal xulosasi → `04_PROJECTS_&_CASES/` keys yozuviga,
   saboq → `memory.md` §6 ga ko'chadi (`journal/README.md` qoida 3)

## Tyrion miya bilan aloqa (scoped — token tejash uchun)

Conductor claude-ads-main'ga xos bo'lmagan, lekin marketing ishiga aloqador savolda
repo ildizi (vault ildizi) bilimiga murojaat qiladi — **faqat marketing-aloqador
notalarga**, butun vault skanerlanmaydi:

- `wiki/mijoz-ishga-tushirish.md` — media buying qoidalar kitobi + mijoz kuni SOP
- `wiki/meta-ads-*.md` — Meta Ads sozlamalari, kutubxona tadqiqoti, interest API
- Boshqa `wiki/*.md` (token-gigiyenasi, session-handoff va h.k.) — FAQAT ishning o'zi
  shu haqda bo'lsa (masalan sessiya boshqaruvi haqida savol)

Vault'ning bilim yo'q qismlarini (masalan avtomatika-darvoza mijozi, boshqa nisha)
claude-ads-main ishiga aralashtirmaydi — bu ikkalasi mustaqil kontekst.

## Xulosa

Bosh agent chaqirilishi shart bo'lgan **yangi fayl emas** — `ads/SKILL.md`
allaqachon shu rolni bajaradi. Yetishmayotgan narsa — **ko'rinuvchanlik**
(team e'loni) va **intizom** (plan approval + clean shutdown), ular yuqorida
qo'shildi. `ads/`, `.claude/agents/`, `agents/` — asl repo kodi — o'zgartirilmadi
(`CLAUDE.md` OPERATOR QATLAMI qoidasiga muvofiq); bu qoidalar operator qatlamida
(`memory.md` orqali) kuzatiladi.

---

**Bog'liq:** [[agent-os-qatlami]] · [[sub-agentlar]] · [[skill-router]] · [[token-gigiyenasi]]
