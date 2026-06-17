"""Tests for veil-profile-audit.py and veil-profile-export.py."""
from __future__ import annotations

import json
import os

from .helpers import db_cmd, profile_audit_cmd, profile_export_cmd


def test_audit_rules_dir_counts(seeded):
    r = profile_audit_cmd("--rules-dir", seeded["rules"], "--json")
    payload = json.loads(r.stdout)
    assert payload["status"] == "ok"
    assert payload["source_type"] == "rules-dir"
    assert payload["summary"]["total_rules"] == 1
    assert payload["summary"]["required_count"] == 1


def test_audit_rules_dir_missing(tmp_path):
    missing = str(tmp_path / "missing-rules")
    r = profile_audit_cmd("--rules-dir", missing, "--json")
    payload = json.loads(r.stdout)
    assert payload["status"] == "skip"
    assert payload["summary"]["total_rules"] == 0


def test_audit_db(tmp_db):
    db_cmd("upsert-rule", "--db", tmp_db, "--term", "foo bar", "--preferred", "baz qux")
    r = profile_audit_cmd("--db", tmp_db, "--json")
    payload = json.loads(r.stdout)
    assert payload["status"] == "ok"
    assert payload["source_type"] == "db"
    assert payload["summary"]["total_rules"] == 1


def test_export_creates_manifest(seeded, tmp_path):
    out = str(tmp_path / "export")
    r = profile_export_cmd(
        "--rules-dir",
        seeded["rules"],
        "--output-dir",
        out,
        "--profile-name",
        "test-profile",
        "--json",
    )
    payload = json.loads(r.stdout)
    assert payload["status"] == "ok"
    assert payload["profile_name"] == "test-profile"
    assert os.path.exists(os.path.join(out, "manifest.json"))
    assert os.path.exists(os.path.join(out, "c.md"))


def test_export_rules_dir_missing(tmp_path):
    out = str(tmp_path / "out")
    rules = str(tmp_path / "nonexistent")
    r = profile_export_cmd("--rules-dir", rules, "--output-dir", out, check=False)
    assert r.returncode == 1