# Kod retseptlari — video edit/montaj (tekshirilgan)

> **Manba:** buyruqlar Tyrion muhitida **real ishga tushirilib tekshirilgan** (2026-09-21):
> ffmpeg 8.1.2, Python 3.13 (numpy, Pillow, faster-whisper). Shell — **PowerShell**.
> Sinov materiali: 1920×1080 30 fps, 2 shot, 1 s jimlik bilan — "foydalanuvchi videosi" simulyatsiyasi.

## 1. Ingest triage (bitta `-show_entries` ichida!)

```powershell
ffprobe -v error -select_streams v:0 -show_entries `
  "stream=width,height,r_frame_rate,avg_frame_rate,pix_fmt,color_transfer,color_primaries:format=duration,bit_rate" `
  -of default=nw=1 input.mp4
```
**Muhim (tekshirilgan tuzoq):** `-show_entries` ni ikki marta berish — ikkinchisi birinchisini
**bekor qiladi** va maydonlar bo'sh chiqadi. Bir marta yozing: `"stream=...:format=..."`.

| Maydon | Xulosa |
|---|---|
| `r_frame_rate != avg_frame_rate` | **VFR** (telefon videosi) → `fps=30` filtr + `-fps_mode cfr` majburiy |
| `color_transfer=arib-std-b67` | HLG (iPhone HDR) → tonemap kerak |
| `color_transfer=smpte2084` | PQ (HDR10) → tonemap kerak |
| `width > height` | Gorizontal → reframe strategiyasi kerak (§5) |

Kadr soni va aniq davomiylik:
```powershell
ffprobe -v error -select_streams v:0 -count_frames `
  -show_entries "stream=nb_read_frames,r_frame_rate:format=duration" -of default=nw=1 input.mp4
```
Tekshirilgan: `nb_read_frames=78`, `r_frame_rate=30/1`, `duration=2.600000` → 78/30 = 2.6 s ✓ (mos).

HDR → SDR (kerak bo'lganda):
```
[0:v]zscale=t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,tonemap=hable:desat=0,zscale=t=bt709:m=bt709:r=tv,format=yuv420p[v]
```

**Proxy** (uzun material, tez montaj):
```powershell
ffmpeg -y -i input.mp4 -vf "scale=960:-2" -c:v libx264 -preset veryfast -crf 26 -c:a copy proxy.mp4
```

## 2. Klipni normalizatsiya qilish (timeline'ga tayyorlash)

```
[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,fps=30,
     format=yuv420p,trim=duration=<d>,setpts=PTS-STARTPTS[v0]
```
- `increase` + `crop` — kadr to'ldiriladi (kesiladi); `decrease` + `pad` — butun kadr sig'adi (chetlar fon).
- `setsar=1` majburiy: aks holda turli SAR'li kliplar `concat` da cho'ziladi.
- `fps=30` — VFR ni CFR ga o'giradi (tekshirilgan: turli fps'dagi 1080p va 1080×1080 kliplar
  bitta 30 fps timeline'ga tushdi).

## 3. Shot-log (kesim nuqtalarini topish)

```powershell
ffmpeg -hide_banner -nostats -i input.mp4 -vf "select='gt(scene,0.3)',showinfo" -f null - 2>&1 |
  Select-String "pts_time"
```
Tekshirilgan: sinov klipining shot almashinuvi `pts_time:2` da topildi ✓.
Bu — **mavjud kesimlar** ro'yxati (paper edit uchun tayanch), o'z kesimlaringiz emas.
`scenedetect` ffmpeg filtri emas — PySceneDetect kerak bo'lsa `pip install scenedetect` (o'rnatilmagan).

## 4. Dead-air (jimlik) topish va olib tashlash

```powershell
ffmpeg -hide_banner -nostats -i input.mp4 -af "silencedetect=noise=-30dB:d=0.4" -f null - 2>&1 |
  Select-String "silence_"
```
Tekshirilgan chiqish: `silence_start: 1.509302`, `silence_end: 2.50774` (1 s jimlik ─ aynan topildi).

Topilgan oraliqlar cut list'ga "olib tashlanadi" deb yoziladi, so'ng kesim `trim` bilan qilinadi (§6).
Ovozda jimlik **saqlanishi kerak** bo'lsa (pauza, dramatik to'xtash) — sabab EDL'da yoziladi.

## 5. Vertikal reframe — blur fon (tekshirilgan)

```
[0:v]split=2[bg][fg];
[bg]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,
    boxblur=luma_radius=48:luma_power=2:chroma_radius=24:chroma_power=2,eq=brightness=-0.08[bgv];
[fg]scale=1080:-2:flags=lanczos[fgv];
[bgv][fgv]overlay=x='(W-w)/2':y='(H-h)/2',format=yuv420p[v]
```
Tekshirilgan: 1920×1080 kirish → **1080×1920** chiqish (4.0 s), subyekt to'liq ko'rinadi, fon xiralashgan.

**Markaziy crop** (subyekt markazda bo'lsa) — eng arzon va eng aniq:
```
[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,format=yuv420p[v]
```
**Pan-and-scan** (subyekt harakatlanadi): qat'iy o'lchamli `crop` + vaqt bo'yicha `x` ifodasi:
```
[0:v]scale=1920:1920,crop=1080:1920:x='(iw-ow)*(1-pow(1-min(t/3,1),3))':y=0,format=yuv420p[v]
```
Qat'iy qoida: `crop` o'lchami **o'zgarmas** bo'lishi shart (o'zgaruvchan `w/h` = buzilgan chiqish;
batafsil: `video-motion-graphics/references/code-recipes.md` §5).

## 6. Kesish va birlashtirish — bitta o'tishda (tekshirilgan)

EDL'dagi kesimlar **bitta filtr zanjirida** bajariladi (oraliq fayl yo'q → sifat yo'qolmaydi):

```
[0:v]trim=start=0.2:end=1.4,setpts=PTS-STARTPTS[v0];
[0:v]trim=start=2.2:end=3.6,setpts=PTS-STARTPTS[v1];
[v0][v1]concat=n=2:v=1:a=0[v];
[0:a]atrim=start=0.2:end=1.4,asetpts=PTS-STARTPTS[a0];
[0:a]atrim=start=2.2:end=3.6,asetpts=PTS-STARTPTS[a1];
[a0][a1]concat=n=2:v=0:a=1,loudnorm=I=-14:TP=-1.0:LRA=11[a]
```
Tekshirilgan: 1.2 s + 1.4 s = **2.6 s / 78 kadr** (aynan ✓) — ya'ni `trim`+`concat` kadr aniqligida ishlaydi.

- `setpts=PTS-STARTPTS` / `asetpts=PTS-STARTPTS` **majburiy** — aks holda vaqt chizig'i sakraydi va
  keyingi filtrlar (xfade, overlay, subtitr) noto'g'ri vaqtda ishlaydi.
- Kliplar orasida o'tish kerak bo'lsa `xfade` (§8) ishlatiladi, `concat` esa keskin kesim uchun.
- **Kesish kadr aniqligi:** `-ss`/`-t` bilan "tez" kesish faqat `-c copy` da keyframe'ga yopishadi;
  aniq kesish uchun `trim` filtri (yuqoridagi) yoki `-ss` ni input'dan oldin + qayta kodlash.

Ovozli J-cut/L-cut (ovoz kadrdan 12 kadr oldin):
```
[0:a]atrim=start=1.0:end=2.6,asetpts=PTS-STARTPTS,adelay=0|0[a]
```

## 7. Transkript va subtitr (tekshirilgan pipeline)

```python
from faster_whisper import WhisperModel
model = WhisperModel("tiny", device="cpu", compute_type="int8")   # o'zbek uchun "small"/"medium"
segments, info = model.transcribe("speech.wav", language="uz", word_timestamps=True)
```
Tekshirilgan: 4.4 s gapi → **3 segment, 14 so'z**, so'z vaqtlari bilan; SRT yozildi
(`00:00:00,000 --> 00:00:02,340`). Model birinchi ishlatishda yuklanadi (internet kerak;
`HF_TOKEN` qo'yilsa tezroq). Natija **qo'lda tahrirlanadi** — imlo va atamalar avtomatik ishonilmaydi.

SRT → kadrga chizish va safe-zone (tekshirilgan retsept):
```
[0:v]...subtitles='D\:/tyrion/runs/x/captions.ass',format=yuv420p[v]
```
ASS faylida `PlayResX: 1080`, `PlayResY: 1920`, `MarginV: 380` (pastki 380 px) — matn
1479–1526 qatorlarida chiqadi, ya'ni platforma UI zonasidan yuqorida ✓.
`force_style` ishlatilsa qiymatlar **skript koordinatasida** (SRT uchun 384×288 → ÷6.667):
`force_style='Default.MarginV=57,Default.FontSize=11'`.

## 8. O'tishlar (`xfade`) va temp (speed ramp)

```
[v0][v1]xfade=transition=fade:duration=0.3:offset=2.7,format=yuv420p[v]
```
Tekshirilgan: 3 s + 2 s klip, `offset=2.7`, `duration=0.3` → chiqish 4.7 s ✓.
`offset = birinchi klip davomiyligi − o'tish davomiyligi`. O'tishlar iqtisodi: ~90% hard-cut;
effekt (whip/glitch/zoom) faqat ma'no anglatganda.

Temp (sekinlashtirish/tezlashtirish, ovoz balandligi saqlanadi):
```
[0:v]setpts=0.5*PTS[v];[0:a]atempo=2.0[a]        # 2× tez
[0:v]setpts=1.5*PTS[v];[0:a]atempo=0.6667[a]     # 1.5× sekin
```
`atempo` chegarasi 0.5–2.0 (undan tashqarisi zanjir bilan: `atempo=2.0,atempo=2.0`).

## 9. Ovoz: tozalash va miks (tekshirilgan)

**Tozalash zanjiri:**
```
[0:a]highpass=f=90,afftdn=nf=-25,deesser=i=0.4,
     acompressor=threshold=-18dB:ratio=3:attack=8:release=180,
     loudnorm=I=-16:TP=-2:LRA=9[a]
```
Tekshirilgan: zanjir ishlaydi (VO tayyorlash uchun −16 LUFS).

**Musiqa ducking (VO ostida):**
```
[0:a]highpass=f=80,acompressor=threshold=-18dB:ratio=3:attack=10:release=200,loudnorm=I=-16:TP=-2:LRA=7[vo];
[1:a]volume=0.35[mus];
[mus][vo]sidechaincompress=threshold=0.03:ratio=12:attack=5:release=350:makeup=1[ducked];
[ducked][vo]amix=inputs=2:duration=shortest:weights=1 1:normalize=0[a]
```
Tekshirilgan: zanjir ishlaydi. **Yakuniy miks oxirida** yana `loudnorm=I=-14:TP=-1.0:LRA=11`.

**O'lchov (majburiy topshirishdan oldin):**
```powershell
ffmpeg -hide_banner -nostats -i final.mp4 -af loudnorm=I=-14:TP=-1.0:LRA=11:print_format=json -f null -
```
Tekshirilgan namunaviy chiqish: `input_i=-14.04  input_tp=-6.95  input_lra=0.00`.
2-pass qo'llash (o'lchangan qiymatlar bilan) — `video-motion-graphics/references/code-recipes.md` §11.

## 10. Stabilizatsiya (2-pass vidstab, tekshirilgan)

```powershell
ffmpeg -y -i input.mp4 -vf "vidstabdetect=shakiness=6:accuracy=15:result=transforms.trf" -f null -
ffmpeg -y -i input.mp4 -vf "vidstabtransform=input=transforms.trf:smoothing=20:zoom=2:interpol=bicubic,unsharp=5:5:0.6" `
  -c:v libx264 -preset veryfast -crf 20 -pix_fmt yuv420p -an stabilized.mp4
```
Tekshirilgan: ikkala pass xatosiz ishlaydi. `zoom=2` — chetlarda paydo bo'ladigan qora bo'shliqni yopadi;
`unsharp` stabilizatsiya yumshatgan detallarni qaytaradi. Stabilizatsiya **kesishdan oldin** qilinadi.

## 11. Eksport (tekshirilgan)

```powershell
ffmpeg -y -hide_banner -v error -i master.mov -map "[v]" -map "[a]" `
  -c:v libx264 -preset slow -crf 17 -profile:v high -level 4.0 `
  -pix_fmt yuv420p -g 60 -bf 2 -movflags +faststart `
  -c:a aac -b:a 192k -ar 48000 -shortest `
  "2026-09-21_mijoz_mavzu_9x16_v1.mp4"
```
- 30 fps da `-g 60` = 2 s keyframe oralig'i (platforma qayta kodlashi silliq bo'ladi).
- Draft: `-preset veryfast -crf 24` + `-vf scale=540:960` (tez ko'rish, mijoz tasdig'i uchun).
- Yakuniy spec **registry'dan**: `ads/references/creative-source-registry.md` (yoddan emas).

## 12. Yetkazish to'plami

```powershell
Get-FileHash -Algorithm SHA256 renders\*.mp4 | Format-Table Path, Hash
```
`MANIFEST.md` da: manba fayl → chiqish fayl xaritasi, har bir hash, ishlatilgan musiqa/stock
litsenziyasi, spec manbasi + sana, `build.py` versiyasi, QA jadvali natijasi.
Manba fayllar **o'zgartirilmagan** (hash solishtiriladi).
