from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SKILL_PATHS = [
    PROJECT_ROOT / "skills" / "claude-code" / "veil-capture.md",
    PROJECT_ROOT / "skills" / "codex" / "veil-capture" / "SKILL.md",
]


def test_veil_capture_skill_files_are_utf8_clean() -> None:
    for path in SKILL_PATHS:
        content = path.read_text(encoding="utf-8")
        assert "竊" not in content
        assert "遶翫・" not in content
        assert "陷ｷ" not in content
        assert "窶・" not in content


def test_veil_capture_skill_files_keep_core_registration_contract() -> None:
    for path in SKILL_PATHS:
        content = path.read_text(encoding="utf-8")
        assert '- {term} (current) -> {candidate1} (candidate 1) | {candidate2} (candidate 2)' in content
        assert 'Do not pass `|`-separated strings as `--preferred`.' in content
        assert 'Nothing to adopt.' in content


def test_veil_capture_skill_files_keep_natural_japanese_override_labels() -> None:
    for path in SKILL_PATHS:
        content = path.read_text(encoding="utf-8")
        assert '各候補の「候補 1」を登録します。' in content
        assert '例: "current state -> 現状維持"' in content
