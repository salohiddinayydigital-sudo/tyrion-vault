#!/usr/bin/env python3
"""skill-search — LLM'siz (deterministik) skill reyestri va agentga ulash. 0 token.

Muammo: agent ishni boshlashdan oldin qaysi skill bo'yicha ishlashini bilishi kerak,
lekin skill papkalari 4 xil joyda yotadi (platforma va operator) va
"qaysi skill qaysi agentga ulangan" degan javob hech qayerda yozilmagan edi.

Yechim: ikki tomonlama ulanish (attach) — frontmatter'dan o'qiladi:
  skill: `attached_agents: [video-editor]`
  agent: `skills: [video-editing, video-motion-graphics]`
`check` bu ikki tomonni solishtiradi va uzilgan ulanishni xato deb ko'rsatadi.

Buyruqlar (agent ishi 0-qadamda `agent` yoki `brief` ni ishlatadi):
  py -3 tools\\skill-search.py agent video-editor
  py -3 tools\\skill-search.py brief "shu videoni montaj qil" --agent video-editor
  py -3 tools\\skill-search.py search "kinetik tipografiya animatsiya" --top 3
  py -3 tools\\skill-search.py list [--layer operator|platform]
  py -3 tools\\skill-search.py check

Chiqish: qisqa qatorlar (token tejamkor). Kod: 0 — topildi/muammo yo'q,
1 — topilmadi yoki `check` da uzilish bor, 2 — argument xatosi.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path

VAULT = Path(__file__).resolve().parent.parent

for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        try:
            _stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:  # pragma: no cover
            pass

try:  # PyYAML bor bo'lsa — to'liq YAML
    import yaml
except ImportError:  # pragma: no cover
    yaml = None  # type: ignore[assignment]

# Skill qatlamlari: nom -> (ildiz, layer)
SKILL_ROOT = VAULT / "skills"
AGENT_ROOT = VAULT / "agents"

FRONTMATTER_RE = re.compile(r"\A---\r?\n(.*?)\r?\n---", re.DOTALL)
WORD = re.compile(r"[a-zA-Zа-яА-ЯёЁʻʼ'\u0400-\u04FF]+", re.UNICODE)
STOP = {"va", "bilan", "uchun", "bu", "shu", "bir", "eng", "yoki", "ham", "kerak",
        "qil", "qilib", "qilsin", "qiling", "ber", "bering", "beringiz", "berin",
        "yasa", "yasab", "yasash", "yasalgan", "iltimos", "menga", "men", "hozir", "tez",
        "the", "and", "for", "with", "of", "to", "in", "on", "a", "is"}


# --------------------------------------------------------------------------- #
# Frontmatter o'qish
# --------------------------------------------------------------------------- #

def _fallback_list(block: str, key: str) -> list[str]:
    """PyYAML bo'lmaganda `key: [a, b]` yoki `key:` + `- a` ro'yxatini o'qish."""
    inline = re.search(rf"^{key}:\s*\[(.*?)\]\s*$", block, re.M)
    if inline:
        return [x.strip().strip("'\"") for x in inline.group(1).split(",") if x.strip()]
    block_form = re.search(rf"^{key}:\s*\n((?:\s*-\s*.+\n?)+)", block, re.M)
    if block_form:
        return [ln.strip().lstrip("-").strip().strip("'\"")
                for ln in block_form.group(1).splitlines() if ln.strip()]
    return []


def read_frontmatter(path: Path) -> dict:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return {}
    match = FRONTMATTER_RE.match(text)
    if not match:
        return {}
    raw = match.group(1)
    if yaml is not None:
        try:
            data = yaml.safe_load(raw) or {}
            if isinstance(data, dict):
                return data
        except Exception:
            pass
    flat: dict[str, object] = {}
    for line in raw.splitlines():
        if not line or line.startswith(("#", " ", "\t", "-")) or ":" not in line:
            continue
        key, _, value = line.partition(":")
        flat[key.strip()] = value.strip().strip('"').strip("'")
    for key in ("triggers", "attached_agents", "skills"):
        values = _fallback_list(raw, key)
        if values:
            flat[key] = values
    return flat


def as_list(value: object) -> list[str]:
    if not value:
        return []
    if isinstance(value, str):
        return [x.strip() for x in value.split(",") if x.strip()]
    if isinstance(value, (list, tuple)):
        return [str(x).strip() for x in value if str(x).strip()]
    return []


# --------------------------------------------------------------------------- #
# Reyestr
# --------------------------------------------------------------------------- #

def _infer_layer(name: str, fm: dict) -> str:
    if fm.get("layer"):
        return str(fm["layer"])
    return "platform" if (name == "ads" or name.startswith("ads-")) else "operator"


def load_skills() -> list[dict]:
    """Barcha SKILL.md fayllar (yagona kanonik `skills/` papkasidan)."""
    skills: list[dict] = []
    if not SKILL_ROOT.is_dir():
        return skills
    for path in sorted(SKILL_ROOT.glob("*/SKILL.md")):
        fm = read_frontmatter(path)
        name = str(fm.get("name") or path.parent.name).strip()
        layer = _infer_layer(name, fm)
        body = path.read_text(encoding="utf-8", errors="replace")
        skills.append({
            "name": name,
            "dir": path.parent.name,
            "path": path.relative_to(VAULT).as_posix(),
            "abs": path,
            "layer": layer,
            "root": layer,
            "description": re.sub(r"\s+", " ", str(fm.get("description") or "")).strip(),
            "triggers": as_list(fm.get("triggers")),
            "agents": as_list(fm.get("attached_agents")),
            "refs": sorted(p.name for p in path.parent.glob("references/*.md")),
            "dir_name_matches": path.parent.name == name,
            "has_frontmatter": bool(fm),
            "standalone": bool(fm.get("standalone")),
            "body": body,
        })
    return sorted(skills, key=lambda s: s["name"])


def load_agents() -> dict[str, dict]:
    """Agent charterlari (kanonik `agents/`) va ulardagi `skills:` ro'yxati."""
    agents: dict[str, dict] = {}
    if not AGENT_ROOT.is_dir():
        return agents
    for path in sorted(AGENT_ROOT.glob("*.md")):
        fm = read_frontmatter(path)
        name = str(fm.get("name") or path.stem).strip()
        agents[name] = {
            "name": name,
            "path": path.relative_to(VAULT).as_posix(),
            "skills": as_list(fm.get("skills")),
            "mirror_exists": True,
        }
    return agents


# --------------------------------------------------------------------------- #
# Qidiruv
# --------------------------------------------------------------------------- #

def tokens(value: str) -> list[str]:
    return [w.lower() for w in WORD.findall(value) if len(w) > 1 and w.lower() not in STOP]


def score(skill: dict, query_tokens: list[str], idf: dict[str, float] | None = None) -> float:
    """Vazn: nom > trigger (butun so'z) > trigger > tavsif > tana. Deterministik, LLM'siz.

    Ikki tuzatish (tekshirilgan holatlar asosida):
    1. Tana hissasi cheklangan (2.5) — aks holda uzun SKILL.md matni umumiy so'zlar bilan
       ball to'plab noto'g'ri skillni yutib oladi.
    2. `idf` — so'z noyobligi: reyestrda ko'p skillda uchraydigan so'z ("reels", "video")
       kamroq vazn beradi, faqat bitta skillga xos so'z ("animatsion", "kinetik") ko'proq.
    """
    name = skill["name"].lower()
    trig = " ".join(skill["triggers"]).lower()
    trig_words = set(WORD.findall(trig))
    desc = skill["description"].lower()
    body = skill["body"].lower()
    total = 0.0
    for token in set(query_tokens):
        weight = 0.0
        if token in name:
            weight += 8
        if token in trig_words:
            weight += 8          # trigger ichida butun so'z sifatida
        elif token in trig:
            weight += 4          # qisman moslik (masalan "animatsion" → "animatsion video")
        if token in desc:
            weight += 3
        count = body.count(token)
        if count:
            weight += min(1 + math.log(1 + count), 2.5)
        if idf:
            weight *= idf.get(token, 1.0)
        total += weight
    return total


def build_idf(pool: list[dict], query_tokens: list[str]) -> dict[str, float]:
    """So'z noyobligi: reyestrda kam uchraydigan so'z ko'proq vazn oladi (1.0 … ~5)."""
    ids: dict[str, float] = {}
    total = max(len(pool), 1)
    for token in set(query_tokens):
        seen = sum(
            1 for s in pool
            if token in (s["name"] + " " + " ".join(s["triggers"]) + " " + s["description"]).lower()
        )
        ids[token] = 1.0 + math.log(1 + total / max(seen, 1))
    return ids


def rank(skills: list[dict], query: str, idf_pool: list[dict] | None = None) -> list[tuple[float, dict]]:
    query_tokens = tokens(query)
    idf = build_idf(idf_pool if idf_pool is not None else skills, query_tokens)
    ranked = [(score(s, query_tokens, idf), s) for s in skills]
    return sorted([(sc, s) for sc, s in ranked if sc > 0], key=lambda x: (-x[0], x[1]["name"]))


# --------------------------------------------------------------------------- #
# Chiqarish
# --------------------------------------------------------------------------- #

def print_skill_line(score_value: float, skill: dict, agent: str = "") -> None:
    attached = ", ".join(skill["agents"]) or "—"
    print(f"  [{int(score_value):3}] {skill['name']}  ({skill['layer']})")
    print(f"        fayl    : {skill['path']}")
    print(f"        ulangan : {attached}")
    if skill["refs"]:
        print(f"        qo'shimcha: references/ — {', '.join(skill['refs'])}")
    if skill["description"]:
        print(f"        nima    : {skill['description'][:100]}")


def attached_to(skills: list[dict], agent: str) -> list[dict]:
    return [s for s in skills if agent in s["agents"]]


# --------------------------------------------------------------------------- #
# Buyruqlar
# --------------------------------------------------------------------------- #

def cmd_agent(args: argparse.Namespace) -> int:
    skills = load_skills()
    agents = load_agents()
    agent = args.name
    if agent not in agents:
        near = [a for a in agents if agent.lower() in a.lower()]
        print(f"✗ agent topilmadi: {agent}" + (f" (o'xshash: {', '.join(near[:5])})" if near else ""))
        return 2
    listed = agents[agent]["skills"]
    attached = {s["name"]: s for s in attached_to(skills, agent)}
    print(f"Agent: {agent}  (charter: {agents[agent]['path']})")
    print(f"Ulangan skill ({len(attached)}):")
    if not attached:
        print("  — yo'q: charter frontmatter'ida `skills:` va skillda `attached_agents:` yozilsin")
        return 1
    for name in (listed or sorted(attached)):
        skill = attached.get(name)
        if skill is None:
            print(f"  [{name}] ✗ skill papkasi yo'q (charter'da e'lon qilingan, fayl topilmadi)")
            continue
        print(f"  {name}")
        print(f"        fayl: {skill['path']}")
        if skill["refs"]:
            print(f"        qo'shimcha: references/ — {', '.join(skill['refs'])}")
    return 0


def cmd_brief(args: argparse.Namespace) -> int:
    """Agent e'lon qiladigan 'skill talash so'rovi' bloki + tanlangan skill."""
    skills = load_skills()
    pool = skills
    if args.agent:
        subset = attached_to(skills, args.agent)
        if not subset:
            print(f"Skill so'rovi: \"{args.query}\"")
            print(f"✗ {args.agent} agentiga skill ulanmagan — ish boshlanmaydi (needs_input)")
            return 1
        pool = subset
    hits = rank(pool, args.query, idf_pool=skills)
    scope = f" · agent: {args.agent}" if args.agent else ""
    print(f"Skill so'rovi: \"{args.query}\"{scope}")
    if not hits:
        print("✗ mos skill topilmadi — ish boshlanmaydi, conductor'ga `needs_input` qaytariladi")
        print("  (vazifa turi boshqacha nomlansa, o'sha nom bilan qayta qidirilsin)")
        return 1
    top_score, top = hits[0]
    print(f"Tanlandi: {top['name']}  (ball {int(top_score)})")
    print(f"  fayl    : {top['path']}")
    print(f"  ulangan : {', '.join(top['agents']) or '—'}")
    if top["refs"]:
        print(f"  qo'shimcha: references/ — {', '.join(top['refs'])}")
    if top["triggers"]:
        print(f"  trigger : {', '.join(top['triggers'][:8])}")
    others = [h for h in hits[1:args.top]]
    if others:
        print("Zaxira: " + " · ".join(f"{s['name']} ({int(sc)})" for sc, s in others))
    print("Keyingi qadam: shu SKILL.md ni o'qib, FAQAT shu skill tartibi bo'yicha ishla.")
    return 0


def cmd_search(args: argparse.Namespace) -> int:
    skills = load_skills()
    pool = skills
    if args.agent:
        pool = attached_to(skills, args.agent)
        if not pool:
            print(f"✗ {args.agent} agentiga skill ulanmagan")
            return 1
    hits = rank(pool, args.query)[: args.top]
    if not hits:
        print(f"✗ mos skill topilmadi (so'rov: {args.query})")
        return 1
    scope = f" · agent: {args.agent}" if args.agent else f" · reyestr: {len(pool)} skill"
    print(f"Topildi {len(hits)}{scope}:")
    for sc, skill in hits:
        print_skill_line(sc, skill)
    return 0


def cmd_list(args: argparse.Namespace) -> int:
    skills = load_skills()
    if args.layer:
        skills = [s for s in skills if s["layer"] == args.layer]
    agents = load_agents()
    print(f"Skill reyestri: {len(skills)} ta" + (f" (layer={args.layer})" if args.layer else ""))
    for skill in skills:
        attached = ", ".join(skill["agents"]) or ("— ulanmagan"
                                                  if not skill["standalone"] else "standalone")
        print(f"  {skill['layer']:9} {skill['name']:28} → {attached}")
    print(f"Agentlar: {len(agents)} · skill ulangan: "
          f"{sum(1 for a in agents.values() if a['skills'])}")
    return 0


def cmd_check(_args: argparse.Namespace) -> int:
    """Ikki tomonlama ulanishni tekshir: skill ↔ agent, frontmatter, papka nomi."""
    skills = load_skills()
    agents = load_agents()
    problems: list[str] = []
    warnings: list[str] = []

    for skill in skills:
        if not skill["has_frontmatter"]:
            problems.append(f"{skill['path']}: frontmatter yo'q")
            continue
        if not skill["description"]:
            problems.append(f"{skill['path']}: `description` bo'sh")
        if not skill["dir_name_matches"]:
            warnings.append(f"{skill['path']}: papka nomi ({skill['dir']}) ≠ skill nomi ({skill['name']})")
        for agent in skill["agents"]:
            if agent not in agents:
                problems.append(f"{skill['name']}: `attached_agents: {agent}` — bunday charter yo'q "
                                f"(agents/{agent}.md)")
                continue
            if skill["name"] not in agents[agent]["skills"]:
                problems.append(f"{skill['name']} → {agent}: agent charterida teskari havola yo'q "
                                f"(`skills:` ga qo'shilsin)")
        if not skill["agents"] and not skill["standalone"] and skill["root"] == "operator":
            # Operator qatlami: har skill bitta agentga ulanishi shart (aks holda agent uni topa olmaydi).
            warnings.append(f"{skill['name']}: hech qaysi agentga ulanmagan "
                            f"(agent uni topa olmaydi; kerak bo'lmasa `standalone: true`)")

    for agent in agents.values():
        for name in agent["skills"]:
            match = next((s for s in skills if s["name"] == name), None)
            if match is None:
                problems.append(f"{agent['name']}.skills: `{name}` — SKILL.md topilmadi")
            elif agent["name"] not in match["agents"]:
                problems.append(f"{agent['name']} → {name}: skillda `attached_agents: {agent['name']}` yo'q")

    print(f"Skill: {len(skills)} · agent: {len(agents)} · "
          f"ulanish: {sum(len(s['agents']) for s in skills)}")
    if warnings:
        print(f"⚠ ogohlantirish ({len(warnings)}):")
        for item in warnings[:10]:
            print(f"  - {item}")
    if problems:
        print(f"✗ uzilgan ulanish / xato ({len(problems)}):")
        for item in problems[:15]:
            print(f"  - {item}")
        return 1
    print("✓ skill reyestri va ulanishlar butun")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="skill-search.py",
                                     description="LLM'siz skill reyestri va agentga ulash")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("agent", help="agentga ulangan skilllar")
    p.add_argument("name")
    p.set_defaults(func=cmd_agent)

    p = sub.add_parser("brief", help="skill talash so'rovi bloki (agent 0-qadam)")
    p.add_argument("query")
    p.add_argument("--agent", default="")
    p.add_argument("--top", type=int, default=3)
    p.set_defaults(func=cmd_brief)

    p = sub.add_parser("search", help="so'rov bo'yicha skill qidirish")
    p.add_argument("query")
    p.add_argument("--agent", default="")
    p.add_argument("--top", type=int, default=3)
    p.set_defaults(func=cmd_search)

    p = sub.add_parser("list", help="butun reyestr")
    p.add_argument("--layer", default="")
    p.set_defaults(func=cmd_list)

    p = sub.add_parser("check", help="ulanish va frontmatter tekshiruvi")
    p.set_defaults(func=cmd_check)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
