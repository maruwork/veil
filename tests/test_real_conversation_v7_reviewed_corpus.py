from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest


MODULE_PATH = Path(__file__).resolve().parents[1] / "workspace/audit/20260722-real-conversation-ux-v7/validate_reviewed_corpus.py"
SPEC = importlib.util.spec_from_file_location("v7_reviewed_corpus", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)


def write_json(path: Path, value: object) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def write_jsonl(path: Path, rows: list[dict[str, object]]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8")
    return path


def fixture(tmp_path: Path) -> dict[str, Path]:
    source_text = "この作業では計画モードを使う。"
    source = write_jsonl(tmp_path / "input/source.jsonl", [{"session_id": "s1", "source_text": source_text}])
    snapshot = write_json(tmp_path / "reviewed/snapshot.json", {"contract_version": "2", "read_at": "2026-07-22T00:00:00+00:00", "source": "read-only", "normalized_active_terms": []})
    frame: dict[str, object] = {
        "term": "計画モード", "intent": "adopt", "persistence": "temporary", "polarity": "affirmed",
        "scope": "one-off", "impact": "medium", "term_evidence": {"text": "計画モード", "occurrence": 1},
        "intent_evidence": [{"text": "計画モードを使う", "occurrence": 1}], "confidence": "high",
    }
    reviewer_a = {
        "contract_version": "2", "case_id": "case-1", "session_id": "s1", "context": source_text,
        "term": "計画モード", "registered_terms": [], "expected_outcome": "observe", "impact": "medium",
        "reason": "temporary one-off adoption", "source_class": "anonymized-real-conversation",
        "reviewer": {"id": "reviewer-a-v7", "reviewed_at": "2026-07-22T00:00:00+00:00"},
        "second_review": "pending", "provenance": {"kind": "anonymized-real-conversation", "scope_id": "20260722-real-conversation-ux-v7", "contains_real_conversation": True},
        "review_frame": frame,
    }
    reviewer_b = {
        "case_id": "case-1", "session_id": "s1", "context": source_text, "term": "計画モード",
        "registered_terms": [], "review_frame": frame, "expected_outcome": "observe",
        "reviewer": {"id": "reviewer-b-v7", "reviewed_at": "2026-07-22T00:01:00+00:00"},
        "verdict": "agree", "reason": "matrix row 5 applies independently",
    }
    return {
        "source": source,
        "snapshot": snapshot,
        "reviewer_a": write_jsonl(tmp_path / "reviewed/a.jsonl", [reviewer_a]),
        "reviewer_b": write_jsonl(tmp_path / "reviewed/b.jsonl", [reviewer_b]),
    }


def test_merges_agreeing_independent_review_artifacts(tmp_path: Path) -> None:
    state = fixture(tmp_path)

    merged, report = validator.validate_reviewed_corpus(**{f"{key}_path": value for key, value in state.items()})

    assert merged[0]["second_review"]["reviewer_id"] == "reviewer-b-v7"
    assert merged[0]["second_review"]["verdict"] == "agree"
    assert report["outcome_counts"] == {"observe": 1}


def test_rejects_reviewer_b_outcome_disagreement(tmp_path: Path) -> None:
    state = fixture(tmp_path)
    rows = validator.read_jsonl(state["reviewer_b"])
    rows[0]["expected_outcome"] = "exception"
    write_jsonl(state["reviewer_b"], rows)

    with pytest.raises(ValueError, match="does not agree"):
        validator.validate_reviewed_corpus(**{f"{key}_path": value for key, value in state.items()})


def test_rejects_reviewer_b_different_primary_target(tmp_path: Path) -> None:
    state = fixture(tmp_path)
    rows = validator.read_jsonl(state["reviewer_b"])
    rows[0]["term"] = "別の対象"
    rows[0]["review_frame"]["term"] = "別の対象"
    rows[0]["review_frame"]["term_evidence"] = {"text": "この作業", "occurrence": 1}
    write_jsonl(state["reviewer_b"], rows)

    with pytest.raises(ValueError, match="primary target differs"):
        validator.validate_reviewed_corpus(**{f"{key}_path": value for key, value in state.items()})


def test_rejects_outcome_that_conflicts_with_matrix(tmp_path: Path) -> None:
    state = fixture(tmp_path)
    rows = validator.read_jsonl(state["reviewer_a"])
    rows[0]["expected_outcome"] = "exception"
    write_jsonl(state["reviewer_a"], rows)

    with pytest.raises(ValueError, match="does not follow"):
        validator.validate_reviewed_corpus(**{f"{key}_path": value for key, value in state.items()})
