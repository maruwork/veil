"""Unit tests for veil-db.py CLI."""
from __future__ import annotations

import json
import os
import sqlite3

from .helpers import db_cmd


def test_init_db_creates_file(tmp_path):
    db = str(tmp_path / "new.db")
    assert not os.path.exists(db)
    db_cmd("init-db", "--db", db)
    assert os.path.exists(db)


def test_init_db_json_output(tmp_path):
    db = str(tmp_path / "new.db")
    result = db_cmd("init-db", "--db", db, "--json")
    payload = json.loads(result.stdout)
    assert payload["status"] == "ok"
    assert payload["db_path"] == db


def test_upsert_inserts_row(tmp_db):
    result = db_cmd("upsert-rule", "--db", tmp_db, "--term", "foo bar", "--preferred", "baz qux", "--json")
    payload = json.loads(result.stdout)
    assert payload["status"] == "ok"
    assert payload["action"] in ("inserted", "updated")
    assert payload["row"]["term_original"] == "foo bar"
    assert payload["row"]["preferred"] == "baz qux"


def test_upsert_with_alts(tmp_db):
    db_cmd("upsert-rule", "--db", tmp_db, "--term", "current state", "--preferred", "present state", "--preferred-alt-2", "current status")
    result = db_cmd("readback", "--db", tmp_db, "--json")
    rows = json.loads(result.stdout)["rows"]
    row = next(r for r in rows if r["term_original"] == "current state")
    assert row["preferred"] == "present state"
    assert row["preferred_alt_2"] == "current status"


def test_upsert_with_level(tmp_db):
    result = db_cmd(
        "upsert-rule",
        "--db",
        tmp_db,
        "--term",
        "validator",
        "--preferred",
        "checker",
        "--level",
        "recommended",
        "--json",
    )
    payload = json.loads(result.stdout)
    assert payload["row"]["profile_level"] == "recommended"


def test_upsert_with_level_alias(tmp_db):
    result = db_cmd(
        "upsert-rule",
        "--db",
        tmp_db,
        "--term",
        "observer",
        "--preferred",
        "watcher",
        "--level",
        "推奨",
        "--json",
    )
    payload = json.loads(result.stdout)
    assert payload["row"]["profile_level"] == "recommended"


def test_upsert_rejects_invalid_level(tmp_db):
    result = db_cmd(
        "upsert-rule",
        "--db",
        tmp_db,
        "--term",
        "broken",
        "--preferred",
        "fixed",
        "--level",
        "typo",
        "--json",
        check=False,
    )
    payload = json.loads(result.stdout)
    assert result.returncode == 1
    assert payload["status"] == "error"
    assert payload["reason"] == "store.invalid_profile_level"


def test_readback_empty(tmp_db):
    result = db_cmd("readback", "--db", tmp_db, "--json")
    payload = json.loads(result.stdout)
    assert payload["status"] == "ok"
    assert payload["rows"] == []


def test_export_mirror_generates_file(tmp_db, tmp_rules):
    db_cmd("upsert-rule", "--db", tmp_db, "--term", "current state", "--preferred", "present state")
    db_cmd("export-mirror", "--db", tmp_db, "--rules-dir", tmp_rules)
    assert os.path.exists(os.path.join(tmp_rules, "c.md"))


def test_export_mirror_json(tmp_db, tmp_rules):
    db_cmd("upsert-rule", "--db", tmp_db, "--term", "current state", "--preferred", "present state")
    result = db_cmd("export-mirror", "--db", tmp_db, "--rules-dir", tmp_rules, "--json")
    payload = json.loads(result.stdout)
    assert payload["status"] == "ok"
    assert payload["row_count"] == 1
    assert "c.md" in payload["written_files"]


def test_export_html(tmp_db, tmp_path):
    db_cmd("upsert-rule", "--db", tmp_db, "--term", "current state", "--preferred", "present state")
    html_path = str(tmp_path / "veil.html")
    db_cmd("export-html", "--db", tmp_db, "--html-path", html_path)
    assert os.path.exists(html_path)
    content = open(html_path, encoding="utf-8").read()
    assert "current state" in content
    assert "present state" in content
    assert "Manual copy prompt opened." in content
    assert "Clipboard access is unavailable. Copy this text manually:" in content
    assert "opacity: 0" not in content


def test_import_rules_yes_flag(tmp_db, tmp_rules):
    db_cmd("upsert-rule", "--db", tmp_db, "--term", "alpha", "--preferred", "beta")
    db_cmd("export-mirror", "--db", tmp_db, "--rules-dir", tmp_rules)
    result = db_cmd("import-rules", "--db", tmp_db, "--rules-dir", tmp_rules, "--yes")
    assert result.returncode == 0
    rows = json.loads(db_cmd("readback", "--db", tmp_db, "--json").stdout)["rows"]
    assert any(r["term_original"] == "alpha" for r in rows)


def test_import_rules_no_yes_aborts_non_tty(tmp_db, tmp_rules):
    db_cmd("upsert-rule", "--db", tmp_db, "--term", "alpha", "--preferred", "beta")
    db_cmd("export-mirror", "--db", tmp_db, "--rules-dir", tmp_rules)
    result = db_cmd("import-rules", "--db", tmp_db, "--rules-dir", tmp_rules, check=False)
    assert result.returncode == 1


def test_import_rules_round_trips_alt_candidates_and_levels(tmp_db, tmp_rules):
    db_cmd(
        "upsert-rule",
        "--db",
        tmp_db,
        "--term",
        "current state",
        "--preferred",
        "present state",
        "--preferred-alt-2",
        "current status",
        "--preferred-alt-3",
        "system state",
        "--level",
        "observe",
    )
    db_cmd("export-mirror", "--db", tmp_db, "--rules-dir", tmp_rules)
    result = db_cmd("import-rules", "--db", tmp_db, "--rules-dir", tmp_rules, "--yes", "--json")
    payload = json.loads(result.stdout)
    assert payload["status"] == "ok"
    row = next(r for r in json.loads(db_cmd("readback", "--db", tmp_db, "--json").stdout)["rows"] if r["term_original"] == "current state")
    assert row["preferred_alt_2"] == "current status"
    assert row["preferred_alt_3"] == "system state"
    assert row["profile_level"] == "observe"


def test_corrupted_db_returns_error(tmp_path):
    db = tmp_path / "bad.db"
    db.write_text("not a sqlite database", encoding="utf-8")
    result = db_cmd("readback", "--db", str(db), "--json", check=False)
    payload = json.loads(result.stdout)
    assert result.returncode == 1
    assert payload["status"] == "error"


def test_legacy_db_schema_migrates_profile_level(tmp_path):
    db = tmp_path / "legacy.db"
    conn = sqlite3.connect(db)
    conn.executescript(
        """
        CREATE TABLE rules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            term_original TEXT NOT NULL,
            term_normalized TEXT NOT NULL UNIQUE,
            preferred TEXT NOT NULL,
            preferred_alt_2 TEXT,
            preferred_alt_3 TEXT,
            status TEXT NOT NULL,
            category_hint TEXT,
            note TEXT,
            source_context TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        INSERT INTO rules (
            term_original, term_normalized, preferred, preferred_alt_2, preferred_alt_3,
            status, category_hint, note, source_context, created_at, updated_at
        ) VALUES (
            'current state', 'current state', 'present state', NULL, NULL,
            'active', NULL, NULL, 'legacy', '2026-06-17T00:00:00+00:00', '2026-06-17T00:00:00+00:00'
        );
        """
    )
    conn.commit()
    conn.close()

    result = db_cmd("readback", "--db", str(db), "--json")
    payload = json.loads(result.stdout)
    assert payload["status"] == "ok"
    assert payload["rows"][0]["profile_level"] == "required"
