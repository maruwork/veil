#!/usr/bin/env bash
# VEIL one-liner installer
# Usage: curl -fsSL https://raw.githubusercontent.com/maruwork/veil/main/get-veil.sh | bash
# To customize install location: VEIL_REPO=~/dev/veil bash <(curl -fsSL ...)
set -euo pipefail

VEIL_REPO="${VEIL_REPO:-$HOME/tools/veil}"

if [ -d "$VEIL_REPO/.git" ]; then
  echo "Updating existing VEIL install at $VEIL_REPO..."
  git -C "$VEIL_REPO" pull --ff-only
else
  echo "Cloning VEIL to $VEIL_REPO..."
  git clone https://github.com/maruwork/veil.git "$VEIL_REPO"
fi

bash "$VEIL_REPO/install.sh"
