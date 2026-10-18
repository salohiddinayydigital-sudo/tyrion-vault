# Kod retseptlari — animatsion video (tekshirilgan)

> **Manba:** barcha buyruqlar Tyrion muhitida **real ishga tushirilib tekshirilgan** (2026-09-21):
> ffmpeg 8.1.2 (Gyan full build), Python 3.13 (numpy, Pillow, PyYAML, faster-whisper), Node 22.
> Tekshirilmagan retsept alohida **"tekshirilmagan"** deb belgilangan — ishlatishdan oldin sinang.

## 1. Muhit (inventar — "bor" deb yozishdan oldin tekshirilgan)

| Vosita | Holat |
|---|---|
| `ffmpeg` / `ffprobe` 8.1.2 | **bor** — `libx264/x265/vpx-vp9/prores_ks/aac/opus/png` enkoderlari bilan |
| ffmpeg filtrlar | **bor**: `zoompan`, `crop`, `lut3d`, `curves`, `colorbalance`, `vignette`, `noise`, `unsharp`, `gblur`, `overlay`, `drawtext`, `subtitles`, `ass`, `xfade`, `concat`, `tonemap`, `zscale`, `vidstab*`, `sidechaincompress`, `loudnorm`, `afftdn`, `deesser`, `blackdetect`, `freezedetect`, `tblend`, `minterpolate` |
| ffmpeg filtrlar | **yo'q**: `scenedetect` (bu ffmpeg filtri emas — PySceneDetect paketi), OpenCV, librosa, moviepy, ImageMagick, whisper CLI |
| Python | **bor**: `numpy`, `PIL`, `yaml`, `faster_whisper` |
| Node/npm | **bor** — Remotion 4.0.526 o'rnatilgan va render qilingan loyiha mavjud: `output/reels-google-vs-meta/` (§10) |
| Shriftlar | Arial, Segoe UI, Calibri, Tahoma, Verdana, Times, Georgia — **U+02BB (ʻ) qoplaydi** (Pillow bilan tekshirilgan). `DejaVuSans.ttf` **yo'q** |

## 2. Filter faylini yozish — BOM tuzog'i (majburiy qoida)

Uzun filtergraph **faylda** saqlanadi va `-filter_complex_script` bilan beriladi
(Windows'da shell quoting muammosi yo'qoladi). Fayl **BOM'siz UTF-8** bo'lishi shart:

```python
from pathlib import Path
Path("build/render.filter").write_text(graph, encoding="utf-8")   # BOM'siz
```

```powershell
# XATO: Windows PowerShell'ning `-Encoding utf8` BOM qo'shadi va ffmpeg yiqiladi
"[0:v]scale=1080:1920,format=yuv420p[v]" | Set-Content -Encoding utf8 render.filter
```

BOM bilan olingan xato **chalkash** bo'ladi (sabab emas, oqibat ko'rsatiladi):

```
[AVFilterGraph] Trailing garbage after a filter: subtitles='test.srt',format=yuv420p[v]
```

## 3. Ifoda (expression) yozish qoidasi

1. Ichida **vergul** bo'lgan ifoda **qo'shtirnoqqa olinadi** — aks holda vergul filtr ajratuvchisi bo'lib ketadi:

   ```
   XATO : y=1400+40*(1-pow(1-min(t/0.4,1),3))
          -> [AVFilterGraph] No such filter: '1)'
   TO'G'RI: y='1400+40*(1-pow(1-min(t/0.4,1),3))'
   ```
2. Windows yo'llari filtr ichida: `C:/Windows/Fonts/arial.ttf` → `C\:/Windows/Fonts/arial.ttf`
   (`fontfile='C\:/Windows/Fonts/arial.ttf'` — tekshirilgan).
3. Qiymatda `:` (masalan `C:`) bo'lsa — faqat shu belgi escape qilinadi, `/` ishlatiladi (`\` emas).

## 4. Easing — ffmpeg'da matematik ekvivalent

| Egri | Ifoda (`p` = boshlang'ich, `q` = oxirgi, `T` = davomiylik kadr/sekundda) |
|---|---|
| ease-out-cubic | `p+(q-p)*(1-pow(1-min(t/T,1),3))` |
| ease-out-quint | `p+(q-p)*(1-pow(1-min(t/T,1),5))` |
| ease-in-cubic | `p+(q-p)*pow(min(t/T,1),3)` |
| ease-in-out-cubic | `if(lt(t,T/2),p+(q-p)*4*pow(t/T,3),q-(q-p)*4*pow(1-t/T,3))` |
| overshoot (back, 6%) | `p+(q-p)*(1+2.7*pow(min(t/T,1)-1,3)+1.7*pow(min(t/T,1)-1,2))` |
| stagger (element `i`) | `max(0,min((t-0.067*<i>)/0.4,1))` — 2 kadr (30 fps) oraliq |

## 5. Push-in (kamera yaqinlashuvi) — tekshirilgan 2 yo'l

**A yo'l — `scale eval=frame` + qat'iy o'lchamli `crop` (tavsiya etiladi):**

```
[0:v]scale=eval=frame:w='1242-162*(1-pow(1-min(t/1.5,1),3))':h='2208-288*(1-pow(1-min(t/1.5,1),3))',
     crop=1080:1920:x='(iw-ow)/2':y='(ih-oh)/2',format=yuv420p[v]
```
Natija (tekshirilgan): 1080×1920 qat'iy, 30 fps, kadrlar orasida ko'rinadigan o'zgarish (frame diff 12.8/255).

**B yo'l — `zoompan`:**

```
[0:v]scale=1620:2880:flags=lanczos,
     zoompan=z='1.5-0.5*(1-pow(1-min(on/45,1),3))':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':
     d=1:s=1080x1920:fps=30,format=yuv420p[v]
```
Natija (tekshirilgan): 1080×1920, 60 kadr/2 s, frame diff 37.4/255 (kuchliroq harakat).

**XATO (tekshirilgan anti-pattern):** `crop` da **vaqt bo'yicha o'zgaruvchan `w/h`** berish —
chiqish o'lchami kadrma-kadr o'zgaradi va enkoder birinchi kadr o'lchamida qotib qoladi:

```
[0:v]crop=w='1080-162*(1-pow(1-min(t/1.5,1),3))':h='1920-288*(...)':...   # -> 918x1632 chiqdi (1080x1920 emas)
```
Zoom kerak bo'lsa: o'lchamni `scale`/`zoompan` animatsiya qiladi, `crop` esa **qat'iy** o'lchamda qoladi.

## 6. Kinetik tipografiya (drawtext, tekshirilgan)

```
[0:v]scale=1080:1920,
 drawtext=fontfile='C\:/Windows/Fonts/arial.ttf':text='Birinchi soʻz':fontsize=96:fontcolor=white:
   box=1:boxcolor=black@0.35:boxborderw=24:x='(w-text_w)/2':
   y='1400+40*(1-pow(1-min(t/0.4,1),3))':alpha='min(t/0.4,1)',
 drawtext=fontfile='C\:/Windows/Fonts/arial.ttf':text='ikkinchi soʻz':fontsize=72:fontcolor=0xFFD166:
   x='(w-text_w)/2':y='1580':alpha='if(lt(t,0.1),0,min((t-0.1)/0.4,1))',
 format=yuv420p[v]
```
Tekshirilgan: `t=0.05` da matn deyarli ko'rinmaydi (alpha≈0.12), `t=1.00` da 16 276 px matn
1440–1632 qatorlarida — ya'ni **kirish animatsiyasi va stagger ishlaydi**; `ʻ` (U+02BB) Arial bilan chiziladi.

**Uzun matn uchun 3 yo'l (tanlang va aralashtirmang):**
1. `drawtext` — 1–2 qisqa qator, sarlavha/CTA uchun (tez, kod bilan boshqariladi).
2. **ASS fayl** (PlayRes + stil) — subtitr, ko'p qatorli matn, `\fad`, `\move`, `\t` animatsiyalari bilan (§8).
3. Remotion — sahnalar/komponentlar kerak bo'lsa (§10).

## 7. 9:16 koordinata xaritasi (1080×1920)

| Zona | y oralig'i | Izoh |
|---|---|---|
| Yuqori UI (bo'sh) | 0–230 | platforma yuqori paneli |
| Matn xavfsiz zonasi | 230–1536 | faqat shu yerda muhim matn |
| Subtitr/caption chizig'i | 1440–1536 | `MarginV` ≥ 380 (tekshirilgan: 1479–1526) |
| Pastki UI (bo'sh) | 1536–1920 | tugmalar/aksiya paneli |

Gorizontal: `x` 86–994 (8% marja); o'ng 12% (≈950–1080) — tugmalar zonasi, matn qo'yilmaydi.

## 8. Subtitr va caption (tekshirilgan)

**A yo'l (tavsiya) — o'z ASS fayli: qat'iy PlayRes, pikselli o'lchamlar.**

```
[Script Info]
PlayResX: 1080
PlayResY: 1920
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Caption,Arial,72,&H00FFFFFF,&H00FFFFFF,&H00101010,&H80000000,0,0,0,0,100,100,1,0,1,4,0,2,80,80,380,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,0:00:00.00,0:00:01.00,Caption,,0,0,0,,Salom, bu sinov subtitri
```
```
[0:v]...subtitles='D\:/tyrion/runs/x/captions.ass',format=yuv420p[v]
```
Tekshirilgan: matn 1480–1532 qatorlarida (pastki 12% **toza** — platforma UI zonasi bo'sh).

**B yo'l — SRT + `force_style`:** qiymatlar **skript koordinatasida** (SRT uchun 384×288),
ya'ni pikselli niyat ÷6.667 (1920/288):

```
subtitles='D\:/.../test.srt':force_style='Default.MarginV=57,Default.FontSize=11'
```
Tekshirilgan: matn 1479–1526 (kutilgan ~380 px pastki chegara). Sintaksis qoidasi (tekshirilgan):
`Default.Attr=qiymat` formati ishlaydi; prefikssiz va `*.Attr=` formalari **jim e'tiborsiz** qolishi mumkin;
`MarginV` ni "piksel" deb yozish matnni kadrdan **butunlay chiqarib yuboradi**
(`MarginV=400` → 400×6.667 = 2667 px → ko'rinmaydi).

## 9. Sahnalarni yig'ish: normalizatsiya + `xfade` (tekshirilgan)

Turli o'lcham/fps manbalarni bitta timeline'ga keltirish — **har klip avval normalizatsiya qilinadi**,
keyin o'tish qo'llanadi:

```
[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,fps=30,
     format=yuv420p,trim=duration=3,setpts=PTS-STARTPTS[v0];
[1:v]scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=0x101014,
     setsar=1,fps=30,format=yuv420p,trim=duration=2,setpts=PTS-STARTPTS[v1];
[v0][v1]xfade=transition=fade:duration=0.3:offset=2.7,format=yuv420p[v];
[2:a]loudnorm=I=-14:TP=-1.0:LRA=11[a]
```
Tekshirilgan: chiqish **1080×1920, 30 fps, 141 kadr, 4.700 s** (3 + 2 − 0.3 = 4.7 ✓).
`offset` = birinchi klip davomiyligi − o'tish davomiyligi; `xfade` dan keyin `fps`/`format` qayta qo'yiladi.

## 10. Remotion (sahna-asosli animatsiya) — **tekshirilgan (2026-09-21)**

Remotion 4.0.526 o'rnatilgan va ishlaydi; mavjud ishlaydigan namuna loyiha:
`outputs/reels-google-vs-meta/` (8 sahna React'da, 1080×1920 · 30 fps · 45 s).
Tekshiruv: `npx remotion still src/index.ts GoogleVsMeta out/verify-still.png --frame=45`
→ **1080×1920 PNG** chiqdi (bundle + render zanjiri ishlaydi).

```bash
npm i remotion @remotion/cli @remotion/media-utils
npx remotion studio                                              # jonli tahrir (brauzer)
npx remotion render src/index.ts Ad out/ad.mp4 --props=props.json --codec=h264 --crf=17 --concurrency=4
npx remotion render src/index.ts Ad out/draft.mp4 --scale=0.5 --crf=26      # tez draft
npx remotion still  src/index.ts Ad out/poster.png --frame=45               # QA uchun kadr
```
Asosiy API: `useCurrentFrame()`, `interpolate(frame,[0,12],[0,1],{extrapolateRight:'clamp',easing:Easing.bezier(0.22,1,0.36,1)})`,
`spring({frame, fps, config:{damping:200}})`, `<Sequence from={} durationInFrames={}>`, `<AbsoluteFill>`,
`<OffthreadVideo playbackRate={}>` (speed ramp uchun), `<Audio startFrom trimAfter>`.
**Determinizm ogohlantirishi:** mavjud loyiha `@remotion/google-fonts` ishlatadi — shrift render paytida
yuklanadi, ya'ni internetsiz/ofisda render boshqacha chiqishi mumkin. Professional ishda shrift **lokal**
qo'yiladi (`staticFile()` + `@font-face`); `Math.random()` o'rniga `random('<seed>')`, `Date.now()` ishlatilmaydi.

## 11. Ovoz: miks, loudness, ducking (tekshirilgan)

**1) O'lchov (1-pass) — JSON qaytaradi:**
```bash
ffmpeg -hide_banner -nostats -i in.mp4 -af loudnorm=I=-14:TP=-1.0:LRA=11:print_format=json -f null -
```
Tekshirilgan chiqish namunasi: `input_i=-14.04  input_tp=-6.95  input_lra=0.00  input_thresh=-24.04  target_offset=0.00`.

**2) Qo'llash (2-pass, linear) — o'lchangan qiymatlar bilan:**
```bash
ffmpeg -y -i in.mp4 -c:v copy \
  -af "loudnorm=I=-14:TP=-1.0:LRA=11:linear=true:measured_I=-14.04:measured_TP=-6.95:measured_LRA=0.00:measured_thresh=-24.04:offset=0.00" \
  -c:a aac -b:a 192k out.mp4
```
Tekshirilgan: natija `I = -14.03 LUFS`, `TP = -3.18 dBTP` (maqsad −14/−1.0 ✓).

**3) VO ostida musiqa ducking (sidechain):**
```
[0:a]highpass=f=80,acompressor=threshold=-18dB:ratio=3:attack=10:release=200,loudnorm=I=-16:TP=-2:LRA=7[vo];
[1:a]volume=0.35[mus];
[mus][vo]sidechaincompress=threshold=0.03:ratio=12:attack=5:release=350:makeup=1[ducked];
[ducked][vo]amix=inputs=2:duration=shortest:weights=1 1:normalize=0[a]
```
Tekshirilgan: zanjir ishlaydi (miks o'lchandi, `I=-22.05`, `TP=-17.40` — test sinuslari past).
Haqiqiy ishda miks **oxirida** yana `loudnorm` bilan −14 LUFS ga keltiriladi.

## 12. Eksport (tekshirilgan buyruq)

```bash
ffmpeg -y -hide_banner -v error \
  -i master.mov \
  -map "[v]" -map "[a]" \
  -c:v libx264 -preset slow -crf 17 -profile:v high -level 4.0 \
  -pix_fmt yuv420p -g 60 -bf 2 -movflags +faststart \
  -c:a aac -b:a 192k -ar 48000 -shortest \
  final_9x16_1080x1920.mp4
```
- `-g 60` = 30 fps da 2 s keyframe oralig'i (platforma qayta kodlashi uchun qulay).
- `-movflags +faststart` — mobil ijro uchun moov atom oldinga.
- Draft: `-preset veryfast -crf 24` + `-vf scale=540:960` (tez ko'rish uchun).
- Yakuniy o'lcham/bitrate **registry'dan** (`ads/references/creative-source-registry.md`), yoddan emas.
