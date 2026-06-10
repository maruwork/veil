#!/usr/bin/env bash
# Install VEIL skill files to their respective AI tool directories.
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

CLAUDE_COMMANDS_DIR="$HOME/.claude/commands"
mkdir -p "$CLAUDE_COMMANDS_DIR"
cp "$REPO_DIR/skills/claude-code/veil-capture.md" "$CLAUDE_COMMANDS_DIR/veil-capture.md"
echo "[OK] Claude Code  $CLAUDE_COMMANDS_DIR/veil-capture.md"

CODEX_SKILLS_DIR="$HOME/.agents/skills/veil-capture"
mkdir -p "$CODEX_SKILLS_DIR"
cp "$REPO_DIR/skills/codex/veil-capture/SKILL.md" "$CODEX_SKILLS_DIR/SKILL.md"
echo "[OK] Codex        $CODEX_SKILLS_DIR/SKILL.md"

echo "done."
