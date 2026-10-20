#!/usr/bin/env python3
"""video-run — video ishi uchun ish maydonini ochadi (scaffold). 0 token, LLM'siz.

Muammo: har video ishida papka tuzilishi, MANIFEST, render skripti va QA jadvali qo'lda
qaytadan o'ylab topilardi — natijada yo'llar, hash yozuvi va QA darvozasi ishdan ishga
farq qilardi (natijani taqqoslab bo'lmaydi, litsenziya/hash yo'qoladi).

Yechim: bitta buyruq standart ish maydonini ochadi va tayyor skeletlarni beradi:
  .claude-ads/runs/<run_id>/workers/<task_id>/
    assets/     — manba nusxalari (stock, mijoz videosi; asl fayl tegilmaydi)
    renders/    — chiqish fayllari
    build.py    — qayta ishga tushiriladigan render skripti (ffmpeg + QA)
    props.json  — matn/kesim/spec tokenlari (kodda sehrli son yo'q)
    MANIFEST.md — manba→chiqish xaritasi, hash, litsenziya, spec manbasi
    qa.md       — topshirish darvozasi jadvali (to'ldiriladi)

Buyruqlar:
  py -3 tools\\video-run.py new --client dilobar --topic "kuz-aksiya" --task video-editor --format 9x16
  py -3 tools\\video-run.py list
  py -3 tools\\video-run.py status <run_id>
  py -3 tools\\video-run.py new --dry-run --client test --topic demo     # reja ko'rsatiladi, yozilmaydi

Qoidalar: mavjud fayl ustiga YOZILMAYDI (xato qaytaradi — hech narsa o'chirilmaydi);
qayta ishga tushirish idempotent (bo'sh papkalar va yo'q fayllar to'ldiriladi).
Kod: 0 — bajarildi, 1 — mumkin emas (fayl bor / run topilmadi), 2 — argument xatosi.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

VAULT = Path(__file__).resolve().parent.parent
DEFAULT_ROOT = VAULT / "outputs" / "video-runs"
FORMATS = {"9x16": (1080, 1920), "1x1": (1080, 1080), "16x9": (1920, 1080), "4x5": (1080, 1350)}

for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        try:
            _stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:  # pragma: no cover
            pass

SLUG_RE = re.compile(r"[^a-z0-9]+")

BUILD_PY = r'''#!/usr/bin/env python3
"""Render skripti — {run_id}/{task}: normalizatsiya → kesim → kadr → rang → subtitr → miks → eksport → QA.

Qayta ishga tushiriladi: `py -3 build.py` (bir martalik buyruq emas).
Manba fayllar o'zgartirilmaydi: hash solishtiriladi va natija MANIFEST'ga yoziladi.
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

for _stream in (sys.stdout, sys.stderr):          # Windows konsoli cp1251 bo'lsa ham UTF-8
    if hasattr(_stream, "reconfigure"):
        try:
            _stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

HERE = Path(__file__).resolve().parent
PROPS = json.loads((HERE / "props.json").read_text(encoding="utf-8"))
RENDERS = HERE / "renders"
RENDERS.mkdir(exist_ok=True)
W, H = PROPS["output"]["width"], PROPS["output"]["height"]
FPS = PROPS["output"]["fps"]
CUES = PROPS.get("cut_list", [])


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def run(cmd: list[str]) -> int:
    proc = subprocess.run(cmd)
    return proc.returncode


def video_chain() -> str:
    """Manba → normalizatsiya (CFR, SAR) → kesimlar → concat → reframe → rang."""
    src = PROPS["source"]["path"]
    norm = ("scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},setsar=1,"
            "fps={fps},format=yuv420p").format(w=W, h=H, fps=FPS)
    parts: list[str] = []
    if CUES:
        for i, cue in enumerate(CUES):
            parts.append(f"[0:v]trim=start={cue['in']}:end={cue['out']},{norm},"
                         f"setpts=PTS-STARTPTS[v{i}]")
        labels = "".join(f"[v{i}]" for i in range(len(CUES)))
        parts.append(f"{labels}concat=n={len(CUES)}:v=1:a=0[vcut]")
    else:
        parts.append(f"[0:v]{norm},setpts=PTS-STARTPTS[vcut]")
    chain = ";".join(parts)          # zanjirlar `;` bilan ajratiladi (aks holda parser yiqiladi)
    # rang: yagona palitra — ekspozitsiya → kontrast → saturatsiya (LUT oxirida, bitta)
    grade = PROPS.get("color", {}).get("filter", "eq=contrast=1.04:saturation=1.04")
    post = f"[vcut]{grade},format=yuv420p[vgraded]"
    return chain + ";" + post


def audio_chain() -> str:
    """Ovoz: tozalash → (musiqa bo'lsa ducking) → loudness normasi.

    Diqqat: bitta yorliq (label) ikki marta ishlatilmaydi — VO'ni ham sidechain, ham miks
    uchun berish kerak bo'lsa `asplit` qo'yiladi (aks holda ffmpeg zanjirni rad etadi).
    """
    a = PROPS.get("audio", {})
    steps = ["highpass=f=90", "afftdn=nf=-25",
             "acompressor=threshold=-18dB:ratio=3:attack=8:release=180"]
    voice = "[0:a]" + ",".join(steps) + "[vo0]"
    music = a.get("music")
    if music:
        return (voice + ";"
                "[vo0]asplit=2[vo][voside];"
                f"[1:a]volume={a.get('music_gain', 0.28)}[mus];"
                "[mus][voside]sidechaincompress=threshold=0.03:ratio=12:attack=5:release=350:makeup=1[duck];"
                "[duck][vo]amix=inputs=2:duration=shortest:weights=1 1:normalize=0,"
                f"loudnorm=I={a.get('lufs', -14)}:TP=-1.0:LRA=11[a]")
    return voice + f";[vo0]loudnorm=I={a.get('lufs', -14)}:TP=-1.0:LRA=11[a]"


def captions_chain() -> str:
    """ASS subtitr (PlayRes = kadr o'lchami; pikselli MarginV) — safe-zone ichida."""
    ass = PROPS.get("captions")
    if not ass:
        return ""
    esc = (HERE / ass).resolve().as_posix().replace(":", r"\:")   # Windows: / + escape qilingan ':'
    return f"[vgraded]subtitles='{esc}'[vsub]"


def render(tag: str = "final") -> Path:
    graph_file = HERE / f"render_{tag}.filter"
    audio_graph = audio_chain()
    caps = captions_chain()
    vlabel = "vsub" if caps else "vgraded"
    graph = video_chain() + ";" + (caps + ";" if caps else "") + audio_graph
    graph_file.write_text(graph, encoding="utf-8")  # BOM'SIZ — BOM ffmpeg'ni yiqitadi
    out = RENDERS / f"{PROPS['output']['basename']}_{tag}.mp4"
    cmd = ["ffmpeg", "-y", "-hide_banner", "-v", "error", "-i", PROPS["source"]["path"]]
    if PROPS.get("audio", {}).get("music"):
        cmd += ["-i", PROPS["audio"]["music"]]
    cmd += ["-filter_complex_script", str(graph_file), "-map", f"[{vlabel}]", "-map", "[a]",
            "-c:v", "libx264", "-preset", PROPS["output"].get("preset", "medium"),
            "-crf", str(PROPS["output"].get("crf", 18)), "-profile:v", "high",
            "-pix_fmt", "yuv420p", "-g", str(FPS * 2), "-movflags", "+faststart",
            "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-shortest", str(out)]
    print(f"[render:{tag}] {out.name}")
    if run(cmd) != 0:
        print(f"✗ render xatosi — {graph_file.name} va ffmpeg xatosini o'qi")
        return out
    print(f"  ✓ {out.stat().st_size / 1e6:.2f} MB · sha256 {sha256(out)[:16]}…")
    return out


def qa(files: list[Path]) -> None:
    """Topshirish darvozasi: kadr aniqligi, CFR, nuqsonlar, loudness."""
    rows: list[str] = []
    for f in files:
        if not f.is_file():
            continue
        probe = subprocess.run(
            ["ffprobe", "-v", "error", "-select_streams", "v:0", "-count_frames",
             "-show_entries", "stream=width,height,r_frame_rate,avg_frame_rate,nb_read_frames:format=duration",
             "-of", "default=nw=1", str(f)], capture_output=True, text=True)
        vals = dict(re.findall(r"^(\w+)=(.*)$", probe.stdout, re.M))
        frames, rate = int(vals.get("nb_read_frames", 0) or 0), vals.get("r_frame_rate", "0/1")
        num, _, den = rate.partition("/")
        fps = (float(num) / float(den or 1)) if float(den or 1) else 0.0
        dur = float(vals.get("duration", 0) or 0)
        calc = frames / fps if fps else 0
        cfr = vals.get("r_frame_rate") == vals.get("avg_frame_rate")
        loud = subprocess.run(
            ["ffmpeg", "-hide_banner", "-nostats", "-i", str(f), "-af",
             "loudnorm=I=-14:TP=-1.0:LRA=11:print_format=json", "-f", "null", "-"],
            capture_output=True, text=True)
        m = re.search(r"\{[^{}]*\"input_i\"[^{}]*\}", loud.stderr, re.S)
        info = json.loads(m.group(0)) if m else {}
        rows.append(
            f"| {f.name} | {vals.get('width')}×{vals.get('height')} | {fps:g} | "
            f"{'CFR ✓' if cfr else 'VFR ✗'} | {frames} kadr / {dur:.2f}s "
            f"({'✓' if abs(calc - dur) <= 1 / max(fps, 1) else '✗'}) | "
            f"{info.get('input_i', '?')} LUFS · TP {info.get('input_tp', '?')} |")
    report = ["# QA natijasi", "",
              "| Fayl | O'lcham | fps | CFR | Kadr/davomiylik | Loudness |",
              "|---|---|---|---|---|---|", *rows, "",
              "Nuqson skanerlari (bo'sh chiqish = nuqson yo'q):",
              "```powershell",
              "ffmpeg -hide_banner -nostats -i <fayl> -vf blackdetect=d=0.1:pix_th=0.10 -f null - 2>&1 | Select-String black_",
              "ffmpeg -hide_banner -nostats -i <fayl> -vf freezedetect=n=-60dB:d=0.5 -f null - 2>&1 | Select-String freeze",
              "ffmpeg -hide_banner -nostats -i <fayl> -af silencedetect=noise=-30dB:d=0.4 -f null - 2>&1 | Select-String silence",
              "```"]
    (HERE / "qa-report.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    print("[qa] qa-report.md yozildi")


def main() -> int:
    if len(sys.argv) > 1 and sys.argv[1] == "qa-only":
        qa(sorted(RENDERS.glob("*.mp4")))
        return 0
    for src_key in ("source", "music"):
        src = PROPS["source"].get("path") if src_key == "source" else PROPS.get("audio", {}).get("music")
        if src and Path(src).is_file():
            print(f"[manba] {Path(src).name} sha256 {sha256(Path(src))[:16]}…")
    files = [render("draft" if "--draft" in sys.argv else "final")]
    qa(files)
    print("Keyingi qadam: qa-report.md ni to'ldir va MANIFEST.md ga hash/QA yoz")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
'''

PROPS_JSON = {
    "run_id": "",
    "source": {"path": "assets/source.mp4", "hash": "", "notes": "asl fayl tegilmaydi"},
    "output": {"basename": "", "width": 1080, "height": 1920, "fps": 30, "crf": 18,
               "preset": "medium", "placement": "reels", "spec_source": ""},
    "cut_list": [],
    "color": {"filter": "eq=contrast=1.04:saturation=1.04", "lut": "", "notes": ""},
    "audio": {"music": "", "music_gain": 0.28, "lufs": -14, "denoise": True},
    "captions": "",
    "text": {"hook": "", "body": [], "cta": ""},
}

MANIFEST_MD = """---
name: manifest-{run_id}
description: "{topic} — RUN MANIFEST: manba, chiqish, hash, litsenziya, spec manbasi, QA"
tags: [run, manifest, video]
updated: {date}
---

# MANIFEST — {topic}

- **run_id:** `{run_id}`
- **task:** `{task}` · **agent:** video-editor · **skill:** _(0-qadamda topilgan skill)_
- **format:** {fmt} ({w}x{h} · {fps} fps) · **sana:** {date}

## 1. Manba material (o'zgartirilmaydi)

| Fayl | Turi | Manba (URL/yo'l) | Litsenziya | SHA-256 | Triage natijasi |
|---|---|---|---|---|---|
| | mijoz videosi / stock / audio | | | | VFR/HDR/aylanish/loudness |

## 2. Chiqish fayllari

| Fayl | O'lcham | Davomiylik | SHA-256 | QA |
|---|---|---|---|---|
| renders/ | | | | qa-report.md |

## 3. Spec manbasi (yoddan emas)

- `ads/references/creative-source-registry.md` → joylashtirish: {placement} · olingan sana: {date}

## 4. Skill va qaror

- Skill so'rovi natijasi: `skill-search.py brief "..." --agent video-editor` → _(skill nomi)_
- Montaj qarorlari: _(kesim sabablari, dead-air, reframe strategiyasi, rang qarori)_

## 5. QA darvozasi

- [ ] Kadr aniqligi (`nb_read_frames / fps ≈ duration`, farq ≤1 kadr)
- [ ] CFR (`r_frame_rate == avg_frame_rate`)
- [ ] Nuqson skanerlari: blackdetect / freezedetect / silencedetect
- [ ] Loudness: −14 LUFS · TP ≤ −1.0 dBTP
- [ ] Safe-zone, imlo (o\u02bb/g\u02bb), CTA ≥2 s
- [ ] Manba hash o'zgarmagan

## 6. Ochiq risklar / needs_input

- _(yo'q yoki sabab)_
"""

QA_MD = """# QA jadvali — {topic} ({run_id})

> Buyruqlar: `video-editing/references/qa-checklist.md`. Har band — **o'lchov**, taxmin emas.

| # | Band | O'lchov / buyruq | Natija | ✓ |
|---|---|---|---|---|
| 1 | Manba daxlsizligi | SHA-256 solishtirish | | |
| 2 | O'lcham va fps | `ffprobe -show_entries stream=width,height,r_frame_rate,avg_frame_rate` | | |
| 3 | CFR (VFR emas) | `r_frame_rate == avg_frame_rate` | | |
| 4 | Kadr aniqligi | `nb_read_frames / fps ≈ duration` (≤1 kadr) | | |
| 5 | Qora/muzlagan kadr | `blackdetect`, `freezedetect` | | |
| 6 | Jimlik | `silencedetect=noise=-30dB:d=0.4` | | |
| 7 | Loudness | `loudnorm=I=-14:TP=-1.0` → LUFS, dBTP | | |
| 8 | Safe-zone | kontakt varaq (`fps=2,tile=5x4`) ko'zdan kechirildi | | |
| 9 | Ritm | 2 s dan uzun harakatsiz kadr yo'q | | |
| 10 | Subtitr | safe-zone, imlo, 3 til segmenti (kerak bo'lsa) | | |
| 11 | MANIFEST | hash, litsenziya, spec manbasi to'liq | | |

**Rad etish:** biror band ✗ bo'lsa — tuzatib qayta render; tekshirilmagan ish topshirilmaydi.
"""


def slug(value: str) -> str:
    return SLUG_RE.sub("-", value.lower()).strip("-") or "run"


def write_if_absent(path: Path, content: str, dry_run: bool, created: list[str],
                    force: bool = False) -> None:
    """Mavjud fayl ustiga yozilmaydi. `force` bo'lsa — eskisi `_archive/` ga ko'chiriladi."""
    if path.exists():
        if not force:
            created.append(f"  = mavjud (tegilmadi): {path.name}")
            return
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        archive = path.parent / "_archive"
        created.append(f"  ↻ yangilandi: {path.name} (eskisi _archive/{path.name}.{stamp})")
        if not dry_run:
            archive.mkdir(exist_ok=True)
            path.replace(archive / f"{path.name}.{stamp}")
    else:
        created.append(f"  + {path.name}")
    if not dry_run:
        path.write_text(content, encoding="utf-8")


def cmd_new(args: argparse.Namespace) -> int:
    root = Path(args.root) if args.root else DEFAULT_ROOT
    if args.format not in FORMATS:
        print(f"✗ format noma'lum: {args.format} (bor: {', '.join(FORMATS)})")
        return 2
    if not args.client or not args.topic:
        print("✗ --client va --topic kerak")
        return 2
    date = datetime.now().strftime("%Y-%m-%d")
    run_id = args.run_id or f"{date}-{slug(args.client)}-{slug(args.topic)}"
    task = args.task
    base = root / run_id / "workers" / task
    w, h = FORMATS[args.format]
    props = dict(PROPS_JSON)
    props["run_id"] = run_id
    props["output"] = {**PROPS_JSON["output"], "width": w, "height": h,
                       "basename": f"{run_id}_{args.format}"}
    created: list[str] = []
    if not args.dry_run:
        for sub in ("assets", "renders"):
            (base / sub).mkdir(parents=True, exist_ok=True)
    created.append(f"run_id: {run_id} · task: {task} · format: {args.format} ({w}x{h})")
    # props.json — MA'LUMOT (agent to'ldiradi): `--force` ham uni ustiga yozmaydi
    write_if_absent(base / "props.json",
                    json.dumps(props, ensure_ascii=False, indent=2) + "\n", args.dry_run, created)
    write_if_absent(base / "build.py",
                    BUILD_PY.replace("{run_id}", run_id).replace("{task}", task),
                    args.dry_run, created, force=args.force)
    write_if_absent(base / "MANIFEST.md",
                    MANIFEST_MD.format(run_id=run_id, topic=args.topic, task=task, date=date,
                                       fmt=args.format, w=w, h=h, fps=props["output"]["fps"],
                                       placement=args.placement), args.dry_run, created, force=args.force)
    write_if_absent(base / "qa.md", QA_MD.format(topic=args.topic, run_id=run_id),
                    args.dry_run, created, force=args.force)
    head = "REJA (dry-run)" if args.dry_run else "ISH MAYDONI TAYYOR"
    print(f"{head}: {base}")
    print("\n".join(created))
    if not args.dry_run:
        print("\nKeyingi qadamlar: manba nusxasini assets/ ga qo'y → props.json ni to'ldir →")
        print("  py -3 build.py --draft   (tez ko'rish)  →  py -3 build.py  (final)  →  qa.md")
    return 0


def cmd_list(args: argparse.Namespace) -> int:
    root = Path(args.root) if args.root else DEFAULT_ROOT
    if not root.is_dir():
        print(f"Run yo'q: {root}")
        return 0
    runs = sorted(p for p in root.iterdir() if p.is_dir())
    print(f"Run'lar: {len(runs)} ({root})")
    for run in runs:
        outputs = list(run.glob("workers/*/renders/*.mp4"))
        qa = list(run.glob("workers/*/qa-report.md"))
        print(f"  {run.name}: {len(outputs)} render · {'QA bor' if qa else 'QA yo`q'}")
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    root = Path(args.root) if args.root else DEFAULT_ROOT
    run = root / args.run_id
    if not run.is_dir():
        print(f"✗ run topilmadi: {args.run_id}")
        return 1
    print(f"Run: {args.run_id}")
    for item in sorted(run.rglob("*")):
        if item.is_file() and item.suffix != ".pyc":
            rel = item.relative_to(run).as_posix()
            print(f"  {item.stat().st_size:>10,} B  {rel}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="video-run.py", description="Video ishi uchun ish maydoni (scaffold)")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("new", help="yangi ish maydoni ochish")
    p.add_argument("--client", required=True)
    p.add_argument("--topic", required=True)
    p.add_argument("--task", default="video-editor")
    p.add_argument("--format", default="9x16", choices=sorted(FORMATS))
    p.add_argument("--placement", default="reels")
    p.add_argument("--run-id", default="")
    p.add_argument("--root", default="", help="boshqa ildiz (test uchun)")
    p.add_argument("--force", action="store_true",
                   help="skeletlarni yangilash (eskisi _archive/ ga; props.json tegilmaydi)")
    p.add_argument("--dry-run", action="store_true")
    p.set_defaults(func=cmd_new)

    p = sub.add_parser("list", help="run'lar ro'yxati")
    p.add_argument("--root", default="")
    p.set_defaults(func=cmd_list)

    p = sub.add_parser("status", help="run ichidagi fayllar")
    p.add_argument("run_id")
    p.add_argument("--root", default="")
    p.set_defaults(func=cmd_status)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
