#!/usr/bin/env bash
# VEIL install script
# Usage: bash install.sh
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VEIL_DIR="$HOME/.veil"
CONFIG_FILE="$VEIL_DIR/config.json"
SYNC_SCRIPT="$REPO_DIR/shared/runtime/veil-sync.py"

echo "VEIL install"
echo "repo: $REPO_DIR"
echo ""

# Claude Code
CLAUDE_COMMANDS_DIR="$HOME/.claude/commands"
mkdir -p "$CLAUDE_COMMANDS_DIR"
cp "$REPO_DIR/skills/claude-code/veil-capture.md" "$CLAUDE_COMMANDS_DIR/veil-capture.md"
echo "[OK] Claude Code  $CLAUDE_COMMANDS_DIR/veil-capture.md"

# Codex
CODEX_SKILLS_DIR="$HOME/.agents/skills/veil-capture"
mkdir -p "$CODEX_SKILLS_DIR"
cp "$REPO_DIR/skills/codex/veil-capture/SKILL.md" "$CODEX_SKILLS_DIR/SKILL.md"
echo "[OK] Codex        $CODEX_SKILLS_DIR/SKILL.md"

# Detect language (VEIL_LANG > LANG > LC_ALL > LANGUAGE, fallback en)
_lang_raw="${VEIL_LANG:-${LANG:-${LC_ALL:-${LANGUAGE:-}}}}"
_lang_code="$(echo "${_lang_raw%%[_.-]*}" | tr '[:upper:]' '[:lower:]')"
DETECTED_LANG="${_lang_code:-en}"

# Write sync_script, veil_root, lang to ~/.veil/config.json
mkdir -p "$VEIL_DIR"
if [ -f "$CONFIG_FILE" ]; then
  EXISTING=$(cat "$CONFIG_FILE")
else
  EXISTING="{}"
fi
python3 -c "
import json, sys
cfg = json.loads(sys.argv[1])
cfg['sync_script'] = sys.argv[2]
cfg['veil_root'] = sys.argv[3]
cfg['lang'] = sys.argv[4]
print(json.dumps(cfg, indent=2))
" "$EXISTING" "$SYNC_SCRIPT" "$REPO_DIR" "$DETECTED_LANG" > "$CONFIG_FILE"
echo "[OK] config.json  sync_script=$SYNC_SCRIPT"
echo "[OK] config.json  veil_root=$REPO_DIR"
echo "[OK] config.json  lang=$DETECTED_LANG"

echo ""
echo "done."
