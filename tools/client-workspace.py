#!/usr/bin/env python3
"""Tyrion Client Workspace Scaffolder — Mijoz loyihasini 1 buyruqda tayyor hisob-kitoblar bilan ochish (0 token).

Buyruqlar:
  python3 tools/client-workspace.py new --client "nur-residence" --niche real-estate --budget 3000 --aov 45000 --margin-pct 25 --geo tashkent
  python3 tools/client-workspace.py list
"""

from __future__ import annotations

import argparse
import importlib
import json
import re
import sys
import tyrion_core as tcore
from datetime import date
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
VAULT = TOOLS.parent
DEFAULT_CLIENTS_ROOT = VAULT / "clients"
sys.path.insert(0, str(TOOLS))

for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        try:
            _stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:  # pragma: no cover
            pass


def slugify(value: str) -> str:
    return tcore.safe_slug(value, fallback="client-project")


def scaffold_client(
    client: str,
    niche: str,
    monthly_budget: float,
    aov: float,
    margin_pct: float,
    geo: str,
    root: Path,
    dry_run: bool = False,
) -> dict:
    ma = importlib.import_module("meta-audience")
    cm = importlib.import_module("creative-matrix")

    slug = slugify(client)
    cdir = tcore.validate_safe_path(root / slug, allowed_root=root)
    daily_budget = round(monthly_budget / 30.0, 2)
    gross_profit = round(aov * (margin_pct / 100.0), 2)
    breakeven_roas = round(100.0 / max(margin_pct, 1.0), 2)
    target_cpa = round(gross_profit * 0.5, 2)

    arch = ma.build_architecture(
        niche=niche if niche in ma.NICHE_TAXONOMY else "ecom",
        daily_budget=daily_budget,
        geo=geo if geo in getattr(ma, 'GEO_SEGMENTS', {'tashkent': 1, 'regions': 1, 'uzbekistan': 1}) else "tashkent",
        has_pixel=True,
        has_crm=True,
        target_cpa= max(target_cpa, 5.0),
    )
    mat = cm.build_matrix(niche=niche, product=client, price=aov)

    files_to_write = {
        "BRIEF.md": f"""# 📋 MIJOZ BRIFI VA UNIT-IQTISODIYOT: {client.upper()}

- **Sana:** {date.today().isoformat()}
- **Yo'nalish (Nisha):** `{niche}`
- **Geografiya:** `{geo}`
- **Oylik Reklama Byudjeti:** `${monthly_budget:,.2f}` (Kunlik: `${daily_budget:,.2f}`)
- **O'rtacha Chek (AOV):** `${aov:,.2f}` (Marja: `{margin_pct:.1f}%` -> Yalpi foyda: `${gross_profit:,.2f}`)
- **Break-Even ROAS:** `{breakeven_roas:.2f}x` | **Target CPA (50% marja chegarasi):** `${target_cpa:,.2f}`

## 70 / 20 / 10 Byudjet Taqsimoti
- **70% Scaling Core:** `${round(monthly_budget * 0.70, 2):,.2f}/oy` (`${round(daily_budget * 0.70, 2):,.2f}/kun`)
- **20% 1-5-5 ABO Sandbox:** `${round(monthly_budget * 0.20, 2):,.2f}/oy` (`${round(daily_budget * 0.20, 2):,.2f}/kun`)
- **10% BOF Retargeting:** `${round(monthly_budget * 0.10, 2):,.2f}/oy` (`${round(daily_budget * 0.10, 2):,.2f}/kun`)
""",
        "AUDIENCE-MAP.md": f"""# 🎯 META ADS 4-QATLAMLI AUDITORIYA XARITASI: {client.upper()}

```json
{json.dumps(arch, ensure_ascii=False, indent=2)}
```
""",
        "CREATIVE-MATRIX.md": f"""# 🎨 ANDROMEDA 2 KREATIV MATRITSASI (3x3): {client.upper()}

```json
{json.dumps(mat, ensure_ascii=False, indent=2)}
```
""",
        "TRACKING-CHECKLIST.md": f"""# 📡 TRACKING VA VORONKA DARVOZASI: {client.upper()}

- [ ] Meta Pixel o'rnatilgan va asosiy hodisalar (`Lead` / `Purchase`) yonmoqda
- [ ] Conversions API (`CAPI`) ulangan va `event_id` deduplikatsiyasi (`>=95%`) tekshirilgan
- [ ] Event Match Quality (`EMQ`) balli `>= 6.5/10` (telefon + ism + fbc/fbp)
- [ ] Telegram Bot `?start=utm` zanjiri va AmoCRM/Bitrix24 avto-sdelka integratsiyasi sinovdan o'tgan
- [ ] Sotuv bo'limi javob tezligi (Speed-to-Lead) `<= 15 daqiqa`
""",
        "journal.md": f"""# 📓 KAMPANIYA JURNALI: {client.upper()}

| Sana | Qadam / O'zgarish | Asosiy Metrikalar | Qaror (Kill/Keep/Scale) |
|---|---|---|---|
| {date.today().isoformat()} | Loyiha ish maydoni ochildi (`client-workspace.py`) | Byudjet=${monthly_budget}/oy, Break-even ROAS={breakeven_roas}x | Preflight & Sandbox Start |
""",
    }

    if not dry_run:
        (cdir / "outputs").mkdir(parents=True, exist_ok=True)
        (cdir / "assets").mkdir(parents=True, exist_ok=True)
        for fname, content in files_to_write.items():
            target = cdir / fname
            if not target.exists():
                tcore.atomic_write_text(target, content)

    return {
        "client": client,
        "slug": slug,
        "workspace_dir": str(cdir),
        "dry_run": dry_run,
        "unit_economics": {
            "monthly_budget_usd": monthly_budget,
            "daily_budget_usd": daily_budget,
            "aov_usd": aov,
            "margin_pct": margin_pct,
            "breakeven_roas": breakeven_roas,
            "target_cpa_usd": target_cpa,
        },
        "files": list(files_to_write.keys()),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="client-workspace.py", description="Mijoz ish maydonini yaratish")
    sub = parser.add_subparsers(dest="command", required=True)

    p_new = sub.add_parser("new", help="Yangi mijoz ish maydonini ochish")
    p_new.add_argument("--client", required=True)
    p_new.add_argument("--niche", default="ecom")
    p_new.add_argument("--budget", type=float, default=1500.0)
    p_new.add_argument("--aov", type=float, default=100.0)
    p_new.add_argument("--margin-pct", type=float, default=40.0)
    p_new.add_argument("--geo", default="tashkent")
    p_new.add_argument("--root", default=str(DEFAULT_CLIENTS_ROOT))
    p_new.add_argument("--dry-run", action="store_true")
    p_new.add_argument("--json", action="store_true")

    p_list = sub.add_parser("list", help="Mavjud mijoz ish maydonlari ro'yxati")
    p_list.add_argument("--root", default=str(DEFAULT_CLIENTS_ROOT))

    args = parser.parse_args(argv)
    if args.command == "new":
        res = scaffold_client(
            client=args.client,
            niche=args.niche,
            monthly_budget=args.budget,
            aov=args.aov,
            margin_pct=args.margin_pct,
            geo=args.geo,
            root=Path(args.root),
            dry_run=args.dry_run,
        )
        if args.json:
            print(json.dumps(res, ensure_ascii=False, indent=2))
        else:
            head = "REJA (dry-run)" if args.dry_run else "YARATILDI"
            print(f"✓ {head}: {res['workspace_dir']}")
            print(f"  Break-even ROAS: {res['unit_economics']['breakeven_roas']}x · Target CPA: ${res['unit_economics']['target_cpa_usd']}")
            print(f"  Fayllar: {', '.join(res['files'])}")
        return 0

    if args.command == "list":
        root = Path(args.root)
        if not root.is_dir():
            print("Mijozlar papkasi hali bo'sh.")
            return 0
        clients = sorted(p.name for p in root.iterdir() if p.is_dir())
        print(f"Mijoz ish maydonlari ({len(clients)}): " + (", ".join(clients) or "yo'q"))
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
