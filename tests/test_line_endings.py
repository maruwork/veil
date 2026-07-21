"""Executable-script line-ending contracts."""
from __future__ import annotations

from pathlib import Path

from .helpers import PROJECT_ROOT


def test_posix_installer_uses_lf_only() -> None:
    content = (Path(PROJECT_ROOT) / "install.sh").read_bytes()

    assert b"\r" not in content


def test_posix_installer_has_git_lf_contract() -> None:
    attributes = (Path(PROJECT_ROOT) / ".gitattributes").read_text(encoding="utf-8").splitlines()

    assert "/install.sh text eol=lf" in attributes
