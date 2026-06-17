"""Unit tests for veil-normalize.py CLI."""
from __future__ import annotations

import json

from .helpers import normalize_cmd


def test_normalize_existing_match(seeded):
    result = normalize_cmd("--db", seeded["db"], "--text", "current states", "--json")
    payload = json.loads(result.stdout)
    existing = payload.get("existing", [])
    assert any(m["preferred"] == "present state" for m in existing), "Expected existing match for 'current state'"


def test_normalize_new_candidate(tmp_db):
    result = normalize_cmd("--db", tmp_db, "--text", "migration plan", "--json")
    payload = json.loads(result.stdout)
    new = payload.get("new", [])
    assert new, f"Expected new candidate for 'migration plan', got: {new}"


def test_normalize_groups_variants(seeded):
    result = normalize_cmd("--db", seeded["db"], "--text", "current-state\ncurrent_state\nCurrent State", "--json")
    payload = json.loads(result.stdout)
    existing = payload.get("existing", [])
    assert existing, "Variants of 'current state' should match existing rule"


def test_normalize_empty_input(tmp_db):
    result = normalize_cmd("--db", tmp_db, "--text", "", "--json")
    payload = json.loads(result.stdout)
    assert payload.get("existing", []) == []
    assert payload.get("new", []) == []


def test_normalize_corrupted_db_returns_error(tmp_path):
    db = tmp_path / "bad.db"
    db.write_text("not a sqlite database", encoding="utf-8")
    result = normalize_cmd("--db", str(db), "--text", "current state", "--json", check=False)
    payload = json.loads(result.stdout)
    assert result.returncode == 2
    assert payload["status"] == "error"
