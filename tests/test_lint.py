"""Unit tests for veil-lint.py CLI."""
from __future__ import annotations

import json

from .helpers import lint_cmd


def test_lint_hit(seeded):
    result = lint_cmd("--db", seeded["db"], "--text", "The current state of the system", "--json", check=False)
    payload = json.loads(result.stdout)
    assert payload["violations"], "Expected a violation for 'current state'"
    assert payload["violations"][0]["original"] == "current state"
    assert payload["violations"][0]["preferred"] == "present state"


def test_lint_clean(seeded):
    result = lint_cmd("--db", seeded["db"], "--text", "The present state of the system", "--json", check=False)
    payload = json.loads(result.stdout)
    assert not payload["violations"], "Expected clean output"


def test_lint_exit_code_on_violation(seeded):
    result = lint_cmd("--db", seeded["db"], "--text", "The current state", check=False)
    assert result.returncode != 0


def test_lint_exit_code_clean(seeded):
    result = lint_cmd("--db", seeded["db"], "--text", "The present state", check=False)
    assert result.returncode == 0


def test_lint_skip_no_rules(tmp_db):
    result = lint_cmd("--db", tmp_db, "--text", "anything here", "--json", check=False)
    payload = json.loads(result.stdout)
    assert result.returncode == 0
    assert payload.get("status") == "skip"


def test_lint_protected_backtick(seeded):
    result = lint_cmd("--db", seeded["db"], "--text", "Use `current state` as the variable name", "--json")
    payload = json.loads(result.stdout)
    assert not payload["violations"], "Backtick-wrapped term should be protected"


def test_lint_case_insensitive(seeded):
    result = lint_cmd("--db", seeded["db"], "--text", "The Current State", "--json", check=False)
    payload = json.loads(result.stdout)
    assert payload["violations"], "Case-insensitive match expected"


def test_lint_protected_indented_code_block(seeded):
    result = lint_cmd("--db", seeded["db"], "--text", "    current state", "--json")
    payload = json.loads(result.stdout)
    assert not payload["violations"], "Indented code block should be protected"


def test_lint_detects_nested_markdown_list_item(seeded):
    text = "- item one\n    - the current state is bad\n"
    result = lint_cmd("--db", seeded["db"], "--text", text, "--json", check=False)
    payload = json.loads(result.stdout)
    assert payload["violations"], "Nested markdown list item should not be masked as code"
    assert payload["violations"][0]["original"] == "current state"


def test_lint_protects_indented_code_block_after_blank_line(seeded):
    text = "Example:\n\n    current state\n"
    result = lint_cmd("--db", seeded["db"], "--text", text, "--json")
    payload = json.loads(result.stdout)
    assert not payload["violations"], "Indented code block after a blank line should be protected"


def test_lint_protected_tilde_fence(seeded):
    text = "~~~text\ncurrent state\n~~~"
    result = lint_cmd("--db", seeded["db"], "--text", text, "--json")
    payload = json.loads(result.stdout)
    assert not payload["violations"], "Tilde fenced code block should be protected"


def test_lint_corrupted_db_returns_error(tmp_path):
    db = tmp_path / "bad.db"
    db.write_text("not a sqlite database", encoding="utf-8")
    result = lint_cmd("--db", str(db), "--text", "The current state", "--json", check=False)
    payload = json.loads(result.stdout)
    assert result.returncode == 2
    assert payload["status"] == "error"
