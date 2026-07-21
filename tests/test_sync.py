"""Unit tests for veil-sync.py CLI."""
from __future__ import annotations

import json
import os
import re
from pathlib import Path

from .helpers import PROJECT_ROOT, db_cmd, lint_cmd, sync_cmd


def _make_target(tmp_path: Path, name: str = "CLAUDE.md") -> str:
    p = tmp_path / name
    p.write_text("# Test target\n", encoding="utf-8")
    return str(p)


def _veil_block_lines(content: str, start: str, end: str) -> list[str]:
    match = re.search(re.escape(start) + r"\n(.*?)\n" + re.escape(end), content, flags=re.DOTALL)
    assert match is not None
    return match.group(1).splitlines()


def test_add_registers_target(seeded, tmp_path, tmp_cfg):
    target = _make_target(tmp_path)
    sync_cmd("--config-dir", tmp_cfg, "--db", seeded["db"], "--add", target)
    result = sync_cmd("--config-dir", tmp_cfg, "--db", seeded["db"], "--list")
    assert target in result.stdout


def test_add_injects_veil_block(seeded, tmp_path, tmp_cfg):
    target = _make_target(tmp_path)
    sync_cmd("--config-dir", tmp_cfg, "--db", seeded["db"], "--add", target)
    content = open(target, encoding="utf-8").read()
    assert "VEIL_START" in content
    assert "present state" in content


def test_list_empty(tmp_cfg, tmp_db):
    result = sync_cmd("--config-dir", tmp_cfg, "--db", tmp_db, "--list")
    assert result.returncode == 0


def test_list_missing_target_format(tmp_cfg, tmp_path):
    missing = str(tmp_path / "missing.md")
    cfg_path = Path(tmp_cfg) / "targets.json"
    cfg_path.write_text(json.dumps([missing]), encoding="utf-8")
    result = sync_cmd("--config-dir", tmp_cfg, "--db", str(tmp_path / "veil.db"), "--list")
    assert "[[x]" not in result.stdout
    assert "[x] (not found)" in result.stdout


def test_remove_unregisters_target(seeded, tmp_path, tmp_cfg):
    target = _make_target(tmp_path)
    sync_cmd("--config-dir", tmp_cfg, "--db", seeded["db"], "--add", target)
    sync_cmd("--config-dir", tmp_cfg, "--db", seeded["db"], "--remove", target)
    result = sync_cmd("--config-dir", tmp_cfg, "--db", seeded["db"], "--list")
    assert target not in result.stdout


def test_purge_removes_veil_block(seeded, tmp_path, tmp_cfg):
    target = _make_target(tmp_path)
    sync_cmd("--config-dir", tmp_cfg, "--db", seeded["db"], "--add", target)
    assert "VEIL_START" in open(target, encoding="utf-8").read()
    sync_cmd("--config-dir", tmp_cfg, "--db", seeded["db"], "--remove", target, "--purge")
    assert "VEIL_START" not in open(target, encoding="utf-8").read()


def test_behavior_md_injected(seeded, tmp_path, tmp_cfg):
    behavior = os.path.join(tmp_cfg, "behavior.md")
    with open(behavior, "w", encoding="utf-8") as f:
        f.write("Test behavior rule.\n")
    target = _make_target(tmp_path)
    sync_cmd("--config-dir", tmp_cfg, "--db", seeded["db"], "--add", target)
    content = open(target, encoding="utf-8").read()
    assert "Test behavior rule" in content


def test_add_comments_every_line_for_yaml_target(seeded, tmp_path, tmp_cfg):
    target = _make_target(tmp_path, ".aider.conf.yml")
    sync_cmd("--config-dir", tmp_cfg, "--db", seeded["db"], "--add", target)
    content = Path(target).read_text(encoding="utf-8")
    body_lines = _veil_block_lines(content, "# VEIL_START", "# VEIL_END")

    assert body_lines
    assert all(line.startswith("#") for line in body_lines)
    assert "Terminology rules:" not in body_lines


def test_add_comments_every_line_for_toml_target(seeded, tmp_path, tmp_cfg):
    target = _make_target(tmp_path, "tool.toml")
    sync_cmd("--config-dir", tmp_cfg, "--db", seeded["db"], "--add", target)
    content = Path(target).read_text(encoding="utf-8")
    body_lines = _veil_block_lines(content, "# VEIL_START", "# VEIL_END")

    assert body_lines
    assert all(line.startswith("#") for line in body_lines)
    assert "current state -> present state / current status" not in body_lines


def test_add_comments_every_line_for_ini_target(seeded, tmp_path, tmp_cfg):
    target = _make_target(tmp_path, "tool.ini")
    sync_cmd("--config-dir", tmp_cfg, "--db", seeded["db"], "--add", target)
    content = Path(target).read_text(encoding="utf-8")
    body_lines = _veil_block_lines(content, "# VEIL_START", "# VEIL_END")

    assert body_lines
    assert all(line.startswith("#") for line in body_lines)


def test_sync_updates_existing_target(seeded, tmp_path, tmp_cfg):
    target = _make_target(tmp_path)
    sync_cmd("--config-dir", tmp_cfg, "--db", seeded["db"], "--add", target)
    db_cmd("upsert-rule", "--db", seeded["db"], "--term", "old term", "--preferred", "new term")
    sync_cmd("--config-dir", tmp_cfg, "--db", seeded["db"])
    content = open(target, encoding="utf-8").read()
    assert "new term" in content


def test_registered_rule_syncs_and_lint_enforces_preferred_form(seeded, tmp_path, tmp_cfg):
    target = _make_target(tmp_path)
    sync_cmd("--config-dir", tmp_cfg, "--db", seeded["db"], "--add", target)

    content = open(target, encoding="utf-8").read()
    assert "current state -> present state" in content
    assert "current status" not in content

    violation = lint_cmd("--db", seeded["db"], "--text", "The current state is unstable.", "--json", check=False)
    violation_payload = json.loads(violation.stdout)
    assert violation.returncode != 0
    assert violation_payload["violations"][0]["original"] == "current state"
    assert violation_payload["violations"][0]["preferred"] == "present state"

    clean = lint_cmd("--db", seeded["db"], "--text", "The present state is stable.", "--json", check=False)
    clean_payload = json.loads(clean.stdout)
    assert clean.returncode == 0
    assert clean_payload["violations"] == []


def test_sync_corrupted_db_fails_cleanly(tmp_path, tmp_cfg):
    target = _make_target(tmp_path)
    bad_db = tmp_path / "bad.db"
    bad_db.write_text("not a sqlite database", encoding="utf-8")
    result = sync_cmd("--config-dir", tmp_cfg, "--db", str(bad_db), "--add", target, check=False)
    assert result.returncode == 1
    assert "cannot load source rules" in result.stdout.lower()


def test_sync_corrupted_db_does_not_register_target(tmp_path, tmp_cfg):
    target = _make_target(tmp_path)
    bad_db = tmp_path / "bad.db"
    bad_db.write_text("not a sqlite database", encoding="utf-8")
    failed = sync_cmd("--config-dir", tmp_cfg, "--db", str(bad_db), "--add", target, check=False)
    assert "Registered:" not in failed.stdout
    listed = sync_cmd("--config-dir", tmp_cfg, "--db", str(bad_db), "--list")
    assert target not in listed.stdout


def test_add_rejects_repo_common_target(tmp_cfg, tmp_db):
    target = os.path.join(PROJECT_ROOT, "common", "AGENTS.md")
    result = sync_cmd("--config-dir", tmp_cfg, "--db", tmp_db, "--add", target, check=False)
    assert result.returncode == 1
    assert "common" in result.stdout.lower()


def test_sync_skips_protected_registered_target(seeded, tmp_cfg):
    target = os.path.join(PROJECT_ROOT, "archive", "AGENTS.md")
    cfg_path = Path(tmp_cfg) / "targets.json"
    cfg_path.write_text(json.dumps([target]), encoding="utf-8")
    result = sync_cmd("--config-dir", tmp_cfg, "--db", seeded["db"])
    assert result.returncode == 0
    assert "protected repo directory" in result.stdout.lower()
