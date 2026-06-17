"""Tests for shared/runtime/veil-status.py"""
from __future__ import annotations

import json
from pathlib import Path

from .helpers import status_cmd


def test_version():
    r = status_cmd("--version", check=False)
    assert "1.0.1" in r.stdout


def test_json_db_missing(tmp_path: Path):
    db = str(tmp_path / "nonexistent.db")
    r = status_cmd("--db", db, "--json")
    payload = json.loads(r.stdout)
    assert payload["db_exists"] is False
    assert r.returncode == 0


def test_json_db_present(tmp_path: Path):
    db = str(tmp_path / "veil.db")
    from .helpers import db_cmd
    db_cmd("init-db", "--db", db)
    r = status_cmd("--db", db, "--json")
    payload = json.loads(r.stdout)
    assert payload["db_exists"] is True
    assert payload["rule_count"] == 0


def test_check_db_missing_exits_1(tmp_path: Path):
    db = str(tmp_path / "nonexistent.db")
    r = status_cmd("--db", db, "--check", "--json", check=False)
    assert r.returncode == 1
    payload = json.loads(r.stdout)
    assert payload["has_error"] is True


def test_check_db_missing_text_output(tmp_path: Path):
    db = str(tmp_path / "nonexistent.db")
    r = status_cmd("--db", db, "--check", check=False)
    assert r.returncode == 1
    assert "[ERROR]" in r.stdout
