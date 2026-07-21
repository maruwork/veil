# VEIL install script for Windows PowerShell
# Usage: .\install.ps1
# Requires: Python 3.8+

$ErrorActionPreference = "Stop"

$RepoDir    = $PSScriptRoot
$VeilDir    = "$env:USERPROFILE\.veil"
$ConfigFile = "$VeilDir\config.json"
$SyncScript = "$RepoDir\shared\runtime\veil-sync.py"
$DefaultProfileSeed = "$RepoDir\shared\default-profile\technical-writing-default.json"
$DbPath = "$VeilDir\veil.db"
$HtmlPath = "$VeilDir\veil.html"

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
if ($LangRaw -match "^([A-Za-z]{2,3})") { $DetectedLang = $Matches[1].ToLower() }
else { $DetectedLang = "en" }

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
Write-Host "Initializing SQLite canonical DB..."
$DbAlreadyPresent = Test-Path $DbPath
python "$RepoDir\shared\tools\veil-db.py" init-db --db "$DbPath"
Write-Host "[OK] veil.db       $DbPath"
if (-not $DbAlreadyPresent) {
    Write-Host ""
    Write-Host "Seeding bundled technical-writing default profile..."
    python "$RepoDir\shared\tools\veil-db.py" import-seed --db "$DbPath" --seed-file "$DefaultProfileSeed" --yes
    Write-Host "[OK] default rules $DefaultProfileSeed"
}
python "$RepoDir\shared\tools\veil-db.py" export-html --db "$DbPath" --html-path "$HtmlPath"
Write-Host "[OK] veil.html      $HtmlPath"

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
Write-Host "Configuring UTF-8 output mode..."
[System.Environment]::SetEnvironmentVariable("PYTHONUTF8", "1", "User")
Write-Host "[OK] PYTHONUTF8=1 set for current user"

Write-Host ""
Write-Host "done."
