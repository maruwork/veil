# VEIL one-liner installer
# Usage: irm https://raw.githubusercontent.com/maruwork/veil/main/get-veil.ps1 | iex
# To customize install location: $env:VEIL_REPO = "$env:USERPROFILE\dev\veil"; irm ... | iex
$ErrorActionPreference = "Stop"

$VeilRepo = if ($env:VEIL_REPO) { $env:VEIL_REPO } else { "$env:USERPROFILE\tools\veil" }

if (Test-Path "$VeilRepo\.git") {
    Write-Host "Updating existing VEIL install at $VeilRepo..."
    git -C $VeilRepo pull --ff-only
} else {
    Write-Host "Cloning VEIL to $VeilRepo..."
    git clone https://github.com/maruwork/veil.git $VeilRepo
}

& "$VeilRepo\install.ps1"
