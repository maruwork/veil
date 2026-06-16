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
