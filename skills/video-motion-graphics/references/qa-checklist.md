# QA darvozasi — animatsion video (topshirishdan oldin)

> Buyruqlar Tyrion muhitida ishga tushirilgan (ffmpeg/ffprobe 8.1.2). Har band **o'lchov**,
> taxmin emas: "yaxshi ko'rinadi" — dalil emas.

> Shell: **PowerShell** (`pwsh`). Uzun buyruqni satrga bo'lish uchun backtick (`` ` ``), quvur `|`.

## 0. Tekshiriladigan fayl

```powershell
$F = "outputs/video-runs/<run>\workers\video-editor\renders\final_9x16.mp4"
```

## 1. Texnik butunlik

```powershell
ffprobe -v error -select_streams v:0 -count_frames `
  -show_entries stream=width,height,r_frame_rate,avg_frame_rate,nb_read_frames,pix_fmt,color_transfer `
  -show_entries format=duration,bit_rate -of default=nw=1 $F
```
| Band | O'tish sharti |
|---|---|
| O'lcham | Format spec bilan **aynan** mos (9:16 → 1080×1920) |
| `r_frame_rate == avg_frame_rate` | Teng — VFR emas (VFR = platformada stutter) |
| `nb_read_frames / fps ≈ duration` | Farq ≤ 1 kadr (kadr aniqligi) |
| `pix_fmt` | `yuv420p` (SDR tarqatish) |
| `color_transfer` | `unknown`/`bt709` — HDR material bo'lsa tonemap qilingani yozilgan |
| Bitrate | Registry'dagi chegarada (vertikal odatda ~10–12 Mbps) |

## 2. Nuqson skanerlari (bo'sh chiqish = nuqson yo'q)

```powershell
ffmpeg -hide_banner -nostats -i $F -vf blackdetect=d=0.1:pix_th=0.10 -f null - 2>&1 | Select-String "black_"
ffmpeg -hide_banner -nostats -i $F -vf freezedetect=n=-60dB:d=0.5 -f null - 2>&1 | Select-String "freeze"
ffmpeg -hide_banner -nostats -i $F -af silencedetect=noise=-30dB:d=0.4 -f null - 2>&1 | Select-String "silence"
```
| Nuqson | Chegara |
|---|---|
| Qora kadr (`black_start`) | Faqat ssenariyda ataylab bo'lsa; boshqa holatda — nuqson |
| Muzlagan kadr (`freeze_start`) | Ruxsat etilgan maksimum 0.5 s (ataylab "hold" dan tashqari) |
| Jimlik (`silence_start`) | ≥0.4 s jimlik — faqat ataylab pauza |

## 3. Ovoz (miks)

```powershell
ffmpeg -hide_banner -nostats -i $F -af loudnorm=I=-14:TP=-1.0:LRA=11:print_format=json -f null -
```
| Band | O'tish sharti |
|---|---|
| `input_i` (integrated) | −14 ± 0.5 LUFS (Reels/TikTok normasi) |
| `input_tp` (true peak) | ≤ −1.0 dBTP |
| `input_lra` | ≤ 11 (VO + musiqa uchun kengaytirilgan diapazon emas) |
| Ovoz-sinxron | Harakat/SFX kadri bilan mos: kesimlarda ≤1 kadr siljish qabul qilinadi |

## 4. Kadr aniqligi va ko'rinish tekshiruvi (ko'z + skript)

```powershell
ffmpeg -y -v error -i $F -vf "fps=2,scale=270:-1,tile=5x4" -frames:v 1 kontakt-varaq.png
ffmpeg -y -v error -ss <hook_vaqti> -i $F -frames:v 1 kadr_hook.png
ffmpeg -y -v error -sseof -0.2 -i $F -frames:v 1 kadr_oxir.png
```
| Band | Tekshiriladi |
|---|---|
| Hook (0–3 s) | Birinchi kadr pattern-interrupt; logo bilan boshlanmaydi; ovozsiz ham ma'no bor |
| Safe-zone | Muhim matn 230–1536 px oralig'ida, pastki 20% (1536–1920) va o'ng 12% da matn **yo'q** |
| Ritm | 2 s dan uzun harakatsiz/o'lik kadr yo'q (kontakt varaqda ko'rinadi) |
| Rang | Bitta palitra, teri rangi tabiiy, banding yo'q, oversaturatsiya yo'q |
| Matn | ≤2 shrift, kontrast ≥4.5:1, imlo (ʻ = U+02BB), raqamlar to'g'ri |
| Oxiri | CTA ≥2 s turadi; loop uchun oxirgi kadr boshlanish bilan mos |

## 5. Topshirish to'plami (release)

| Element | Talab |
|---|---|
| Render(lar) | Spec bo'yicha fayl(lar) + SHA-256 |
| `MANIFEST.md` | Har asset: manba URL, litsenziya, hash; stock/AI asset farqlanadi |
| `build.py` / `render.sh` | Natija noldan qayta chiqadi; versiya (`ffmpeg 8.1.2`) yozilgan |
| `props.json` | Matn/raqam/rang tokenlari — kodda sehrli son yo'q |
| Spec manbasi | Registry fayli + olingan sana |
| QA natijasi | Shu fayl bo'yicha to'ldirilgan jadval (har band OK) |

```powershell
Get-FileHash -Algorithm SHA256 "renders\final_9x16.mp4" | Format-List
```

## 6. Rad etish sabablari (bittasi bo'lsa topshirilmaydi)

1. VFR yoki kadr soni davomiylikka mos emas.
2. Qora/muzlagan kadr yoki kutilmagan jimlik topildi.
3. Integrallangan loudness −14 LUFS dan ±1 dan ortiq chetlashgan yoki TP > −1 dBTP.
4. Matn safe-zonedan tashqarida yoki platforma UI zonasi ostida.
5. Easing yo'q (linear) harakat, bir vaqtda 4+ element harakati.
6. Matn imlosi/apostrofi xato yoki raqam manbasiz.
7. Litsenziyasi noma'lum asset (musiqa, stock, AI) MANIFEST'da.
8. Render qo'lda tuzatilgan, skriptda qayta tiklanmaydi.
9. Spec (o'lcham/bitrate/davomiylik) registry'dan olinmagan.
10. CTA oxirida 2 s dan kam yoki ekranda aniq emas.
