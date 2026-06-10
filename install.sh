#!/usr/bin/env bash
# VEIL install script
# Usage: bash install.sh

set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

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

echo ""
echo "done."
