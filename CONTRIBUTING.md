# Contributing to Tyrion v4.0

Tyrion v4.0 uses a **Single-Root ECC Architecture** where every layer has a single canonical directory at the repository root:

| Layer | Canonical Location | Generated Mirror |
|---|---|---|
| **Agents (36)** | `agents/*.md` | *(None — Single Source of Truth)* |
| **Skills (62)** | `skills/*/SKILL.md` | *(None — Single Source of Truth)* |
| **Slash Commands (16)** | `commands/*.md` | `.claude/commands/*.md` |
| **Context Modes (5)** | `contexts/*.md` | *(None)* |
| **Playbooks (8)** | `playbooks/*.md` | *(None)* |
| **Wiki Notes (98)** | `wiki/*.md` | `INDEX.md`, `graphify-out/graph.json` |
| **Rules (8)** | `rules/*.md` | *(None)* |

## Pre-Commit Verification Checklist

Run the following before every commit or PR:
```bash
python3 tools/vault-audit.py . --write
python3 tools/catalog.py sync-mirrors
python3 tools/catalog.py sync-claims
python3 tools/brain-graph.py build --report
python3 tools/catalog.py build
python3 tools/doctor.py
python3 tools/tyrion-shield.py scan
python3 -m unittest discover tests -v
```
