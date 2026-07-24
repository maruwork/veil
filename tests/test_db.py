"""Unit tests for veil-db.py CLI."""
from __future__ import annotations

import json
import os
import sqlite3
from pathlib import Path

from shared.tools.veil_delivery_freshness import read_manifest, verify_manifest
from shared.tools.veil_html_assets import _HTML_TEMPLATE, _HTML_UI_BY_LANG
from shared.tools.veil_rule_store import (
    DB_CLI_PATH,
    capture_taxonomy_payload,
    parse_preferred_variants,
)

from .helpers import PROJECT_ROOT, db_cmd


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


def test_init_db_rejects_repo_common_path():
    db = os.path.join(PROJECT_ROOT, "common", "blocked.db")
    result = db_cmd("init-db", "--db", db, "--json", check=False)
    payload = json.loads(result.stdout)
    assert result.returncode == 1
    assert payload["reason"] == "store.protected_output_path"


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


def test_parse_preferred_variants_preserves_slash_value() -> None:
    assert parse_preferred_variants("input / output") == ("input / output", None, None)


def test_parse_preferred_variants_splits_bar_separated_values() -> None:
    assert parse_preferred_variants("present state | current status | current snapshot") == (
        "present state",
        "current status",
        "current snapshot",
    )


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
        "should",
        "--json",
    )
    payload = json.loads(result.stdout)
    assert payload["row"]["profile_level"] == "recommended"


def test_upsert_batch_uses_validated_json_without_shell_interpolation(tmp_db, tmp_path: Path):
    batch_path = tmp_path / "accepted-rules.json"
    batch_path.write_text(
        json.dumps(
            {
                "contract_version": "1",
                "rules": [
                    {
                        "term": "current state",
                        "preferred": "present state",
                        "source_context": "veil-capture batch",
                    },
                    {
                        "term": "literal $(not-executed); value",
                        "preferred": "literal preferred && unchanged",
                    },
                ],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    result = db_cmd(
        "upsert-batch",
        "--db",
        tmp_db,
        "--input-json",
        str(batch_path),
        "--json",
    )
    payload = json.loads(result.stdout)
    rows = json.loads(db_cmd("readback", "--db", tmp_db, "--json").stdout)["rows"]

    assert payload["status"] == "ok"
    assert payload["atomic"] is True
    assert payload["processed_count"] == 2
    assert {(row["term_original"], row["preferred"]) for row in rows} == {
        ("current state", "present state"),
        ("literal $(not-executed); value", "literal preferred && unchanged"),
    }


def test_upsert_batch_validates_every_rule_before_any_write(tmp_db, tmp_path: Path):
    batch_path = tmp_path / "invalid-rules.json"
    batch_path.write_text(
        json.dumps(
            {
                "contract_version": "1",
                "rules": [
                    {"term": "would write", "preferred": "must not write"},
                    {"term": "broken", "preferred": "value", "shell": "forbidden"},
                ],
            }
        ),
        encoding="utf-8",
    )

    result = db_cmd(
        "upsert-batch",
        "--db",
        tmp_db,
        "--input-json",
        str(batch_path),
        "--json",
        check=False,
    )
    payload = json.loads(result.stdout)
    rows = json.loads(db_cmd("readback", "--db", tmp_db, "--json").stdout)["rows"]

    assert result.returncode == 1
    assert payload["reason"] == "invalid_batch_payload"
    assert payload["processed_count"] == 0
    assert rows == []


def test_upsert_batch_rejects_invalid_rule_semantics_before_any_write(tmp_db, tmp_path: Path):
    batch_path = tmp_path / "invalid-level-rules.json"
    batch_path.write_text(
        json.dumps(
            {
                "contract_version": "1",
                "rules": [
                    {"term": "would write", "preferred": "must not write"},
                    {"term": "broken", "preferred": "value", "level": "typo"},
                ],
            }
        ),
        encoding="utf-8",
    )

    result = db_cmd(
        "upsert-batch",
        "--db",
        tmp_db,
        "--input-json",
        str(batch_path),
        "--json",
        check=False,
    )
    payload = json.loads(result.stdout)
    rows = json.loads(db_cmd("readback", "--db", tmp_db, "--json").stdout)["rows"]

    assert result.returncode == 1
    assert payload["reason"] == "store.batch_validation_failed"
    assert payload["failed_index"] == 1
    assert payload["processed_count"] == 0
    assert rows == []


def test_upsert_batch_rolls_back_all_rules_after_sqlite_failure(tmp_db, tmp_path: Path):
    with sqlite3.connect(tmp_db) as conn:
        conn.execute(
            """
            CREATE TRIGGER reject_second_rule
            BEFORE INSERT ON rules
            WHEN NEW.term_normalized = 'second term'
            BEGIN
                SELECT RAISE(ABORT, 'forced batch failure');
            END
            """
        )

    batch_path = tmp_path / "rollback-rules.json"
    batch_path.write_text(
        json.dumps(
            {
                "contract_version": "1",
                "rules": [
                    {"term": "first term", "preferred": "first preferred"},
                    {"term": "second term", "preferred": "second preferred"},
                ],
            }
        ),
        encoding="utf-8",
    )

    result = db_cmd(
        "upsert-batch",
        "--db",
        tmp_db,
        "--input-json",
        str(batch_path),
        "--json",
        check=False,
    )
    payload = json.loads(result.stdout)
    rows = json.loads(db_cmd("readback", "--db", tmp_db, "--json").stdout)["rows"]

    assert result.returncode == 1
    assert payload["reason"] == "store.batch_write_failed"
    assert payload["atomic"] is True
    assert payload["processed_count"] == 0
    assert rows == []


def test_delete_rule_removes_row(tmp_db):
    db_cmd("upsert-rule", "--db", tmp_db, "--term", "current state", "--preferred", "present state")
    result = db_cmd("delete-rule", "--db", tmp_db, "--term", "current state", "--json")
    payload = json.loads(result.stdout)
    assert payload["status"] == "ok"
    assert payload["action"] == "deleted"
    rows = json.loads(db_cmd("readback", "--db", tmp_db, "--json").stdout)["rows"]
    assert rows == []


def test_delete_rule_missing_returns_skip(tmp_db):
    result = db_cmd("delete-rule", "--db", tmp_db, "--term", "missing term", "--json", check=False)
    payload = json.loads(result.stdout)
    assert result.returncode == 1
    assert payload["status"] == "skip"
    assert payload["reason"] == "store.rule_not_found"


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


def test_export_html(tmp_db, tmp_path):
    db_cmd("upsert-rule", "--db", tmp_db, "--term", "current state", "--preferred", "present state")
    html_path = str(tmp_path / "veil.html")
    db_cmd("export-html", "--db", tmp_db, "--html-path", html_path)
    assert os.path.exists(html_path)
    content = Path(html_path).read_text(encoding="utf-8")
    assert "current state" in content
    assert "present state" in content
    assert "Manual copy prompt opened." in content
    assert "Clipboard access is unavailable. Copy this text manually:" in content
    assert "opacity: 0" not in content
    assert "Register or change a rule" in content
    assert "AI review recovery" in content
    assert 'id="capture-input"' in content
    assert 'id="capture-analyze-btn"' in content
    assert 'id="capture-copy-exceptions-btn"' in content
    assert "analyzeCaptureInput()" in content
    assert "function copyCaptureReviewRequest()" in content
    assert "Copy complete AI review request" in content
    assert "evidence-backed semantic decision frames (contract v2)" in content
    assert "separate critic pass" in content
    assert "diagnostic_only: true" in content
    assert "write_allowed: false" in content
    assert content.index('id="capture-copy-exceptions-btn"') < content.index('id="capture-analyze-btn"')
    assert "__UI_CAPTURE_EXCEPTIONS_COPY_BTN__" not in content
    assert "Select a term to continue" not in content
    assert "用語を選んで続け" not in content
    assert "function analyzeCaptureOutcomes(text)" in content
    assert "existing-match" in content
    assert "loadCaptureResult(" in content
    assert "capture-result-line" in content
    assert "coined_or_shortened" in content
    assert 'id="capture-copy-prompt-btn"' not in content
    assert "The local preview found no possible exception." in content
    assert "No vocabulary decision is needed." not in content
    assert 'id="register-btn"' in content
    assert 'id="register-commands-btn"' in content
    assert 'id="col-actions"' in content
    assert "copyDeleteInstruction(this)" in content
    assert "copyRegisterPrompt()" in content
    assert "delete-rule" in content
    assert "export-html" in content
    assert "upsert-rule" in content
    assert "--level" not in content
    assert 'id="new-level"' not in content
    assert "Run these commands to delete this rule:" in content
    assert "Run these commands to register this rule:" in content
    assert "Copy save request" in content
    assert "Advanced: copy commands" in content
    assert "Register this VEIL rule in the current repository:" in content
    assert "Update the SQLite canonical, then regenerate the mirror and veil.html." in content
    assert "navigator.clipboard.writeText" in content
    assert "openManualCopy(text)" in content
    for forbidden_browser_write in ("fetch(", "XMLHttpRequest", "indexedDB", "localStorage", "sessionStorage", "WebSocket"):
        assert forbidden_browser_write not in content
    assert "navigator.languages" in content
    assert "const _captureConfig =" in content
    assert r"masked.split(/\r?\n/)" in content
    assert r"].join('\n\n');" in content
    assert r"].join('\n');" in content
    assert r"lines.join('\n')" in content
    assert '"zh-hans"' in content
    assert '"zh-hant"' in content
    assert '"ko"' in content
    assert '"ar"' in content
    assert "document.documentElement.dir = isRtlLocale" in content
    assert "竊" not in content
    assert "용어 규칙" in content
    assert "词汇规则" in content
    assert "詞彙規則" in content
    assert "قواعد المصطلحات" in content
    manifest, error = read_manifest(content)
    assert error is None
    assert manifest is not None
    rows = json.loads(db_cmd("readback", "--db", tmp_db, "--json").stdout)["rows"]
    assert verify_manifest(
        content,
        template=_HTML_TEMPLATE,
        ui_by_lang=_HTML_UI_BY_LANG,
        capture_taxonomy=capture_taxonomy_payload(),
        rows=rows,
        settings={
            "db_cli_path": DB_CLI_PATH,
            "db_path": Path(tmp_db).as_posix(),
            "html_path": Path(html_path).as_posix(),
            "default_lang": "en",
        },
    ) == "OK"


def test_html_manifest_marks_missing_legacy_and_tampered_content(tmp_db, tmp_path):
    db_cmd("upsert-rule", "--db", tmp_db, "--term", "current state", "--preferred", "present state")
    html_path = str(tmp_path / "veil.html")
    db_cmd("export-html", "--db", tmp_db, "--html-path", html_path)
    content = Path(html_path).read_text(encoding="utf-8")
    rows = json.loads(db_cmd("readback", "--db", tmp_db, "--json").stdout)["rows"]
    inputs = {
        "template": _HTML_TEMPLATE,
        "ui_by_lang": _HTML_UI_BY_LANG,
        "capture_taxonomy": capture_taxonomy_payload(),
        "rows": rows,
        "settings": {
            "db_cli_path": DB_CLI_PATH,
            "db_path": Path(tmp_db).as_posix(),
            "html_path": Path(html_path).as_posix(),
            "default_lang": "en",
        },
    }
    assert verify_manifest(content.replace(' type="application/json"', ' type="application/x-json"'), **inputs) == "STALE"
    assert verify_manifest(content.replace('"format":1', '"format":'), **inputs) == "ERROR"
    assert verify_manifest(content.replace("Vocabulary Rules", "Vocabulary Rules changed", 1), **inputs) == "ERROR"


def test_html_manifest_marks_changed_canonical_rows_stale(tmp_db, tmp_path):
    html_path = str(tmp_path / "veil.html")
    db_cmd("upsert-rule", "--db", tmp_db, "--term", "current state", "--preferred", "present state")
    db_cmd("export-html", "--db", tmp_db, "--html-path", html_path)
    db_cmd("upsert-rule", "--db", tmp_db, "--term", "current issue", "--preferred", "current problem")
    rows = json.loads(db_cmd("readback", "--db", tmp_db, "--json").stdout)["rows"]
    assert verify_manifest(
        Path(html_path).read_text(encoding="utf-8"), template=_HTML_TEMPLATE, ui_by_lang=_HTML_UI_BY_LANG,
        capture_taxonomy=capture_taxonomy_payload(), rows=rows,
        settings={"db_cli_path": DB_CLI_PATH, "db_path": Path(tmp_db).as_posix(), "html_path": Path(html_path).as_posix(), "default_lang": "en"},
    ) == "STALE"

def test_readback_releases_db_handle(tmp_path: Path) -> None:
    db = tmp_path / "handle-check.db"
    db_cmd("init-db", "--db", str(db))
    db_cmd("upsert-rule", "--db", str(db), "--term", "current state", "--preferred", "present state")

    result = db_cmd("readback", "--db", str(db), "--json")
    payload = json.loads(result.stdout)

    assert payload["status"] == "ok"
    db.unlink()
    assert not db.exists()


def test_export_html_releases_output_handles(tmp_path: Path) -> None:
    db = tmp_path / "export.db"
    html_path = tmp_path / "veil.html"
    db_cmd("init-db", "--db", str(db))
    db_cmd("upsert-rule", "--db", str(db), "--term", "current state", "--preferred", "present state")

    result = db_cmd("export-html", "--db", str(db), "--html-path", str(html_path), "--json")
    payload = json.loads(result.stdout)

    assert payload["status"] == "ok"
    html_path.unlink()
    db.unlink()
    assert not html_path.exists()
    assert not db.exists()


def test_readback_legacy_db_without_profile_level_column(tmp_path: Path) -> None:
    db = tmp_path / "legacy.db"
    conn = sqlite3.connect(db)
    conn.execute(
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
        )
        """
    )
    conn.execute(
        """
        INSERT INTO rules (
            term_original,
            term_normalized,
            preferred,
            preferred_alt_2,
            preferred_alt_3,
            status,
            category_hint,
            note,
            source_context,
            created_at,
            updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            "current state",
            "current state",
            "present state",
            "current status",
            None,
            "active",
            None,
            None,
            "legacy.md:1",
            "2026-01-01T00:00:00+00:00",
            "2026-01-01T00:00:00+00:00",
        ),
    )
    conn.commit()
    conn.close()

    result = db_cmd("readback", "--db", str(db), "--json")
    payload = json.loads(result.stdout)

    assert payload["status"] == "ok"
    assert payload["summary"]["total"] == 1
    assert payload["rows"][0]["term_original"] == "current state"
    assert payload["rows"][0]["profile_level"] == "required"


def test_import_bundled_default_profile(tmp_db: str) -> None:
    bundled_seed = os.path.join(PROJECT_ROOT, "shared", "default-profile", "technical-writing-default.json")
    result = db_cmd("import-seed", "--db", tmp_db, "--seed-file", bundled_seed, "--yes", "--json")
    payload = json.loads(result.stdout)

    assert payload["status"] == "ok"
    assert payload["imported_count"] == 3

    readback = json.loads(db_cmd("readback", "--db", tmp_db, "--json").stdout)
    rows = {row["term_original"]: row for row in readback["rows"]}
    assert rows["current state"]["preferred"] == "present state"
    assert rows["current state"]["preferred_alt_2"] == "current status"
    assert rows["current issue"]["preferred"] == "current problem"
    assert rows["unstable wording"]["preferred"] == "inconsistent phrasing"


def test_export_html_rejects_repo_archive_path(tmp_db):
    html_path = os.path.join(PROJECT_ROOT, "archive", "veil-generated.html")
    result = db_cmd("export-html", "--db", tmp_db, "--html-path", html_path, "--json", check=False)
    payload = json.loads(result.stdout)
    assert result.returncode == 1
    assert payload["reason"] == "store.protected_output_path"


def test_corrupted_db_returns_error(tmp_path):
    db = tmp_path / "bad.db"
    db.write_text("not a sqlite database", encoding="utf-8")
    result = db_cmd("readback", "--db", str(db), "--json", check=False)
    payload = json.loads(result.stdout)
    assert result.returncode == 1
    assert payload["status"] == "error"
    db.unlink()
    assert not db.exists()


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
