"""CLI subprocess helpers for VEIL tests."""
from __future__ import annotations

import os
import subprocess
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PYTHON = sys.executable

_DB_SCRIPT = os.path.join(PROJECT_ROOT, "shared", "tools", "veil-db.py")
_SYNC_SCRIPT = os.path.join(PROJECT_ROOT, "shared", "runtime", "veil-sync.py")
_LINT_SCRIPT = os.path.join(PROJECT_ROOT, "shared", "runtime", "veil-lint.py")
_NORMALIZE_SCRIPT = os.path.join(PROJECT_ROOT, "shared", "runtime", "veil-normalize.py")
_CLASSIFY_SCRIPT = os.path.join(PROJECT_ROOT, "shared", "runtime", "veil-classify.py")


def _run(
    script: str,
    *args: str,
    check: bool = True,
    input: str | None = None,
    env_overrides: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    env = {**os.environ, "VEIL_LANG": "en", "PYTHONUTF8": "1"}
    if env_overrides:
        env.update(env_overrides)
    return subprocess.run(
        [PYTHON, script, *args],
        check=check,
        capture_output=True,
        text=True,
        cwd=PROJECT_ROOT,
        env=env,
        input=input,
    )


def db_cmd(
    *args: str,
    check: bool = True,
    input: str | None = None,
    env_overrides: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    return _run(_DB_SCRIPT, *args, check=check, input=input, env_overrides=env_overrides)


def sync_cmd(
    *args: str,
    check: bool = True,
    env_overrides: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    return _run(_SYNC_SCRIPT, *args, check=check, env_overrides=env_overrides)


def lint_cmd(
    *args: str,
    check: bool = True,
    env_overrides: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    return _run(_LINT_SCRIPT, *args, check=check, env_overrides=env_overrides)


def normalize_cmd(
    *args: str,
    check: bool = True,
    env_overrides: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    return _run(_NORMALIZE_SCRIPT, *args, check=check, env_overrides=env_overrides)


def classify_cmd(
    *args: str,
    check: bool = True,
    input: str | None = None,
    env_overrides: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    return _run(_CLASSIFY_SCRIPT, *args, check=check, input=input, env_overrides=env_overrides)


_STATUS_SCRIPT = os.path.join(PROJECT_ROOT, "shared", "runtime", "veil-status.py")
_PROFILE_AUDIT_SCRIPT = os.path.join(PROJECT_ROOT, "shared", "tools", "veil-profile-audit.py")
_PROFILE_EXPORT_SCRIPT = os.path.join(PROJECT_ROOT, "shared", "tools", "veil-profile-export.py")


def status_cmd(
    *args: str,
    check: bool = True,
    env_overrides: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    return _run(_STATUS_SCRIPT, *args, check=check, env_overrides=env_overrides)


def profile_audit_cmd(
    *args: str,
    check: bool = True,
    env_overrides: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    return _run(_PROFILE_AUDIT_SCRIPT, *args, check=check, env_overrides=env_overrides)


def profile_export_cmd(
    *args: str,
    check: bool = True,
    env_overrides: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    return _run(_PROFILE_EXPORT_SCRIPT, *args, check=check, env_overrides=env_overrides)
