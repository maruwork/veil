# VEIL install script for Windows PowerShell
# Usage: .\install.ps1
# Requires: Python 3.8+

$ErrorActionPreference = "Stop"

$RepoDir    = $PSScriptRoot
$VeilDir    = "$env:USERPROFILE\.veil"
$ConfigFile = "$VeilDir\config.json"
$SyncScript = "$RepoDir\shared\runtime\veil-sync.py"

Write-Host "VEIL install"
Write-Host "repo: $RepoDir"
Write-Host ""

# Claude Code
$ClaudeDir = "$env:USERPROFILE\.claude\commands"
New-Item -ItemType Directory -Force -Path $ClaudeDir | Out-Null
Copy-Item "$RepoDir\skills\claude-code\veil-capture.md" "$ClaudeDir\veil-capture.md" -Force
Write-Host "[OK] Claude Code  $ClaudeDir\veil-capture.md"

# Codex
$CodexDir = "$env:USERPROFILE\.agents\skills\veil-capture"
New-Item -ItemType Directory -Force -Path $CodexDir | Out-Null
Copy-Item "$RepoDir\skills\codex\veil-capture\SKILL.md" "$CodexDir\SKILL.md" -Force
Write-Host "[OK] Codex        $CodexDir\SKILL.md"

# Detect language
$DetectedLang = "en"
$LangRaw = $env:VEIL_LANG
if (-not $LangRaw) { $LangRaw = $env:LANG }
if (-not $LangRaw) { $LangRaw = (Get-WinSystemLocale).Name }
if ($LangRaw -match "^ja") { $DetectedLang = "ja" }

# Write config.json
New-Item -ItemType Directory -Force -Path $VeilDir | Out-Null
$SyncScriptFwd = $SyncScript -replace "\\", "/"
$RepoDirFwd    = $RepoDir    -replace "\\", "/"

if (Test-Path $ConfigFile) {
    $cfg = Get-Content $ConfigFile -Raw | ConvertFrom-Json
    $cfgHash = @{}
    $cfg.PSObject.Properties | ForEach-Object { $cfgHash[$_.Name] = $_.Value }
} else {
    $cfgHash = @{}
}
$cfgHash["sync_script"] = $SyncScriptFwd
$cfgHash["veil_root"]   = $RepoDirFwd
$cfgHash["lang"]        = $DetectedLang
$jsonContent = [PSCustomObject]$cfgHash | ConvertTo-Json
[System.IO.File]::WriteAllText($ConfigFile, $jsonContent, (New-Object System.Text.UTF8Encoding $false))

Write-Host "[OK] config.json  sync_script=$SyncScriptFwd"
Write-Host "[OK] config.json  veil_root=$RepoDirFwd"
Write-Host "[OK] config.json  lang=$DetectedLang"

Write-Host ""
Write-Host "Registering sync targets..."

function Invoke-VeilAdd([string]$Path) {
    if (Test-Path $Path) {
        python $SyncScript --add $Path
    }
}

# Global Claude Code config
Invoke-VeilAdd "$env:USERPROFILE\.claude\CLAUDE.md"

# Project-level: if run from a project directory
$AiConfigs = @("CLAUDE.md", "AGENTS.md", "GEMINI.md", ".cursorrules", ".aider.conf.yml")
if ((Resolve-Path $PWD).Path -ne (Resolve-Path $RepoDir).Path) {
    foreach ($name in $AiConfigs) {
        Invoke-VeilAdd "$PWD\$name"
    }
    Invoke-VeilAdd "$PWD\.github\copilot-instructions.md"
}

Write-Host ""
Write-Host "done."
