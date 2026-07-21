#!/usr/bin/env bash
# VEIL install script
# Usage: bash install.sh
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VEIL_DIR="$HOME/.veil"
CONFIG_FILE="$VEIL_DIR/config.json"
SYNC_SCRIPT="$REPO_DIR/shared/runtime/veil-sync.py"
DEFAULT_PROFILE_SEED="$REPO_DIR/shared/default-profile/technical-writing-default.json"
DB_PATH="$VEIL_DIR/veil.db"
HTML_PATH="$VEIL_DIR/veil.html"

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
_lang_code="${_lang_raw%%:*}"           # LANGUAGE=ja:en:de -> ja
_lang_code="${_lang_code%%[_.-]*}"     # ja_JP.UTF-8 -> ja
_lang_code="$(echo "$_lang_code" | tr '[:upper:]' '[:lower:]')"
[[ "$_lang_code" =~ ^[a-z]{2,3}$ ]] && DETECTED_LANG="$_lang_code" || DETECTED_LANG="en"

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
echo "Initializing SQLite canonical DB..."
DB_ALREADY_PRESENT=0
[ -f "$DB_PATH" ] && DB_ALREADY_PRESENT=1
python3 "$REPO_DIR/shared/tools/veil-db.py" init-db --db "$DB_PATH"
echo "[OK] veil.db       $DB_PATH"
if [ "$DB_ALREADY_PRESENT" -eq 0 ]; then
  echo ""
  echo "Seeding bundled technical-writing default profile..."
  python3 "$REPO_DIR/shared/tools/veil-db.py" import-seed --db "$DB_PATH" --seed-file "$DEFAULT_PROFILE_SEED" --yes
  python3 "$REPO_DIR/shared/tools/veil-db.py" export-html --db "$DB_PATH" --html-path "$HTML_PATH"
  echo "[OK] default rules $DEFAULT_PROFILE_SEED"
fi

echo ""
echo "Registering sync targets..."
_veil_try_add() {
  if [ -f "$1" ]; then
    python3 "$SYNC_SCRIPT" --add "$1"
  fi
}
# Global Claude Code config (siblings like AGENTS.md auto-registered if present)
_veil_try_add "$HOME/.claude/CLAUDE.md"
# Project-level: if install.sh was run from a project directory
if [ "$PWD" != "$REPO_DIR" ]; then
  for _name in CLAUDE.md AGENTS.md GEMINI.md .cursorrules .aider.conf.yml; do
    _veil_try_add "$PWD/$_name"
  done
  _veil_try_add "$PWD/.github/copilot-instructions.md"
fi

echo ""
echo "done."
