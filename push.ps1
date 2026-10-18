# push.ps1 — Tyrion v4.2 Automated Pre-Flight Verification & GitHub Push Script (Windows PowerShell)
param(
    [string]$RemoteUrl = "https://github.com/salohiddinayydigital-sudo/tyrion-vault.git"
)
$ErrorActionPreference = 'Stop'

$vaultRoot = $PSScriptRoot
if (-not $vaultRoot) { $vaultRoot = (Get-Location).Path }
Set-Location $vaultRoot

$pyCmd = if (Get-Command py -ErrorAction SilentlyContinue) { "py" } else { "python" }

Write-Host "====================================================================" -ForegroundColor Cyan
Write-Host "  🚀 TYRION v4.2 — GITHUB PRE-PUSH VERIFICATION & DEPLOY" -ForegroundColor Green
Write-Host "====================================================================" -ForegroundColor Cyan

Write-Host "[1/5] TyrionShield 5-qavatli xavfsizlik tekshiruvi..." -ForegroundColor White
& $pyCmd tools\tyrion-shield.py scan
if ($LASTEXITCODE -ne 0) { throw "TyrionShield xavfsizlik tekshiruvidan o'tmadi!" }

Write-Host "[2/5] Bilim qatlami va Katalog sinxronligi tekshiruvi..." -ForegroundColor White
& $pyCmd tools\vault-audit.py . --gate
& $pyCmd tools\catalog.py check
& $pyCmd tools\catalog.py drift

Write-Host "[3/5] Eval Suite (10/10 stsenariy) tekshiruvi..." -ForegroundColor White
& $pyCmd tools\skill-eval.py

Write-Host "[4/5] Doctor salomatlik tekshiruvi..." -ForegroundColor White
& $pyCmd tools\doctor.py --quick

Write-Host "[5/5] GitHub repozitoriyga yuklanmoqda: $RemoteUrl ..." -ForegroundColor Yellow
git remote set-url origin $RemoteUrl 2>$null
if ($LASTEXITCODE -ne 0) { git remote add origin $RemoteUrl }

git push -u origin main --force --tags
Write-Host "✅ Tyrion v4.2 GitHub'ga muvaffaqiyatli yuklandi!" -ForegroundColor Green
