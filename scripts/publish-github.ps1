#Requires -Version 5.1
<#
.SYNOPSIS
  GitHub にリポジトリを作成して push（gh auth login 済みが前提）

.EXAMPLE
  .\publish-github.ps1
  .\publish-github.ps1 -RepoName cursor-mcp-hub -Private
#>
param(
    [string]$RepoName = "mcp",
    [switch]$Private,
    [string]$GhExe = "$PSScriptRoot\..\.tools\gh\bin\gh.exe"
)

$ErrorActionPreference = "Stop"
$Root = Resolve-Path (Join-Path $PSScriptRoot "..")

if (-not (Test-Path $GhExe)) {
    throw "gh not found: $GhExe (run install from README or download portable gh)"
}

& $GhExe auth status | Out-Null

$args = @(
    "repo", "create", $RepoName,
    "--description", "Cursor MCP distribution hub (scribus, excel, configs)",
    "--source", $Root,
    "--remote", "origin",
    "--push"
)
if ($Private) { $args += "--private" } else { $args += "--public" }

Write-Host "Creating repo: $RepoName" -ForegroundColor Cyan
& $GhExe @args
Write-Host "Done." -ForegroundColor Green
& $GhExe repo view --web
