"""Unit tests for veil-sync.py CLI."""
from __future__ import annotations

import os
from pathlib import Path

from .helpers import sync_cmd, db_cmd


def _make_target(tmp_path: Path, name: str = "CLAUDE.md") -> str:
    p = tmp_path / name
    p.write_text("# Test target\n", encoding="utf-8")
    return str(p)


def test_add_registers_target(seeded, tmp_path, tmp_cfg):
    target = _make_target(tmp_path)
    sync_cmd("--config-dir", tmp_cfg, "--db", seeded["db"], "--rules-dir", seeded["rules"], "--add", target)
    result = sync_cmd("--config-dir", tmp_cfg, "--db", seeded["db"], "--rules-dir", seeded["rules"], "--list")
    assert target in result.stdout


def test_add_injects_veil_block(seeded, tmp_path, tmp_cfg):
    target = _make_target(tmp_path)
    sync_cmd("--config-dir", tmp_cfg, "--db", seeded["db"], "--rules-dir", seeded["rules"], "--add", target)
    content = open(target, encoding="utf-8").read()
    assert "VEIL_START" in content
    assert "present state" in content


def test_list_empty(tmp_cfg, tmp_db, tmp_rules):
    result = sync_cmd("--config-dir", tmp_cfg, "--db", tmp_db, "--rules-dir", tmp_rules, "--list")
    assert result.returncode == 0


def test_remove_unregisters_target(seeded, tmp_path, tmp_cfg):
    target = _make_target(tmp_path)
    sync_cmd("--config-dir", tmp_cfg, "--db", seeded["db"], "--rules-dir", seeded["rules"], "--add", target)
    sync_cmd("--config-dir", tmp_cfg, "--db", seeded["db"], "--rules-dir", seeded["rules"], "--remove", target)
    result = sync_cmd("--config-dir", tmp_cfg, "--db", seeded["db"], "--rules-dir", seeded["rules"], "--list")
    assert target not in result.stdout


def test_purge_removes_veil_block(seeded, tmp_path, tmp_cfg):
    target = _make_target(tmp_path)
    sync_cmd("--config-dir", tmp_cfg, "--db", seeded["db"], "--rules-dir", seeded["rules"], "--add", target)
    assert "VEIL_START" in open(target, encoding="utf-8").read()
    sync_cmd("--config-dir", tmp_cfg, "--db", seeded["db"], "--rules-dir", seeded["rules"], "--remove", target, "--purge")
    assert "VEIL_START" not in open(target, encoding="utf-8").read()


def test_behavior_md_injected(seeded, tmp_path, tmp_cfg):
    behavior = os.path.join(tmp_cfg, "behavior.md")
    with open(behavior, "w", encoding="utf-8") as f:
        f.write("Test behavior rule.\n")
    target = _make_target(tmp_path)
    sync_cmd("--config-dir", tmp_cfg, "--db", seeded["db"], "--rules-dir", seeded["rules"], "--add", target)
    content = open(target, encoding="utf-8").read()
    assert "Test behavior rule" in content


def test_sync_updates_existing_target(seeded, tmp_path, tmp_cfg):
    target = _make_target(tmp_path)
    sync_cmd("--config-dir", tmp_cfg, "--db", seeded["db"], "--rules-dir", seeded["rules"], "--add", target)
    db_cmd("upsert-rule", "--db", seeded["db"], "--term", "old term", "--preferred", "new term")
    db_cmd("export-mirror", "--db", seeded["db"], "--rules-dir", seeded["rules"])
    sync_cmd("--config-dir", tmp_cfg, "--db", seeded["db"], "--rules-dir", seeded["rules"])
    content = open(target, encoding="utf-8").read()
    assert "new term" in content
