"""Shared fixtures for VEIL pytest suite."""
from __future__ import annotations

import os
from pathlib import Path

import pytest

from .helpers import db_cmd


@pytest.fixture
def tmp_db(tmp_path: Path) -> str:
    db = str(tmp_path / "veil.db")
    db_cmd("init-db", "--db", db)
    return db


@pytest.fixture
def tmp_rules(tmp_path: Path) -> str:
    rules = str(tmp_path / "rules")
    os.makedirs(rules)
    return rules


@pytest.fixture
def tmp_cfg(tmp_path: Path) -> str:
    cfg = str(tmp_path / "veilcfg")
    os.makedirs(cfg)
    return cfg


@pytest.fixture
def seeded(tmp_path: Path) -> dict[str, str]:
    db = str(tmp_path / "veil.db")
    rules = str(tmp_path / "rules")
    os.makedirs(rules)
    db_cmd("init-db", "--db", db)
    db_cmd("upsert-rule", "--db", db, "--term", "current state", "--preferred", "present state", "--preferred-alt-2", "current status")
    db_cmd("export-mirror", "--db", db, "--rules-dir", rules)
    return {"db": db, "rules": rules}
