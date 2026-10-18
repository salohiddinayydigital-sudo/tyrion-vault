#!/usr/bin/env bash
# install.sh — Tyrion v4.2 Single-Root ECC Installer (macOS / Linux / WSL)
set -euo pipefail

VAULT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "===================================================================="
echo "  🧠 TYRION v4.2 — AI PAID MEDIA & TARGETOLOGY OS INSTALLER"
echo "===================================================================="

if command -v python3 >/dev/null 2>&1; then
    PY_CMD="python3"
elif command -v python >/dev/null 2>&1; then
    PY_CMD="python"
else
    echo "[-] Error: Python 3.10+ is required." >&2
    exit 1
fi

echo "[1/4] Syncing Claude Code hooks & slash commands..."
"$PY_CMD" "$VAULT_ROOT/tools/install-hooks.py"

echo "[2/4] Verifying Multi-Harness Adapter readiness (Claude, Cursor, Windsurf)..."
"$PY_CMD" "$VAULT_ROOT/tools/harness-export.py" --target claude

echo "[3/4] Running TyrionShield Security Audit & Behavioral Evals..."
"$PY_CMD" "$VAULT_ROOT/tools/tyrion-shield.py" scan
"$PY_CMD" "$VAULT_ROOT/tools/skill-eval.py"

echo "[4/4] Running System Doctor..."
"$PY_CMD" "$VAULT_ROOT/tools/doctor.py" --quick

echo ""
echo "✅ TYRION v4.2 INSTALLATION COMPLETE!"
echo "   Run: $PY_CMD tools/tyrion.py status"
