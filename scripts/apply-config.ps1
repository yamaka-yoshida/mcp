#Requires -Version 5.1
<#
.SYNOPSIS
  mcp.json.template から ~/.cursor/mcp.json を生成

.EXAMPLE
  .\apply-config.ps1
  .\apply-config.ps1 -PdfFormsDocs "C:\work\MyProject\docs"
#>
param(
    [string]$McpRoot = "C:\work\MCP",
    [string]$WorkRoot = "C:\work",
    [string]$Python313 = "$env:LOCALAPPDATA\Programs\Python\Python313",
    [string]$Python314 = "$env:LOCALAPPDATA\Programs\Python\Python314",
    [string]$Python314Scripts = "$env:LOCALAPPDATA\Programs\Python\Python314\Scripts",
    [string]$PdfFormsDocs = "C:\work\PythonProject\APA送り状印刷ツール\docs",
    [switch]$WhatIf
)

$ErrorActionPreference = "Stop"
$templatePath = Join-Path $McpRoot "configs\mcp.json.template"
$out = Join-Path $env:USERPROFILE ".cursor\mcp.json"

if (-not (Test-Path $templatePath)) {
    throw "Template not found: $templatePath"
}

$json = [System.IO.File]::ReadAllText($templatePath, [System.Text.Encoding]::UTF8)
$replacements = @{
    "{{MCP_ROOT}}"           = ($McpRoot -replace '\\', '\\')
    "{{WORK}}"               = ($WorkRoot -replace '\\', '\\')
    "{{PYTHON313}}"          = ($Python313 -replace '\\', '\\')
    "{{PYTHON314}}"          = ($Python314 -replace '\\', '\\')
    "{{PYTHON314_SCRIPTS}}"  = ($Python314Scripts -replace '\\', '\\')
    "{{PDF_FORMS_DOCS}}"     = ($PdfFormsDocs -replace '\\', '\\')
    "{{USERPROFILE}}"        = ($env:USERPROFILE -replace '\\', '\\')
}
foreach ($k in $replacements.Keys) {
    $json = $json.Replace($k, $replacements[$k])
}

$outDir = Split-Path $out -Parent
if (-not (Test-Path $outDir)) {
    New-Item -ItemType Directory -Force -Path $outDir | Out-Null
}

if ($WhatIf) {
    Write-Host $json
    exit 0
}

# 既存をバックアップ
if (Test-Path $out) {
    $bak = "$out.bak-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
    Copy-Item $out $bak
    Write-Host "Backed up: $bak" -ForegroundColor DarkGray
}

[System.IO.File]::WriteAllText($out, $json, [System.Text.UTF8Encoding]::new($false))
Write-Host "Wrote: $out" -ForegroundColor Green
Write-Host "Restart Cursor to reload MCP." -ForegroundColor Yellow
