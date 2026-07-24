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


def test_veil_capture_skill_files_use_exclusion_first_contract() -> None:
    for path in SKILL_PATHS:
        content = path.read_text(encoding="utf-8")
        assert "--outcomes" in content
        assert "`exclude`" in content
        assert "`observe`" in content
        assert "`existing-match`" in content
        assert "`exception`" in content
        assert "A normal session requires zero user judgments." in content
        assert "Ask exactly one batched question" in content


def test_veil_capture_skill_files_hide_legacy_candidate_flow() -> None:
    for path in SKILL_PATHS:
        content = path.read_text(encoding="utf-8")
        assert "candidate 1" not in content.lower()
        assert "candidate 2" not in content.lower()
        assert "Candidate 1 will be registered" not in content
        assert "OK to proceed" not in content
        assert "Do not show excluded terms, observed terms, candidate tables" in content


def test_veil_capture_skill_files_keep_safe_registration_contract() -> None:
    for path in SKILL_PATHS:
        content = path.read_text(encoding="utf-8")
        assert 'python {veil_root}/shared/tools/veil-db.py upsert-batch' in content
        assert '"contract_version": "1"' in content
        assert "host argument-array/subprocess API" in content
        assert '--term "{term}"' not in content
        assert "Never automatically create a new canonical rule from repetition alone." in content
        assert "The batch write is all-or-nothing" in content
        assert "`atomic=true`" in content
        assert "whether the batch succeeded or failed" in content
        assert "finally-style cleanup" in content
        assert "Never interpolate untrusted conversation text" in content
        assert "If no targets exist, do not add one." in content
        assert "--add <path>" not in content


def test_veil_capture_skill_files_use_semantic_frames_and_critic() -> None:
    for path in SKILL_PATHS:
        content = path.read_text(encoding="utf-8")
        assert "--semantic-frames <agent-generated-frame-path>" in content
        assert '"contract_version": "2"' in content
        assert "Run a separate critic pass" in content
        assert "diagnostic_only=false" in content
        assert "Never fall back to raw-text outcomes as semantic" in content
        assert "After a second failure, perform no DB/HTML/sync write" in content


def test_veil_capture_skill_files_use_plural_safe_batch_confirmation() -> None:
    for path in SKILL_PATHS:
        content = path.read_text(encoding="utf-8")
        assert "Registered {count} term(s): {term -> preferred; ...}." in content
        assert "{count}件を登録しました：{term -> preferred; ...}。" in content
        assert "requested_preferred" in content


def test_veil_capture_skill_files_have_one_line_no_action_copy() -> None:
    for path in SKILL_PATHS:
        content = path.read_text(encoding="utf-8")
        assert "started automatically at task close" in content
        assert "do not add a VEIL-specific line" in content
        assert "No vocabulary decision is needed." in content
        assert "用語について確認が必要なものはありません。" in content
        assert "変更・除外があればその項目だけ" in content
