"""Installer delivery-contract tests."""
from __future__ import annotations

from pathlib import Path

from .helpers import PROJECT_ROOT


def _assert_html_refresh_after_seed_guard(script: str, guard_end: str) -> None:
    assert script.count("export-html") == 1
    assert guard_end in script
    assert script.index("export-html") > script.index(guard_end)


def test_windows_reinstall_refreshes_html_without_reseeding_db() -> None:
    script = (Path(PROJECT_ROOT) / "install.ps1").read_text(encoding="utf-8")

    _assert_html_refresh_after_seed_guard(
        script,
        'Write-Host "[OK] default rules $DefaultProfileSeed"\n}',
    )
    assert 'Write-Host "[OK] veil.html      $HtmlPath"' in script


def test_posix_reinstall_refreshes_html_without_reseeding_db() -> None:
    script = (Path(PROJECT_ROOT) / "install.sh").read_text(encoding="utf-8")

    _assert_html_refresh_after_seed_guard(
        script,
        'echo "[OK] default rules $DEFAULT_PROFILE_SEED"\nfi',
    )
    assert 'echo "[OK] veil.html      $HTML_PATH"' in script
