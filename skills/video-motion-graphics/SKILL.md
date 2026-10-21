---
name: video-motion-graphics
description: 'Animatsion (motion graphics) video ishlab chiqarish — After Effects darajasidagi sifat: kinetik tipografiya, shape/logo animatsiya, qatlamli parallaks, easing va timing intizomi, ovoz dizayni, kadr aniqligida (frame-accurate) render. Ishlatiladi: "animatsion video", "motion graphics", "kinetik tipografiya", "matn animatsiyasi", "logo animatsiya", "after effects uslubida", "explainer video", "infografika animatsiyasi", "animated ad". Chiqish — ffmpeg/Remotion bilan qayta ishga tushiriladigan skript va 9:16/1:1/16:9 render.'
triggers:
- animatsion
- animatsion video
- animatsion reels
- motion graphics
- kinetik
- kinetik tipografiya
- kinetic typography
- after effects
- remotion
- logo animatsiya
- logo reveal
- 2d animatsiya
- infografika video
- shape animation
- text animation
- explainer video
- dinamik matn
- motion design
- noldan video
- xom videom yo'q
- анимационное видео
- моушн графика
aliases:
- motion-design
- kinetic-typography
- remotion
- after-effects
domains:
- video
- animation
- creative
platforms:
- instagram
- tiktok
- youtube
- meta
attached_agents: [video-editor]
related_skills:
- video-editing
- reels-scripting
references:
- skills/video-motion-graphics/references/code-recipes.md
- skills/video-motion-graphics/references/qa-checklist.md
risk_level: low
output_contract: Motion graphics storyboard, keyframe/spring choreography, and render specification
---

# Animatsion video (motion graphics) — professional daraja

Maqsad: **"After Effects'da qilingan"** degan taassurot beradigan animatsion video —
kadr aniqligida, takrorlanadigan skript bilan, bir uslubda. Havaskor animatsiya
"harakat bor" bilan professional animatsiya **"harakat to'g'ri vaqtda, to'g'ri egri bilan,
kerak joyda to'xtaydi"** bilan farq qiladi: farq 90% **timing va easing**da, 10% effektda.

## 0. Kirish sharti — SKILL TALASH SO'ROVI (majburiy, birinchi qadam)

Ishni boshlashdan **oldin**:

1. E'lon qil (bir qator): `Skill so'rovi: "<vazifa kalit so'zlari>" · agent: video-editor`
2. Qidiruv (0 token, LLM'siz):
   `py -3 tools\skill-search.py brief "<vazifa>" --agent video-editor` (repo ildizidan)
3. Chiqqan **`fayl:`** yo'lini `Read` bilan o'qi va **faqat shu skill tartibi** bo'yicha ishla.
   `references/` ko'rsatilsa — kerak bo'lgan faylni ham o'qi (kod retseptlari/QA).
4. Mos skill topilmasa (exit 1) — **ish boshlamaydi**: conductor'ga `needs_input` qaytariladi.
   Taxminiy, skillsiz animatsiya yasaladi deb hech qachon aytilmaydi.

Vazifa "montaj/edit" bo'lsa — bu skill emas, `video-editing` skili (qidiruv o'zi topadi).

## 1. Topshiriq chegarasi (professional minimum)

| Talab | O'lchov |
|---|---|
| Kadr aniqligi | Har harakat butun kadrda boshlanadi/tugaydi (30 yoki 60 fps; "0.1s" emas — kadr soni yoziladi) |
| Qayta ishlab chiqarish | Natija `build.py` / `render.sh` + `props.json` bilan **noldan qayta** chiqadi |
| Bir uslub | 1 palitra (60-30-10), ≤2 shrift oilasi, 1 easing tizimi butun videoda |
| Ritm | Har 0.8–1.6s da e'tibor hodisasi (reveal, kesim, SFX); 2s dan ortiq "o'lik" kadr yo'q |
| Ovoz | Musiqa royalty-free + SFX harakat bilan sinxron; miks −14 LUFS / TP −1.0 dBTP |
| Auditoriya | Ovozsiz ham tushunarli (yopishqoq matn/subtitr), 9:16 da mobil o'qiladi |
| Huquq | Har asset MANIFEST'da: manba URL + litsenziya; watermark/brend logotipli stock taqiqlanadi |

## 2. Vosita darajalari (qaysi biri qachon)

| Daraja | Vosita | Qachon | Holat (tekshirilgan) |
|---|---|---|---|
| **1 — default** | `ffmpeg` 8.1.2 + Python 3 (numpy, Pillow) | 80% ish: harakat, matn, o'tish, rang, ovoz, eksport | ffmpeg/ffprobe `PATH`da; numpy/Pillow bor |
| **2 — sahna-asosli** | Remotion 4.x (React, Node 18+) | Ko'p sahnali, ma'lumotdan quriladigan, komponent qayta ishlatiladigan video | **tekshirilgan**: render ishlaydi; namuna `output/reels-google-vs-meta/` |
| **3 — asset** | Higgsfield/Veo/Kling (AI generatsiya) | B-roll, fon, atmosfera kadrlari | API kalit bo'lmasa `needs_input` ([[video-kreativ-tizimi]] §7) |
| **3b — 3D/tracking** | Blender CLI, OpenCV (`pip install opencv-python`) | 3D obyekt, harakat tracking | Hozir **yo'q** — o'rnatish alohida tasdiqlanadi |

Qoida: qaysi daraja ishlatilsa, MANIFEST'da versiya yoziladi (`ffmpeg 8.1.2`, `node 22.x`).
O'rnatilmagan vositani "ishlatildi" deb yozish — taqiqlanadi.

## 3. Motion til — timing va easing (sifat shu yerda)

### 3.1 Davomiylik jadvali (30 fps; 60 fps da ×2)

| Harakat | Kadr | Vaqt |
|---|---|---|
| Mikro-reaktsiya (tugma, belgi, tick) | 4–6 | 130–200 ms |
| Matn kirishi — so'z | 8–12 | 270–400 ms |
| Matn kirishi — blok | 12–18 | 400–600 ms |
| Sahna o'tishi | 15–20 | 500–670 ms |
| Katta reveal (logo, narx, CTA) | 24–40 | 800–1300 ms |
| **Chiqish (exit)** | kirishning **60–70%** | chiqish doim tezroq |
| Hook matni ushlab turish | ≥ 24 | ≥ 0.8 s |
| CTA ekranda turish | ≥ 60 | ≥ 2 s |

### 3.2 Easing egri chiziqlari (nom → cubic-bezier → qayerda)

| Egri | cubic-bezier | Ishlatilishi |
|---|---|---|
| `ease-out-quint` | `0.22, 1, 0.36, 1` | Default kirish — 90% harakat shu |
| `ease-out-expo` | `0.16, 1, 0.3, 1` | Katta reveal, narx/son paydo bo'lishi |
| `ease-in-out-quart` | `0.76, 0, 0.24, 1` | Sahna/slayd o'tishi, kamera push-in |
| `ease-out-back` | `0.34, 1.56, 0.64, 1` | "Pop" — overshoot ≤6%, faqat kichik elementda |
| `ease-in-cubic` | `0.32, 0, 0.67, 0` | Chiqish, sahna tark etilishi |
| `linear` | — | **Faqat**: aylanish, progress, yuklanish, fon parallaksi |

- `linear` harakat kirish/chiqishda = **havaskor belgisi** (mashina hissi). Easing yo'q harakat topshirilmaydi.
- Bezier — AE `Easy Ease`/`Speed Graph` ning matematik ekvivalenti; ffmpeg'da formula bilan yoziladi
  (`references/code-recipes.md` §1: `1-pow(1-t,3)` = ease-out-cubic).
- Overshoot 6% dan oshsa — "sakrayotgan" ko'rinadi; spring fizikasi kerak bo'lsa damping’ni
  tanlang, tayyor bezier'ni buzib cho'zmang.

### 3.3 Stagger va ustuvorlik

- Ketma-ket elementlar: **so'z 2–3 kadr**, harf 1–2 kadr oraliqda (8 so'zdan ko'p matn — qator-qator).
- Bir vaqtda harakatlanadigan element ≤3. Ko'p element — sahna "qaynaydi", e'tibor nuqtasi yo'qoladi.
- Harakat ierarxiyasi: asosiy element (hook/logo) **birinchi va sekinroq**, ikkinchi darajali tezroq va kichikroq.
- Motion blur: tezlik ~20 px/kadrdan oshsa (180° shutter ekvivalenti); sekin harakatda blur qo'yilmaydi.

### 3.4 Qatlam va chuqurlik (parallaks)

3 qatlam: **fon** (gradient/gradient-mesh), **o'rta** (b-roll, shakl), **old** (matn, aksent).
Parallaks koeffitsienti: `0.85 / 1.00 / 1.15–1.25`. Uzoq qatlamga: 0.5–1.5 px blur,
10–15% kontrast pasaytirish, 3–6% grain — "havo perspektivasi". Old qatlamga aksent rang.
Kamera: push-in 3–5% / 1.5 s, whip-pan 6–10 kadr (faqat mazmun o'zgarganda),
dolly-zoom va "effekt uchun effekt" taqiqlanadi.

## 4. Kompozitsiya va tipografiya (9:16 asos, 1080×1920)

- **Safe-zone:** yuqori 12% va pastki 20–25% bo'sh (platforma UI), o'ng 12–15% (tugmalar).
  Muhim matn faqat markaziy 70%×60% to'rtburchakda.
- **Marja:** 6–8% (65–86 px). Matn kadr chetiga tekkan bo'lsa — nuqson.
- **Tipografik shkala:** hook 90–140 px · subtitle 56–72 px · caption 44–56 px · legal 32–36 px.
- **O'qiluvchanlik:** qator ≤28 belgi, ≤2 qator; kontrast ≥4.5:1 (WCAG AA); yopishqoq matnga
  plashka (`box=1:boxcolor=black@0.35`) yoki kontur (`Outline=3–4`).
- **Shrift:** ≤2 oila (sarlavha + tana). Brend shrifti bo'lsa — faqat u. Shrift **lokal fayl**
  sifatida ishlatiladi (`C:/Windows/Fonts/arial.ttf`), internetdan yuklanmaydi (render nomuvofiq bo'ladi).
- **O'zbek apostrofi:** `oʻ`, `gʻ` uchun U+02BB ishlatiladi; Windows core shriftlari
  (Arial, Segoe UI, Calibri, Tahoma, Verdana, Times, Georgia) uni qoplaydi — **tekshirilgan**.
  Noto'g'ri `o'` (U+0027) matnni professional emas ko'rsatadi.
- Kinetik tipografiya: so'z bo'yicha animatsiya (harf emas) — o'qish tezligiga mos;
  satr almashinuvi matn tugagandan keyin ≥6 kadr.

## 5. Rang va yorug'lik

Tartib (buzilmaydi): **ekspozitsiya → white balance → kontrast (`curves`) → saturatsiya → LUT → grain/vignette**.
- 1 video = 1 palitra (60-30-10) va **1 LUT/curve**; aralash uslub (bir kadr iliq, keyingisi sovuq) — nuqson.
- Saturatsiya "telefonda tabiiy" chegarasida; teri rangi tabiiy; neon/oversaturated — arzon signal.
- Banding ko'rinsa — grain (`noise=alls=4:allf=t`) bilan yopiladi, kontrastni ko'tarish bilan emas.
- Brend kit bo'lmasa palitra konteynerdan so'raladi (`needs_input`); taxmin qilinsa — "gipoteza" deb belgilanadi.

## 6. Ovoz dizayni (professional animatsiyaning yarmi)

- **Beat map:** musiqa BPM → beat kadrlari; kesim va landing'lar beat'da (30 fps: `60/BPM*30` kadr).
- **SFX harakatga bog'lanadi:** whoosh harakatdan **6–8 kadr oldin**, impact **qo'nish kadrida**,
  riser reveal'dan 1–1.5 s oldin. Tasodifiy SFX — nuqson.
- Har 0.8–1.6 s da bitta e'tibor hodisasi (30 s videoda ≥12 SFX nuqtasi).
- **Miks:** VO −16…−18 LUFS · musiqa VO ostida (ducking −12…−18 dB) · SFX peak −6 dBFS ·
  final **−14 LUFS, TP −1.0 dBTP** (o'lchov: `references/qa-checklist.md`).
- Musiqa: royalty-free (platforma kutubxonasi yoki erkin manba) — litsenziya MANIFEST'da.
  Litsenziyasiz tijorat trek — taqiqlanadi.

## 7. Ish tartibi — 7 faza, har fazada darvoza

| # | Faza | Chiqish | Darvoza (o'tmasa keyingisiga o'tilmaydi) |
|---|---|---|---|
| 1 | Brief | 1 varaq: maqsad, auditoriya, offer, format, joylashtirish | Format va spec **registry'dan** olingan, yoddan emas |
| 2 | Skript | hook (0–3 s) → tana → CTA, kadr jadvali bilan | Hook ovozsiz tushunarli; da'volar manbali |
| 3 | Storyboard | Kadr-kadr jadval: kadr #, davomiylik, harakat, matn, SFX | Har kadrda yagona e'tibor nuqtasi |
| 4 | Animatic | Past sifatli draft (matn + vaqt + ovoz) | Ritm to'g'ri: 2 s o'lik kadr yo'q |
| 5 | Build | `props.json` + `build.py`/Remotion komponentlari + `theme` (rang/shrift/easing) | Barcha qiymatlar kadrda, sehrli son yo'q |
| 6 | Render | Draft → final (spec bo'yicha) | QA ro'yxati (quyida) to'liq o'tadi |
| 7 | Topshirish | Render + MANIFEST + QA natijasi | Hash, litsenziya, spec manbasi yozilgan |

Ish maydoni: **standart buyruq bilan ochiladi** —
`py -3 tools\video-run.py new --client <mijoz> --topic "<mavzu>" --format 9x16`
(`assets/`, `renders/`, `build.py`, `props.json`, `MANIFEST.md`, `qa.md`; mavjud fayl ustiga yozilmaydi).
Uni `.claude-ads/runs/<run_id>/workers/video-editor/` ichida to'ldiriladi; animatsion sahnani
Remotion loyihasi sifatida qursa — loyiha ham shu papkada turadi. Kanonik papkalarga yozilmaydi;
hech narsa o'chirilmaydi (eskisi `_archive/` ga).
Conductor tasdiqlagan yakuniy fayl `outputs/<mijoz>/` ga nusxalanadi.

## 8. Render va eksport

- **Kadr aniqligi:** kadr soni butun; `fps_mode cfr` (VFR chiqarilmaydi); davomiylik
  `kadr / fps` bilan tekshiriladi (`-shortest` bilan).
- **Intermediate:** grading/ko'p qatlam kerak bo'lsa `prores_ks` (`.mov`) yoki PNG ketma-ketlik;
  yakuniy tarqatish — H.264 High, `yuv420p`, `-g 60` (2 s keyframe), `-movflags +faststart`.
- **Spec registry'dan:** o'lcham/bitrate/davomiylik chegarasi `ads/references/creative-source-registry.md`
  orqali; vertikal 1080×1920 odatda ~10–12 Mbps, AAC 192 kbps. Yoddan yozilmaydi.
- Draft tez: `-preset veryfast -crf 24 -s 540x960`; final: `-preset slow -crf 17–18`.
- Render **skript** ko'rinishida saqlanadi (bir martalik buyruq emas) — `build.py`/`render.sh`.

## 9. Tekshiruv (topshirishdan oldin — avtomatik + ko'z bilan)

Avtomatik (buyruqlar: `references/qa-checklist.md`):
- [ ] Kadr soni va davomiylik mos: `ffprobe -count_frames` → `nb_read_frames / fps = duration`
- [ ] CFR: `r_frame_rate == avg_frame_rate` (VFR emas)
- [ ] Qora kadr / muzlagan kadr yo'q: `blackdetect`, `freezedetect`
- [ ] Ovoz jimligi kutilmagan joyda yo'q: `silencedetect`
- [ ] Miks: `loudnorm` o'lchovi → I ≈ −14 LUFS, TP ≤ −1.0 dBTP
- [ ] Subtitr/plashka safe-zone ichida (kadr chiqarib ko'riladi)

Ko'z bilan (1× tezlikda, ovoz bilan va ovozsiz):
- [ ] Harakat kerak joyda **to'xtaydi**; linear "mashina" harakati yo'q
- [ ] Har kadrda 1 e'tibor nuqtasi; matn kadr chetiga tekkan emas
- [ ] SFX harakat bilan bir kadrda; musiqa-VO muvozanati
- [ ] O'zbekcha matn imlosi (apostrof U+02BB), raqamlar to'g'ri
- [ ] Oxirgi kadrda CTA ≥2 s turadi va takror ko'rsatilganda (loop) boshi bilan mos

Buzilish bo'lsa — tuzatib **qayta render**; "keyin tuzatamiz" deb topshirilmaydi ([[50-topshirish-dod]]).

## 10. Havaskor ko'rinadigan xatolar (taqiq ro'yxati)

1. Linear kirish/chiqish; easing yo'q harakat.
2. Bir vaqtda 4+ element harakati, hammasi bir xil tezlikda.
3. 3+ shrift oilasi, 5+ rang, palitrasiz "rang-barang" video.
4. Zoom + rotate + dissolve bir vaqtda (uch effekt bir harakatda).
5. Matn kadr chetida yoki platforma UI zonasi ostida.
6. Harakat 6 kadrdan qisqa (o'qib ulgurilmaydi) yoki 2 s dan uzun (zerikarli).
7. Effekt "qiziq bo'lsin" uchun: glitch/whip/dissolve mazmunsiz.
8. Banding, keskin oversaturatsiya, ko'tarilgan sharpening halo.
9. Ovoz: SFX harakatdan keyin/oldin, musiqa VO'ni bosib ketadi, desync >1 kadr.
10. Sessiyada qo'lda tuzatilgan, skriptda qayta tiklanmaydigan natija.

## 11. O'zbekiston bozori xususiyatlari

- 90%+ trafik mobil: 9:16 default, matn katta va qisqa; gorizontal versiya keyin ([[ozbekiston-konteksti]]).
- Ishonch signallari dastlabki 2–3 s da: real jamoa/mijoz kadri, raqam, manzil, telefon.
- CTA — **Telegram** ("Telegramda yozing"); ekranda aniq ko'rinadi; email CTA ishlatilmaydi.
- Til segmentlari: o'zbek-lotin / o'zbek-kirill / rus — har biri **alohida yoziladi**, tarjima emas.
- Ssenariyda isbotsiz va'da, "eng yaxshi", raqamsiz da'vo bo'lmaydi ([[video-kreativ-tizimi]] §8).
- Real suratga olingan material stock'dan ustun — stock faqat atmosfera/b-roll ([[video-kreativ-tizimi]]).

## 12. Manbalar

- `references/code-recipes.md` — tekshirilgan ffmpeg/Remotion retseptlari (easing, push-in, matn, o'tish, miks)
- `references/qa-checklist.md` — topshirish darvozasi: buyruqlar va o'lchovlar
- `wiki/video-kreativ-tizimi.md` · `wiki/video-skript-shablonlari.md` (vault ildizi, `wiki/`)
- `wiki/kreativ-sikl.md` · `wiki/kreativ-hit-rate.md` · `wiki/funnel-2-kreativ-format.md`
- `local/ozbekiston-konteksti.md` · `../ozbekiston-konteksti.md`
- `ads/references/creative-source-registry.md` (spec — yoddan emas)
- `../wiki/sifat-darajasi.md` · `../wiki/dalil-tasnifi.md` (da'vo tasnifi: FAKT/TAJRIBA/FIKR/REKLAMA)
