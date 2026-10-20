# QA darvozasi — video montaj (topshirishdan oldin)

> Shell: **PowerShell**. Buyruqlar ffmpeg/ffprobe 8.1.2 da ishga tushirilgan. Har band — **o'lchov**.

## 0. Fayllar

```powershell
$F   = "outputs/video-runs/<run>\workers\video-editor\renders\final_9x16.mp4"
$SRC = "outputs/video-runs/<run>\workers\video-editor\assets\original.mp4"
```

## 1. Manba material daxlsizligi (birinchi tekshiruv)

```powershell
Get-FileHash -Algorithm SHA256 $SRC | Format-List
```
| Band | O'tish sharti |
|---|---|
| Manba hash | Ingest paytida yozilgan hash bilan **bir xil** (fayl o'zgartirilmagan) |
| Manba joyida | Fayl o'chirilmagan, ko'chirilmagan |

## 2. Texnik butunlik

```powershell
ffprobe -v error -select_streams v:0 -count_frames `
  -show_entries "stream=width,height,r_frame_rate,avg_frame_rate,nb_read_frames,pix_fmt:format=duration,bit_rate" `
  -of default=nw=1 $F
```
| Band | O'tish sharti |
|---|---|
| O'lcham | Format spec bilan aynan mos (9:16 → 1080×1920, 1:1 → 1080×1080) |
| `r_frame_rate == avg_frame_rate` | CFR (VFR chiqarilmaydi) |
| `nb_read_frames / fps ≈ duration` | Farq ≤1 kadr — kesimlar kadr aniq |
| `pix_fmt` | `yuv420p` |
| Bitrate | Registry chegarasida (~10–12 Mbps vertikal) |

## 3. Kesim va montaj tekshiruvi

| Band | Tekshiriladi |
|---|---|
| Cut list mosligi | EDL'dagi har kesim natijada bor; davomiyliklar ±1 kadr |
| Dead-air | EDL'da "olib tashlanadi" belgilangan jimliklar chiqishda yo'q |
| Hook | 0–3 s: birinchi kadr pattern-interrupt, logo bilan boshlanmaydi |
| Ritm | 2 s dan uzun harakatsiz kadr yo'q; shot uzunligi formatga mos |
| Desync | Kamida 3 nuqtada (bosh/o'rta/oxir) lab harakati ≤1 kadr siljish |
| O'tishlar | ~90% hard-cut; effektlar faqat ma'noli joyda |

```powershell
# Nuqson skanerlari: bo'sh chiqish = nuqson yo'q
ffmpeg -hide_banner -nostats -i $F -vf "blackdetect=d=0.1:pix_th=0.10" -f null - 2>&1 | Select-String "black_"
ffmpeg -hide_banner -nostats -i $F -vf "freezedetect=n=-60dB:d=0.5" -f null - 2>&1 | Select-String "freeze"
ffmpeg -hide_banner -nostats -i $F -af "silencedetect=noise=-30dB:d=0.4" -f null - 2>&1 | Select-String "silence"
```

## 4. Rang (shot matching)

| Band | O'tish sharti |
|---|---|
| Kesimda rang sakrashi | Yo'q — qo'shni shotlar bir-biriga moslangan |
| Teri rangi | Tabiiy (qizil/magenta surilmagan) |
| Palitra | 1 LUT, 60-30-10; oversaturatsiya va neon yo'q |
| Yorqinlik | Waveform 0–100% ichida; kuygan (clipped) sohalar yo'q |
| Rasm sifati | Over-sharpening halo yo'q, banding yo'q |

```powershell
ffmpeg -y -v error -i $F -vf "fps=2,scale=270:-1,tile=5x4" -frames:v 1 kontakt-varaq.png
```
Kontakt varaq — rang sakrashi va ritmni bir qarashda ko'rish uchun (majburiy tekshiriladi).

## 5. Ovoz

```powershell
ffmpeg -hide_banner -nostats -i $F -af loudnorm=I=-14:TP=-1.0:LRA=11:print_format=json -f null -
```
| Band | O'tish sharti |
|---|---|
| `input_i` | −14 ± 0.5 LUFS |
| `input_tp` | ≤ −1.0 dBTP (kliping yo'q) |
| `input_lra` | ≤ 11 |
| VO/musiqa balansi | Musiqa VO'ni bosmaydi (ducking ishlaydi) |
| Kirish/chiqish | Fade 10–20 kadr; keskin uzilish yo'q |
| Shovqin | `afftdn` dan keyin fon shovqini eshitilmaydi, ovoz "metall" bo'lmagan |

## 6. Subtitr va matn

| Band | O'tish sharti |
|---|---|
| Safe-zone | Matn 230–1536 px oralig'ida; pastki 20% (platforma UI) va o'ng 12% da matn yo'q |
| O'qiluvchanlik | ≤28 belgi/qator, ≤2 qator, kontrast ≥4.5:1 |
| Vaqt | Har so'z ekranda ≥0.35 s; gap bilan sinxron |
| Imlo | O'zbek lotin/kirill va rus: apostrof U+02BB, raqam/manba to'g'ri |
| Tillar | Har til segmenti alohida yozilgan (tarjima emas), sifati tekshirilgan |

## 7. Platforma mosligi

| Band | O'tish sharti |
|---|---|
| Spec manbasi | `ads/references/creative-source-registry.md` + olingan sana MANIFEST'da |
| Davomiylik | Platforma limitida (registry'dan) |
| Birinchi kadr | Thumbnail sifatida ham ishlaydi (harakatda emas, kadr sifatida o'qiladi) |
| CTA | Oxirida ≥2 s, ekranda aniq (Telegram), havola brief bilan mos |

## 8. Topshirish to'plami

| Element | Talab |
|---|---|
| Render(lar) | Kerakli formatlarda + SHA-256 |
| Nomi | `YYYY-MM-DD_<mijoz>_<mavzu>_<format>_v<N>.mp4` |
| `MANIFEST.md` | Manba→chiqish xaritasi, litsenziyalar, spec manbasi, QA natijasi |
| `cut-list.json` / `build.py` | Cut list va render skripti — natija noldan qayta chiqadi |
| Manba | O'zgartirilmagan (hash bilan tasdiqlangan) |

## 9. Rad etish sabablari (bittasi bo'lsa topshirilmaydi)

1. Manba fayl o'zgartirilgan/o'chirilgan.
2. VFR chiqish yoki kadr soni davomiylikka mos emas (kesim "sakraydi").
3. Desync >1 kadr yoki ovoz gap o'rtasida uzilgan.
4. Loudness −14 LUFS dan ±1 chetlashgan yoki TP > −1 dBTP.
5. Kesimda rang sakrashi / shot matching qilinmagan.
6. Subyekt yuzi kesilgan crop yoki matn safe-zonedan tashqarida.
7. Dead-air EDL'da olib tashlangan deb yozilgan, lekin chiqishda qolgan.
8. Subtitr imlosi tekshirilmagan yoki faqat bitta til uchun yozilgan (3 til kerak bo'lganda).
9. Litsenziyasi noma'lum musiqa/stock MANIFEST'da.
10. Render qo'lda tuzatilgan — skriptda qayta tiklanmaydi.
