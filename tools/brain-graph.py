#!/usr/bin/env python3
"""brain-graph — grafni WIKILINKLARDAN deterministik quradi (LLM'siz, 0 token).

Muammo: `graphify extract` semantik qatlam uchun LLM talab qiladi. Lokal model:
- sekin (CPU), kontekst 4096 (graphify 12k token yuboradi -> sig'maydi), JSON buziladi;
- bulut kaliti yo'q.
Natijada graf eskiradi.

Yechim: vault o'z wikilinklari bilan allaqachon bog'langan. Grafni shulardan
deterministik qurish mumkin: lahzalali, bepul, har doim yangi, %100 ishonchli.
`graphify query|path|explain|god-nodes` shu graf bilan ham ishlaydi (sxema bir xil).

Buyruqlar:
  py -3 tools\\brain-graph.py build      # graphify-out/graph.json ni qayta quradi
  py -3 tools\\brain-graph.py build --report
  py -3 tools\\brain-graph.py stats

Chiqish kodi: 0 — tayyor, 2 — xato.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

VAULT = Path(__file__).resolve().parent.parent
OUT = VAULT / "graphify-out" / "graph.json"
REPORT = VAULT / "graphify-out" / "GRAPH_REPORT.md"

for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        try:
            _stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:  # pragma: no cover
            pass

FM = re.compile(r"\A---\r?\n(.*?)\r?\n---", re.S)
WIKILINK = re.compile(r"\[\[([^\]\|#]+)(?:#[^\]\|]*)?(?:\|[^\]]*)?\]\]")
FENCED = re.compile(r"```.*?```", re.S)
INLINE = re.compile(r"`[^`\n]*`")
SLUG = re.compile(r"[^a-z0-9]+")

# Korpus: bilim + operatsion bog'lanish (LLM yo'q, shuning uchun kengroq olish mumkin)
INCLUDE_DIRS = ("wiki", "playbooks", "contexts", "rules", "commands", "agents")
INCLUDE_ROOT = {"INDEX.md", "AGENTS.md", "CLAUDE.md", "MEMORY.md", "README.md", "LOG.md"}
SKIP_PARTS = {".git", ".obsidian", ".smart-env", "graphify-out", ".code-review-graph",
              "node_modules", "__pycache__", "output", "tmp", ".claude", ".codebuddy",
              ".cursor", ".gemini", ".qoder", "archive", ".github", ".agents"}

FILE_TYPE = {"wiki": "concept", "playbooks": "playbook", "contexts": "context", "rules": "rule",
             "commands": "command", "agents": "agent", "root": "doc"}


def slug(value: str) -> str:
    return SLUG.sub("_", value.lower()).strip("_")


def fm_value(block: str, key: str) -> str:
    m = re.search(rf'^{key}:\s*"?(.*?)"?\s*$', block, re.M)
    return m.group(1).strip() if m else ""


def layer_of(rel: str) -> str:
    parts = rel.split("/")
    if parts[0] in INCLUDE_DIRS:
        return parts[0]
    return "root"


def corpus() -> list[Path]:
    files: list[Path] = []
    for d in INCLUDE_DIRS:
        base = VAULT / d
        if base.is_dir():
            files.extend(p for p in base.rglob("*.md") if p.is_file())
    files.extend(VAULT / name for name in INCLUDE_ROOT if (VAULT / name).is_file())
    return sorted(set(files))


def load(files: list[Path]) -> tuple[list[dict], dict[str, str]]:
    nodes: list[dict] = []
    stem_to_id: dict[str, str] = {}
    for p in files:
        rel = p.relative_to(VAULT).as_posix()
        if any(part in SKIP_PARTS for part in p.relative_to(VAULT).parts):
            continue
        text = p.read_text(encoding="utf-8", errors="replace")
        fm = FM.match(text)
        block = fm.group(1) if fm else ""
        body = text[fm.end():] if fm else text
        clean = INLINE.sub(" ", FENCED.sub(" ", body))
        layer = layer_of(rel)
        nid = f"{layer}_{slug(p.stem)}"
        label = fm_value(block, "name") or p.stem
        tags = fm_value(block, "tags")
        node = {
            "id": nid,
            "label": label,
            "norm_label": slug(label),
            "file_type": FILE_TYPE.get(layer, "doc"),
            "source_file": rel,
            "layer": layer,
            "tags": tags,
            "_links": {x.strip().split("/")[-1].replace(".md", "") for x in WIKILINK.findall(clean)},
        }
        nodes.append(node)
        stem_to_id[p.stem] = nid
    return nodes, stem_to_id


def communities(nodes: list[dict], links: list[dict]) -> None:
    """Teg asosidagi klaster — deterministik va tushunarli (LPA o'rniga)."""
    groups: dict[str, list[str]] = defaultdict(list)
    for n in nodes:
        tags = re.findall(r"[a-z0-9\-]+", str(n.get("tags", "")).lower())
        n["_cname"] = tags[0] if tags else n["layer"]
        groups[n["_cname"]].append(n["id"])
    ordered = sorted(groups.items(), key=lambda kv: (-len(kv[1]), kv[0]))
    cid_of: dict[str, int] = {}
    for cid, (name, _members) in enumerate(ordered):
        cid_of[name] = cid
    for n in nodes:
        n["community"] = cid_of.get(n["_cname"], 0)
        n["community_name"] = n["_cname"] if n["_cname"] else "boshqa"
        n.pop("_cname", None)


def build() -> dict:
    files = corpus()
    nodes, stem_to_id = load(files)
    ids = {n["id"] for n in nodes}
    links: list[dict] = []
    seen: set[tuple[str, str]] = set()
    for n in nodes:
        for target_stem in n["_links"]:
            tid = stem_to_id.get(target_stem)
            if not tid or tid == n["id"]:
                continue
            key = (n["id"], tid)
            if key in seen:
                continue
            seen.add(key)
            links.append({
                "source": n["id"], "target": tid, "relation": "links_to",
                "confidence": "EXTRACTED", "confidence_score": 1.0,
                "weight": 1.0, "source_file": n["source_file"], "source_location": None,
            })
    communities(nodes, links)
    for n in nodes:
        n.pop("_links", None)
    try:
        commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=VAULT, capture_output=True,
                                text=True, timeout=20).stdout.strip()
    except Exception:
        commit = None
    return {
        "directed": False, "multigraph": False,
        "graph": {"name": "tyrion-wikilink-graph", "generator": "tools/brain-graph.py"},
        "nodes": nodes, "links": links, "hyperedges": [],
        "built_at_commit": commit or None,
        "built_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "stats": {"nodes": len(nodes), "links": len(links),
                  "communities": len({n["community"] for n in nodes})},
    }


def write_report(data: dict) -> None:
    indeg: Counter[str] = Counter()
    for l in data["links"]:
        indeg[l["target"]] += 1
    by_id = {n["id"]: n for n in data["nodes"]}
    hubs = indeg.most_common(15)
    comms: Counter[str] = Counter(n["community_name"] for n in data["nodes"])
    lines = [
        "# GRAPH_REPORT — Tyrion bilim grafi (deterministik)",
        "",
        f"> Qurilgan: {data['built_at']} · generator: `tools/brain-graph.py` (LLM'siz, 0 token)",
        "",
        f"**Tugunlar:** {data['stats']['nodes']} · **Qirralar:** {data['stats']['links']} · "
        f"**Klasterlar:** {data['stats']['communities']}",
        "",
        "## Eng bog'langan tugunlar (hublar)",
        "",
        "| # | Tugun | Kiruvchi | Fayl |",
        "|---|-------|----------|------|",
    ]
    for i, (nid, c) in enumerate(hubs, 1):
        n = by_id.get(nid, {})
        lines.append(f"| {i} | {n.get('label', nid)} | {c} | `{n.get('source_file', '')}` |")
    lines += ["", "## Klasterlar", "", "| Klaster | Tugunlar |", "|---------|----------|"]
    for name, c in comms.most_common():
        lines.append(f"| {name} | {c} |")
    lines += ["", "## Manba", "",
              "- Wikilinklardan deterministik qurilgan: `tools/brain-graph.py build`",
              "- Chuqur semantik graf (LLM): `tools\\gy.cmd refresh` (kalit yoki kuchli model bilan)",
              ""]
    REPORT.write_text("\n".join(lines), encoding="utf-8")


def cmd_build(args: argparse.Namespace) -> int:
    data = build()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_report(data)
    s = data["stats"]
    print(f"✓ graf qurildi: {OUT.relative_to(VAULT).as_posix()} "
          f"({s['nodes']} tugun, {s['links']} qirra, {s['communities']} klaster) — 0 token")
    if args.report:
        print(f"  hisobot: {REPORT.relative_to(VAULT).as_posix()}")
    return 0


def cmd_stats(_args: argparse.Namespace) -> int:
    if not OUT.is_file():
        print("✗ graf yo'q — `py -3 tools\\brain-graph.py build`")
        return 2
    data = json.loads(OUT.read_text(encoding="utf-8"))
    s = data.get("stats", {})
    print(f"graf: {s.get('nodes')} tugun · {s.get('links')} qirra · {s.get('communities')} klaster")
    print(f"qurilgan: {data.get('built_at', '?')} · commit: {str(data.get('built_at_commit'))[:8]}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="brain-graph.py",
                                     description="Grafni wikilinklardan deterministik quradi")
    sub = parser.add_subparsers(dest="command", required=True)
    b = sub.add_parser("build", help="graphify-out/graph.json ni qayta quradi")
    b.add_argument("--report", action="store_true", help="GRAPH_REPORT.md ni ham yozadi")
    b.set_defaults(func=cmd_build)
    s = sub.add_parser("stats", help="graf holati")
    s.set_defaults(func=cmd_stats)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
