---
name: web-design-guidelines
description: Review UI code for Web Interface Guidelines compliance. Use when asked to "review my UI", "check accessibility", "audit design", "review UX", or "check my site against best practices".
triggers:
- ui dizayn
- ux audit
- web design
- vizual iyerarxiya
- accessibility
- дизайн сайта
- интерфейс
aliases:
- ui-ux
- web-ui
- design-system
domains:
- design
- web
- cro
platforms:
- web
attached_agents: [visual-designer]
related_skills:
- cro
- ads-landing
- ads-generate
references: []
risk_level: low
output_contract: UI/UX visual hierarchy, accessibility, and mobile conversion layout critique
---

# Web Interface Guidelines

Review files for compliance with Web Interface Guidelines.

## How It Works

1. Fetch the latest guidelines from the source URL below
2. Read the specified files (or prompt user for files/pattern)
3. Check against all rules in the fetched guidelines
4. Output findings in the terse `file:line` format

## Guidelines Source

Fetch fresh guidelines before each review:

```
https://raw.githubusercontent.com/vercel-labs/web-interface-guidelines/main/command.md
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

> Manba: `https://raw.githubusercontent.com/vercel-labs/web-interface-guidelines/main/command.md` — WebFetch yuklandi (2026-09-04). To'liq audit uchun hali ham yuqoridagi URL'dan yangi qoidalar yuklanadi; quyida manbadagi eng muhim qoidalarning offline xulosasi.

1. Ikonali tugmalar `aria-label` talab qiladi; forma kontrollari `label` yoki `aria-label`ga ega bo'ladi (manba: Accessibility)
2. Harakatlar uchun `<button>`, navigatsiya uchun `<a>`/`<Link>` — `<div onClick>` taqiq; semantik HTML ARIA'dan oldin (manba: Accessibility)
3. Rasmlar `alt` oladi (dekorativ bo'lsa `alt=""`); dekorativ ikonalar `aria-hidden="true"` (manba: Accessibility)
4. Sarlavhalar ierarxik `<h1>`–`<h6>`; asosiy kontentga skip-link; async yangilanishlar (toast/validation) `aria-live="polite"` (manba: Accessibility)
5. Interaktiv elementlarda ko'rinadigan fokus: `focus-visible:ring-*`; `outline: none` o'rnini to'ldirmasdan qo'yilmaydi; `:focus-visible` — `:focus` emas (manba: Focus States)
6. Inputlarda `autocomplete` va ma'noli `name`; to'g'ri `type` (`email`, `tel`, `url`) va `inputmode` (manba: Forms)
7. Paste bloklash taqiq (`onPaste` + `preventDefault`); label bosiladigan bo'ladi (`htmlFor`); email/kod maydonlarida `spellCheck={false}` (manba: Forms)
8. Forma xatolari input yonida inline ko'rsatiladi; submit'da birinchi xatoga fokus; yuklanishda spinner, tugma ishga tushguncha disabled (manba: Forms)
9. `prefers-reduced-motion` hurmat qilinadi; faqat `transform`/`opacity` animatsiya; `transition: all` taqiq — xossalar aniq yoziladi (manba: Animation)
10. `...` emas `…`; to'g'ri tirnoq `“ ”`; sonlar/taqqoslashda `font-variant-numeric: tabular-nums`; sarlavhalarda `text-wrap: balance` (manba: Typography)
11. Uzun kontent: `truncate`, `line-clamp-*`, `break-words`; flex bolalarda `min-w-0`; bo'sh holatlar (empty states) buzilgan UI ko'rsatmaydi (manba: Content Handling)
12. `<img>`da aniq `width`/`height` (CLS oldini oladi); pastki rasmlar `loading="lazy"`, tepadagi kritik rasm `priority`/`fetchpriority="high"` (manba: Images)
13. Katta ro'yxatlar (>50 element) virtualizatsiya qilinadi; render paytida layout o'qish (`getBoundingClientRect` va b.) taqiq (manba: Performance)
14. URL holatni aks ettiradi (filter, tab, pagination); destruktiv amallarda tasdiqlash yoki undo oynasi — hech qachon darhol bajarmaslik (manba: Navigation & State)
15. `touch-action: manipulation`; modal/drawer/sheetlarda `overscroll-behavior: contain`; imo-ishora (gesture) faqat emas — tap/click va klaviatura muqobili kerak (manba: Touch & Interaction)
16. Full-bleed layoutda notch uchun `env(safe-area-inset-*)`; dark mode uchun `color-scheme: dark`; `meta theme-color` fon rangiga mos (manba: Safe Areas & Layout, Dark Mode)
17. Sana/vaqt/raqam/pul: `Intl.DateTimeFormat`/`Intl.NumberFormat` — hardcode format taqiq; til `Accept-Language` orqali (manba: Locale & i18n)
18. Tugmalarda `hover:` holati; kontrast interaktiv holatda oshadi; copy: aktiv voz, xato xabari yechim bilan, ikkinchi shaxs (manba: Hover & Interactive States, Content & Copy)
19. `user-scalable=no`/`maximum-scale=1` (zoom o'chirish) — anti-pattern, taqiqlanadi (manba: Anti-patterns)
20. Inputda `value` bo'lsa `onChange` kerak (yoki uncontrolled `defaultValue`); hydration mismatchdan saqlanish (manba: Hydration Safety)

---

## Operator qatlami (Tyrion lokal bilimi)

> Bu bo'lim — Tyrion (Saloxiddin, O'zbekiston targetolog agentligi) uchun lokal moslashuv. Vendor metodika o'zgarishsiz.

### Qachon ishlatiladi (UZ triggerlari)
- "landing UI kodini tekshir" · "sayt/landing audit qil" · "mobil ko'rinishda muammo" · "accessibility tekshir" · "forma/pixel ishlashini tekshir"

### UZ amaliyot qoidalari (manbalardan)
1. Audit mobil birinchi boshlanadi: trafikning 90%+ telefondan — viewport, forma o'lchami, CTA bosilishi va vertikal kreativ tekshiriladi (manba: `local\ozbekiston-konteksti.md` §7.5)
2. Ishonch signallari birinchi ekranda: jonli telefon/manzil, real jamoa suratlari, video-sharhlar hero'da 2–3 soniyada ko'rinishi shart (manba: `local\ozbekiston-konteksti.md` §4, §7.4)
3. Asosiy CTA — Telegramga: "Telegramda yozish" konversiyasi email'dan yuqori; tugma/bot havolasi qulay joyda va ishlaydigan bo'lishi tekshiriladi (manba: `local\ozbekiston-konteksti.md` §1–2; `local\meta-playbook-uz.md` §7)
4. To'lov bloki tekshiruvi: Payme/Click/Uzum ko'rsatilsa — havolalar haqiqiy; xalqaro karta hamma joyda ishlamaydi, "onlayn to'lov" va'dasi asossiz bo'lmasin (manba: `local\ozbekiston-konteksti.md` §5)
5. Forma + tracking: Pixel/CAPI'da Lead va Schedule hodisalari test lead bilan o'lchanganmi; landing jonli va forma yuboryaptimi — preflight ro'yxatidan (manba: `wiki/mijoz-ishga-tushirish.md` §0; `wiki/meta-ads-sozlamalari.md`)
6. Til gigiyenasi: bitta sahifada o'zbek-lotin/kirill/rus aralashmaydi; matn segmentga mos toza tilda (manba: `local\ozbekiston-konteksti.md` §3)

### Bog'liq lokal fayllar
- `local\ozbekiston-konteksti.md` — mobil ulush, ishonch, to'lov (repo ildizi)
- `local\meta-playbook-uz.md` — metrikalar zanjiri (sahifa muammosini topish)
- `wiki/meta-ads-sozlamalari.md` va `wiki/mijoz-ishga-tushirish.md` — vault (`wiki`): Pixel hodisalari, preflight checklist
- `ads\references\meta-audit.md` — landing/reklama audit mezonlari
