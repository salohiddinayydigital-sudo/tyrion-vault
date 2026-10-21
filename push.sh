#!/usr/bin/env bash
# push.sh — Tyrion v5.0 Automated Pre-Flight Verification & GitHub Push Script
set -euo pipefail

VAULT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$VAULT_ROOT"

PY_CMD="python3"
command -v python3 >/dev/null 2>&1 || PY_CMD="python"

echo "===================================================================="
echo "  🚀 TYRION v5.0 — GITHUB PRE-PUSH VERIFICATION & DEPLOY"
echo "===================================================================="

echo "[1/5] Running TyrionShield Security Scan (Zero Secrets Gate)..."
"$PY_CMD" tools/tyrion-shield.py scan

echo "[2/5] Running Vault Audit & Catalog Sync Gate..."
"$PY_CMD" tools/vault-audit.py . --gate
"$PY_CMD" tools/catalog.py check
"$PY_CMD" tools/catalog.py drift

echo "[3/5] Running Behavioral Eval Suite (24/24)..."
"$PY_CMD" tools/skill-eval.py

echo "[4/5] Running System Doctor..."
"$PY_CMD" tools/doctor.py --quick

REMOTE_URL="${1:-https://github.com/salohiddinayydigital-sudo/tyrion-vault.git}"
if ! git remote get-url origin >/dev/null 2>&1; then
    git remote add origin "$REMOTE_URL"
else
    git remote set-url origin "$REMOTE_URL"
fi

echo "[6/6] Pushing branch 'main' and tags to $REMOTE_URL ..."
git push -u origin main --force --tags
echo "✅ Successfully pushed Tyrion v5.0 to GitHub!"
