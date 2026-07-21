"""Tests for veil-profile-audit.py and veil-profile-export.py."""
from __future__ import annotations

import json
import os

from .helpers import db_cmd, profile_audit_cmd, profile_export_cmd


def test_audit_db_counts(seeded):
    r = profile_audit_cmd("--db", seeded["db"], "--json")
    payload = json.loads(r.stdout)
    assert payload["status"] == "ok"
    assert payload["source_type"] == "db"
    assert payload["summary"]["total_rules"] == 1
    assert payload["summary"]["required_count"] == 1


def test_audit_seed_file_counts(tmp_path):
    seed_file = tmp_path / "rules.json"
    seed_file.write_text(
        json.dumps(
            {
                "rules": [
                    {
                        "term_original": "alpha",
                        "preferred": "beta",
                        "status": "active",
                        "profile_level": "recommended",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    r = profile_audit_cmd("--seed-file", str(seed_file), "--json")
    payload = json.loads(r.stdout)
    assert payload["status"] == "ok"
    assert payload["source_type"] == "seed-file"
    assert payload["summary"]["recommended_count"] == 1


def test_audit_seed_file_missing(tmp_path):
    missing = str(tmp_path / "missing-rules.json")
    r = profile_audit_cmd("--seed-file", missing, "--json")
    payload = json.loads(r.stdout)
    assert payload["status"] == "skip"
    assert payload["summary"]["total_rules"] == 0


def test_audit_corrupted_db_returns_error(tmp_path):
    db = tmp_path / "bad.db"
    db.write_text("not a sqlite database", encoding="utf-8")
    r = profile_audit_cmd("--db", str(db), "--json", check=False)
    payload = json.loads(r.stdout)
    assert r.returncode == 1
    assert payload["status"] == "error"


def test_export_creates_manifest_and_rules_json(seeded, tmp_path):
    out = str(tmp_path / "export")
    r = profile_export_cmd(
        "--db",
        seeded["db"],
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
    assert os.path.exists(os.path.join(out, "rules.json"))
    assert payload["summary"]["legacy_flat_count"] == 0


def test_export_seed_file_roundtrip(tmp_path):
    source_seed = tmp_path / "seed.json"
    source_seed.write_text(
        json.dumps(
            {
                "rules": [
                    {
                        "term_original": "alpha",
                        "preferred": "beta",
                        "status": "active",
                        "profile_level": "observe",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    out = str(tmp_path / "export")
    r = profile_export_cmd("--seed-file", str(source_seed), "--output-dir", out, "--json")
    payload = json.loads(r.stdout)
    assert payload["status"] == "ok"
    exported_rules = json.loads(open(os.path.join(out, "rules.json"), encoding="utf-8").read())
    assert exported_rules["rules"][0]["term_original"] == "alpha"
    assert exported_rules["rules"][0]["profile_level"] == "observe"


def test_export_missing_seed_file(tmp_path):
    out = str(tmp_path / "out")
    seed_file = str(tmp_path / "nonexistent.json")
    r = profile_export_cmd("--seed-file", seed_file, "--output-dir", out, check=False)
    assert r.returncode == 1


def test_export_from_base_manifest_uses_rules_json(tmp_path):
    seed_source = tmp_path / "seed.json"
    seed_source.write_text(
        json.dumps(
            {
                "rules": [
                    {
                        "term_original": "alpha",
                        "preferred": "beta",
                        "status": "active",
                        "profile_level": "required",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    base_out = tmp_path / "base"
    profile_export_cmd("--seed-file", str(seed_source), "--output-dir", str(base_out), "--profile-name", "base-profile")
    manifest_path = os.path.join(base_out, "manifest.json")

    derived_out = tmp_path / "derived"
    r = profile_export_cmd(
        "--base-manifest",
        manifest_path,
        "--output-dir",
        str(derived_out),
        "--profile-name",
        "derived-profile",
        "--json",
    )
    payload = json.loads(r.stdout)
    assert payload["status"] == "ok"
    exported_rules = json.loads(open(os.path.join(derived_out, "rules.json"), encoding="utf-8").read())
    assert exported_rules["rules"][0]["term_original"] == "alpha"
