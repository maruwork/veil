"""Shared fixtures for VEIL pytest suite."""
from __future__ import annotations

import os
from pathlib import Path
from uuid import uuid4

import pytest

from .helpers import db_cmd


def pytest_configure(config: pytest.Config) -> None:
    """Keep each default test run isolated under the approved audit shelf."""
    if config.getoption("basetemp") is not None:
        return
    project_root = Path(__file__).resolve().parents[1]
    config.option.basetemp = str(project_root / "workspace" / "audit" / f"pytest-{uuid4().hex}")


@pytest.fixture
def tmp_db(tmp_path: Path) -> str:
    db = str(tmp_path / "veil.db")
    if os.path.exists(db):
        os.remove(db)
    db_cmd("init-db", "--db", db)
    return db


@pytest.fixture
def tmp_cfg(tmp_path: Path) -> str:
    cfg = str(tmp_path / "veilcfg")
    os.makedirs(cfg)
    return cfg


@pytest.fixture
def seeded(tmp_path: Path) -> dict[str, str]:
    db = str(tmp_path / "veil.db")
    if os.path.exists(db):
        os.remove(db)
    db_cmd("init-db", "--db", db)
    db_cmd("upsert-rule", "--db", db, "--term", "current state", "--preferred", "present state", "--preferred-alt-2", "current status")
    return {"db": db}
