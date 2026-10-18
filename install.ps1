# install.ps1 — Tyrion v4.2 Single-Root ECC Installer (Windows PowerShell)
$ErrorActionPreference = 'Stop'

$vaultRoot = $PSScriptRoot
if (-not $vaultRoot) { $vaultRoot = (Get-Location).Path }

Write-Host "====================================================================" -ForegroundColor Cyan
Write-Host "  🧠 TYRION v4.2 — AI PAID MEDIA & TARGETOLOGY OS INSTALLER" -ForegroundColor Magenta
Write-Host "====================================================================" -ForegroundColor Cyan

$pyCmd = if (Get-Command py -ErrorAction SilentlyContinue) { "py" } elseif (Get-Command python -ErrorAction SilentlyContinue) { "python" } else { $null }
if (-not $pyCmd) {
    Write-Host "[-] Python 3.10+ topilmadi. https://python.org dan o'rnating." -ForegroundColor Red
    exit 1
}

Write-Host "[1/4] Claude Code hooklar va slash buyruqlarni o'rnatish..." -ForegroundColor White
& $pyCmd (Join-Path $vaultRoot "tools\install-hooks.py")

Write-Host "[2/4] Multi-Harness (Claude / Cursor / Windsurf) sinxronizatsiyasi..." -ForegroundColor White
& $pyCmd (Join-Path $vaultRoot "tools\harness-export.py") --target claude

Write-Host "[3/4] TyrionShield (5/5) va Eval Suite (10/10) tekshiruvi..." -ForegroundColor White
& $pyCmd (Join-Path $vaultRoot "tools\tyrion-shield.py") scan
& $pyCmd (Join-Path $vaultRoot "tools\skill-eval.py")

Write-Host "[4/4] Tizim salomatligi (Doctor)..." -ForegroundColor White
& $pyCmd (Join-Path $vaultRoot "tools\doctor.py") --quick

Write-Host ""
Write-Host "✅ TYRION v4.2 MUVAFFAQIYATLI O'RNATILDI!" -ForegroundColor Green
Write-Host "   Boshqaruv markazi: py -3 tools\tyrion.py status" -ForegroundColor Yellow
