#Requires -Version 5.1
<#
.SYNOPSIS
  MCP 配布資源の初回セットアップ（pip パッケージインストール）

.EXAMPLE
  .\install.ps1
  .\install.ps1 -Python314 "C:\Users\me\AppData\Local\Programs\Python\Python314"
#>
param(
    [string]$Python313 = "$env:LOCALAPPDATA\Programs\Python\Python313\python.exe",
    [string]$Python314 = "$env:LOCALAPPDATA\Programs\Python\Python314\python.exe"
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
if (-not (Test-Path "$Root\manifest.json")) {
    $Root = "C:\work\MCP"
}

Write-Host "MCP root: $Root" -ForegroundColor Cyan

function Install-Pip($py, $pkg) {
    if (-not (Test-Path $py)) {
        Write-Warning "Python not found: $py — skip $pkg"
        return
    }
    Write-Host "pip install $pkg ($py)" -ForegroundColor Green
    & $py -m pip install --upgrade $pkg
}

Install-Pip $Python314 "scribus-mcp"
Install-Pip $Python313 "excellm"
Install-Pip $Python313 "mcp-excel"
Install-Pip $Python313 "mcp-pdf-forms"

Write-Host ""
Write-Host "Next: .\apply-config.ps1" -ForegroundColor Yellow
Write-Host "Manual: $Root\scribus\manual\index.html" -ForegroundColor Yellow
