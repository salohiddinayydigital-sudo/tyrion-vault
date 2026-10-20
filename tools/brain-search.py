#!/usr/bin/env python3
"""brain-search — LLM'siz (deterministik) bilim qidiruvi. Token tejamkor.

Muammo: grafik (`graphify`) yangilash LLM talab qiladi (kalit yoki katta lokal model),
sekin va qimmat. Ko'p savolga esa oddiy matn qidiruvi yetadi.

Yechim: fayl tizimidan deterministik indeks (frontmatter + wikilinklar) — 0 token,
0 API, darhol javob. Grafik faqat munosabat (path/explain) kerak bo'lganda.

Buyruqlar:
  py -3 tools\\brain-search.py search "katta byudjet meta scaling" --top 5
  py -3 tools\\brain-search.py show <nom>
  py -3 tools\\brain-search.py links <nom>
  py -3 tools\\brain-search.py hubs --top 10
  py -3 tools\\brain-search.py stats

Chiqish: qisqa qatorlar (token tejamkor). Kod: 0 — topildi, 1 — topilmadi, 2 — xato.
"""

from __future__ import annotations

import argparse
import math
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

VAULT = Path(__file__).resolve().parent.parent

for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        try:
            _stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:  # pragma: no cover
            pass

SKIP = {".git", ".obsidian", ".smart-env", "graphify-out", ".code-review-graph",
        "node_modules", "__pycache__", "output", "tmp", ".claude", ".codebuddy",
        ".cursor", ".gemini", ".qoder", "archive"}
FM = re.compile(r"\A---\r?\n(.*?)\r?\n---", re.S)
WIKILINK = re.compile(r"\[\[([^\]\|#]+)(?:#[^\]\|]*)?(?:\|[^\]]*)?\]\]")
FENCED = re.compile(r"```.*?```", re.S)
INLINE = re.compile(r"`[^`\n]*`")
WORD = re.compile(r"[a-zA-Zа-яА-ЯёЁʻʼ'\u0400-\u04FF]+", re.UNICODE)

# Qidiruvda ma'nosiz so'zlar
STOP = {"va", "bilan", "uchun", "bu", "shu", "bir", "eng", "yoki", "ham", "the",
        "and", "for", "with", "of", "to", "in", "on", "a", "is", "are", "bo", "deb"}


def _layer(rel: str) -> str:
    p = rel.replace("\\", "/")
    if p.startswith("wiki/"):
        return "wiki"
    if p.startswith("playbooks/"):
        return "playbook"
    if p.startswith("contexts/"):
        return "context"
    if p.startswith("rules/"):
        return "rule"
    if p.startswith("agents/"):
        return "agent"
    if p in ("INDEX.md", "AGENTS.md", "CLAUDE.md", "MEMORY.md", "README.md"):
        return "root"
    return "other"


def _fm_value(block: str, key: str) -> str:
    m = re.search(rf'^{key}:\s*"?(.*?)"?\s*$', block, re.M)
    return m.group(1).strip() if m else ""


def load_items() -> list[dict]:
    items: list[dict] = []
    for p in VAULT.rglob("*.md"):
        rel = p.relative_to(VAULT).as_posix()
        if any(part in SKIP for part in p.relative_to(VAULT).parts):
            continue
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        fm = FM.match(text)
        block = fm.group(1) if fm else ""
        body = text[fm.end():] if fm else text
        clean = INLINE.sub(" ", FENCED.sub(" ", body))
        items.append({
            "name": p.stem,
            "path": rel,
            "layer": _layer(rel),
            "description": _fm_value(block, "description") or _fm_value(block, "name"),
            "tags": _fm_value(block, "tags"),
            "source": _fm_value(block, "source"),
            "updated": _fm_value(block, "updated"),
            "links": {x.strip().split("/")[-1].replace(".md", "") for x in WIKILINK.findall(clean)},
            "text": clean,
        })
    return items


def tokens(value: str) -> list[str]:
    return [w.lower() for w in WORD.findall(value) if len(w) > 1 and w.lower() not in STOP]


def score(item: dict, query_tokens: list[str]) -> float:
    """Oddiy vaznli qidiruv: nom > tag > tavsif > matn. Deterministik, LLM'siz."""
    name = item["name"].lower()
    tags = item["tags"].lower()
    desc = item["description"].lower()
    text = item["text"].lower()
    total = 0.0
    for t in set(query_tokens):
        w = 0.0
        if t in name:
            w += 6
        if t in tags:
            w += 3
        if t in desc:
            w += 2
        c = text.count(t)
        if c:
            w += 1 + math.log(1 + c)
        total += w
    return total


def cmd_search(args: argparse.Namespace) -> int:
    qt = tokens(args.query)
    if not qt:
        print("✗ so'rov bo'sh")
        return 2
    items = load_items()
    ranked = sorted(((score(i, qt), i) for i in items), key=lambda x: -x[0])
    hits = [(s, i) for s, i in ranked if s > 0][: args.top]
    if not hits:
        print("✗ mos qayd topilmadi — INDEX.md ga qarang yoki so'rovni o'zgartiring")
        return 1
    print(f"Topildi {len(hits)} (so'rov: {args.query}):")
    for s, i in hits:
        print(f"  [{i['layer']:5}] {i['name']:34} {i['description'][:70]}")
        print(f"          {i['path']}")
    return 0


def cmd_show(args: argparse.Namespace) -> int:
    items = {i["name"]: i for i in load_items()}
    i = items.get(args.name) or items.get(args.name.replace(".md", ""))
    if not i:
        # qisman moslik
        cand = [k for k in items if args.name.lower() in k.lower()]
        if len(cand) == 1:
            i = items[cand[0]]
        else:
            print(f"✗ topilmadi: {args.name}" + (f" (o'xshash: {', '.join(cand[:5])})" if cand else ""))
            return 1
    print(f"{i['name']}  [{i['layer']}]")
    print(f"  yo'l: {i['path']}")
    print(f"  tavsif: {i['description']}")
    if i["tags"]:
        print(f"  teglar: {i['tags']}")
    if i["source"]:
        print(f"  manba: {i['source'][:110]}")
    if i["updated"]:
        print(f"  yangilangan: {i['updated']}")
    print(f"  havolalar ({len(i['links'])}): {', '.join(sorted(i['links'])[:12]) or '—'}")
    return 0


def cmd_links(args: argparse.Namespace) -> int:
    items = load_items()
    target = args.name.replace(".md", "")
    out = next((i["links"] for i in items if i["name"] == target), set())
    inbound = sorted({i["name"] for i in items if target in i["links"]})
    print(f"{target}")
    print(f"  chiquvchi ({len(out)}): {', '.join(sorted(out)) or '—'}")
    print(f"  kiruvchi ({len(inbound)}): {', '.join(inbound) or '—'}")
    return 0


def cmd_hubs(args: argparse.Namespace) -> int:
    items = load_items()
    indeg: Counter[str] = Counter()
    for i in items:
        for l in i["links"]:
            indeg[l] += 1
    print(f"Kiruvchi havola bo'yicha hublar (top {args.top}):")
    for name, c in indeg.most_common(args.top):
        print(f"  {c:3}  {name}")
    return 0


def cmd_stats(_args: argparse.Namespace) -> int:
    items = load_items()
    layers = Counter(i["layer"] for i in items)
    indeg: Counter[str] = Counter()
    for i in items:
        for l in i["links"]:
            indeg[l] += 1
    orphans = [i["name"] for i in items if i["layer"] == "wiki" and indeg.get(i["name"], 0) == 0]
    print(f"Fayllar: {len(items)} | qatlamlar: " + ", ".join(f"{k} {v}" for k, v in sorted(layers.items())))
    print(f"Tugunlar (havolada ishtirok): {len(indeg)} | orphan wiki: {len(orphans)}")
    if orphans:
        print("  orphan: " + ", ".join(sorted(orphans)[:10]))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="brain-search.py", description="LLM'siz bilim qidiruvi")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("search", help="so'rov bo'yicha qaydlar")
    p.add_argument("query")
    p.add_argument("--top", type=int, default=5)
    p.set_defaults(func=cmd_search)

    p = sub.add_parser("show", help="qayd kartochkasi")
    p.add_argument("name")
    p.set_defaults(func=cmd_show)

    p = sub.add_parser("links", help="kiruvchi/chiquvchi havolalar")
    p.add_argument("name")
    p.set_defaults(func=cmd_links)

    p = sub.add_parser("hubs", help="eng bog'langan tugunlar")
    p.add_argument("--top", type=int, default=10)
    p.set_defaults(func=cmd_hubs)

    p = sub.add_parser("stats", help="umumiy holat")
    p.set_defaults(func=cmd_stats)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
