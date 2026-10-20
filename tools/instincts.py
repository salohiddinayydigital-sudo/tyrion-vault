#!/usr/bin/env python3
"""Tyrion Instincts Engine — Uzluksiz o'rganish va marketing instinktlari reestri (0 token).

ECC (affaan-m/ECC) continuous-learning-v2 va `/learn` naqshi asosida:
Sessiya, audit yoki kampaniya sinovlaridan olingan tasdiqlangan qoidalarni
`manifests/instincts.json` da saqlaydi, ishonch balli (1-5) bilan baholaydi
va yuqori ishonchli instinktlarni `MEMORY.md` §6 ga ko'taradi.

Buyruqlar:
  py -3 tools/instincts.py list [--domain meta|google|telegram|kreativ|tracking|tizim]
  py -3 tools/instincts.py add --id <slug> --domain <d> --trigger "<qachon>" --action "<nima>" --evidence "<manba>" [--confidence 3]
  py -3 tools/instincts.py promote <id> [--dry-run]
  py -3 tools/instincts.py check [--json]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
VAULT = TOOLS.parent
MANIFEST = VAULT / "manifests" / "instincts.json"
MEMORY = VAULT / "MEMORY.md"
SCHEMA = "tyrion-instincts/v1"
VALID_DOMAINS = ("meta", "google", "telegram", "kreativ", "tracking", "tizim")
SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")

for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        try:
            _stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:  # pragma: no cover
            pass


def load_data() -> dict:
    if not MANIFEST.is_file():
        return {"schema": SCHEMA, "updated": date.today().isoformat(), "instincts": []}
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def save_data(data: dict) -> None:
    data["updated"] = date.today().isoformat()
    import tyrion_core as tcore
    tcore.atomic_write_json(MANIFEST, data)


def cmd_list(args: argparse.Namespace) -> int:
    data = load_data()
    items = data.get("instincts", [])
    if args.domain:
        items = [i for i in items if i.get("domain") == args.domain]
    if args.json:
        print(json.dumps(items, ensure_ascii=False, indent=2))
        return 0
    print(f"Instinktlar reestri: {len(items)} ta" + (f" (domain={args.domain})" if args.domain else ""))
    for item in items:
        stars = "★" * int(item.get("confidence", 1)) + "☆" * (5 - int(item.get("confidence", 1)))
        print(f"  [{item.get('domain', '?'):8}] {item['id']:30} {stars} ({item.get('confidence')}/5)")
        print(f"            Trigger : {item.get('trigger')}")
        print(f"            Harakat : {item.get('action')}")
        print(f"            Manba   : {item.get('evidence')}")
    return 0


def cmd_add(args: argparse.Namespace) -> int:
    if not SLUG_RE.match(args.id):
        print(f"✗ id faqat kichik lotin va tire bo'lishi shart: {args.id}", file=sys.stderr)
        return 2
    if args.domain not in VALID_DOMAINS:
        print(f"✗ noto'g'ri domain: {args.domain}. Ruxsat: {', '.join(VALID_DOMAINS)}", file=sys.stderr)
        return 2
    if not (1 <= args.confidence <= 5):
        print("✗ confidence 1 va 5 orasida bo'lishi shart", file=sys.stderr)
        return 2

    data = load_data()
    instincts = data.setdefault("instincts", [])
    existing = next((i for i in instincts if i["id"] == args.id), None)
    entry = {
        "id": args.id,
        "domain": args.domain,
        "trigger": args.trigger.strip(),
        "action": args.action.strip(),
        "evidence": args.evidence.strip(),
        "confidence": args.confidence,
        "created": existing.get("created", date.today().isoformat()) if existing else date.today().isoformat(),
    }
    if existing:
        idx = instincts.index(existing)
        instincts[idx] = entry
        action_label = "yangilandi"
    else:
        instincts.append(entry)
        action_label = "qo'shildi"

    if not args.dry_run:
        save_data(data)
    print(f"✓ instinkt {action_label}: {args.id} ({args.domain}, confidence={args.confidence}/5)")
    return 0


def cmd_promote(args: argparse.Namespace) -> int:
    data = load_data()
    instincts = data.get("instincts", [])
    target = next((i for i in instincts if i["id"] == args.id), None)
    if not target:
        print(f"✗ instinkt topilmadi: {args.id}", file=sys.stderr)
        return 1
    if int(target.get("confidence", 0)) < 4:
        print(f"✗ '{args.id}' ishonch balli past ({target.get('confidence')}/5 < 4). "
              f"Faqat >=4 ball olgan tasdiqlangan instinktlar memory.md ga ko'tariladi.")
        return 1
    if not MEMORY.is_file():
        print("✗ MEMORY.md topilmadi", file=sys.stderr)
        return 1

    mem_text = MEMORY.read_text(encoding="utf-8")
    if target["id"] in mem_text or target["action"][:40] in mem_text:
        print(f"✓ '{args.id}' allaqachon memory.md da mavjud")
        return 0

    lines = mem_text.splitlines()
    if len(lines) >= 88:
        print("⚠ memory.md 90 qator limitiga yaqin — avval ixchamlashtiring")
        return 1

    bullet = f"- **{target['id']} ({target['created']}):** {target['trigger']} → {target['action']} (`{target['evidence']}`)"
    if args.dry_run:
        print(f"REJA (dry-run): memory.md §6 ga qo'shiladi:\n  {bullet}")
        return 0

    MEMORY.write_text(mem_text.rstrip() + "\n" + bullet + "\n", encoding="utf-8")
    print(f"✓ '{args.id}' memory.md §6 bo'limiga ko'tarildi")
    return 0


def cmd_check(args: argparse.Namespace) -> int:
    errors: list[str] = []
    if not MANIFEST.is_file():
        errors.append("manifests/instincts.json topilmadi")
        data = {"instincts": []}
    else:
        try:
            data = load_data()
        except Exception as exc:
            errors.append(f"JSON xato: {exc}")
            data = {"instincts": []}

    if data.get("schema") != SCHEMA and not errors:
        errors.append(f"sxema mos emas: {data.get('schema')} != {SCHEMA}")

    seen: set[str] = set()
    instincts = data.get("instincts", [])
    for idx, item in enumerate(instincts):
        iid = str(item.get("id") or "")
        if not SLUG_RE.match(iid):
            errors.append(f"instinct[{idx}]: yaroqsiz id '{iid}'")
        if iid in seen:
            errors.append(f"dublikat instinkt id: {iid}")
        seen.add(iid)
        if item.get("domain") not in VALID_DOMAINS:
            errors.append(f"{iid}: noto'g'ri domain '{item.get('domain')}'")
        conf = item.get("confidence")
        if not isinstance(conf, int) or not (1 <= conf <= 5):
            errors.append(f"{iid}: confidence 1..5 butun son bo'lishi kerak")
        for req in ("trigger", "action", "evidence"):
            if not str(item.get(req) or "").strip():
                errors.append(f"{iid}: '{req}' bo'sh")

    res = {
        "passed": len(errors) == 0,
        "count": len(instincts),
        "high_confidence": sum(1 for i in instincts if int(i.get("confidence", 0)) >= 4),
        "errors": errors,
    }
    if getattr(args, "json", False):
        print(json.dumps(res, ensure_ascii=False, indent=2))
        return 0 if res["passed"] else 1

    if errors:
        print(f"✗ instinktlar reestrida {len(errors)} xato:")
        for e in errors:
            print(f"  - {e}")
        return 1
    print(f"✓ instinktlar reestri butun ({res['count']} instinkt, {res['high_confidence']} yuqori ishonchli)")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="instincts.py", description="Tyrion uzluksiz o'rganish va instinktlar reestri")
    sub = parser.add_subparsers(dest="command", required=True)

    p_list = sub.add_parser("list", help="instinktlar ro'yxati")
    p_list.add_argument("--domain", choices=VALID_DOMAINS, default=None)
    p_list.add_argument("--json", action="store_true")
    p_list.set_defaults(func=cmd_list)

    p_add = sub.add_parser("add", help="yangi instinkt qo'shish yoki yangilash")
    p_add.add_argument("--id", required=True)
    p_add.add_argument("--domain", choices=VALID_DOMAINS, required=True)
    p_add.add_argument("--trigger", required=True)
    p_add.add_argument("--action", required=True)
    p_add.add_argument("--evidence", required=True)
    p_add.add_argument("--confidence", type=int, default=3)
    p_add.add_argument("--dry-run", action="store_true")
    p_add.set_defaults(func=cmd_add)

    p_prom = sub.add_parser("promote", help="ishonchli instinktni memory.md §6 ga ko'tarish")
    p_prom.add_argument("id")
    p_prom.add_argument("--dry-run", action="store_true")
    p_prom.set_defaults(func=cmd_promote)

    p_chk = sub.add_parser("check", help="reestr butunligini tekshirish")
    p_chk.add_argument("--json", action="store_true")
    p_chk.set_defaults(func=cmd_check)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
