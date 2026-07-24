from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest


MODULE_PATH = Path(__file__).resolve().parents[1] / "workspace/audit/20260722-real-conversation-ux-v8/validate_reviewed_corpus.py"
SPEC = importlib.util.spec_from_file_location("v8_reviewed_corpus", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)


def write_json(path: Path, value: object) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=True, indent=2) + "\n", encoding="utf-8", newline="\n")
    return path


def write_jsonl(path: Path, rows: list[dict[str, object]]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(row, ensure_ascii=True) + "\n" for row in rows), encoding="utf-8", newline="\n")
    return path


def fixture(tmp_path: Path) -> dict[str, Path]:
    context = "pier means work-oriented"
    source = write_jsonl(tmp_path / "input/source.jsonl", [{"session_id": "s1", "source_text": context}])
    snapshot = write_json(tmp_path / "reviewed/snapshot.json", {
        "contract_version": "2", "read_at": "2026-07-22T00:00:00+00:00",
        "source": "read-only canonical DB readback", "normalized_active_terms": [],
    })
    frame: dict[str, object] = {
        "term": "pier", "intent": "define", "persistence": "durable", "polarity": "affirmed",
        "scope": "project", "impact": "low", "term_evidence": {"text": "pier", "occurrence": 1},
        "intent_evidence": [{"text": "means work-oriented", "occurrence": 1}], "confidence": "high",
    }
    reviewer_a = {
        "contract_version": "2", "case_id": "case-1", "session_id": "s1", "context": context,
        "term": "pier", "registered_terms": [], "expected_outcome": "exception", "impact": "low",
        "reason": "affirmed durable definition", "source_class": "anonymized-real-conversation",
        "reviewer": {"id": "reviewer-a-v8", "reviewed_at": "2026-07-22T00:00:00+00:00"},
        "second_review": "pending",
        "provenance": {"kind": "anonymized-real-conversation", "scope_id": "20260722-real-conversation-ux-v8", "contains_real_conversation": True},
        "review_frame": frame,
    }
    reviewer_b = {
        "case_id": "case-1", "session_id": "s1", "context": context, "term": "pier",
        "registered_terms": [], "review_frame": frame, "expected_outcome": "exception",
        "reviewer": {"id": "reviewer-b-v8", "reviewed_at": "2026-07-22T00:01:00+00:00"},
        "verdict": "agree", "reason": "matrix row 7 applies independently",
    }
    return {
        "source": source, "snapshot": snapshot,
        "reviewer_a": write_jsonl(tmp_path / "reviewed/a.jsonl", [reviewer_a]),
        "reviewer_b": write_jsonl(tmp_path / "reviewed/b.jsonl", [reviewer_b]),
    }


def validate(state: dict[str, Path]) -> tuple[list[dict[str, object]], dict[str, object]]:
    return validator.validate_reviewed_corpus(**{f"{name}_path": path for name, path in state.items()})


def test_merges_agreeing_independent_v8_review_artifacts(tmp_path: Path) -> None:
    merged, report = validate(fixture(tmp_path))

    assert merged[0]["second_review"]["reviewer_id"] == "reviewer-b-v8"
    assert report["outcome_counts"] == {"exception": 1}


def test_rejects_reviewer_b_outcome_that_conflicts_with_its_matrix(tmp_path: Path) -> None:
    state = fixture(tmp_path)
    rows = validator.read_jsonl(state["reviewer_b"])
    rows[0]["expected_outcome"] = "observe"
    write_jsonl(state["reviewer_b"], rows)

    with pytest.raises(ValueError, match="outcome does not follow"):
        validate(state)


def test_rejects_valid_reviewer_b_outcome_that_disagrees_with_a(tmp_path: Path) -> None:
    state = fixture(tmp_path)
    rows = validator.read_jsonl(state["reviewer_b"])
    rows[0]["review_frame"]["persistence"] = "unclear"
    rows[0]["expected_outcome"] = "observe"
    write_jsonl(state["reviewer_b"], rows)

    with pytest.raises(ValueError, match="does not agree"):
        validate(state)


def test_allows_independent_valid_evidence_and_confidence(tmp_path: Path) -> None:
    state = fixture(tmp_path)
    rows = validator.read_jsonl(state["reviewer_b"])
    rows[0]["case_id"] = "independent-case-id"
    rows[0]["review_frame"]["confidence"] = "low"
    write_jsonl(state["reviewer_b"], rows)

    merged, report = validate(state)

    assert len(merged) == 1
    assert report["outcome_counts"] == {"exception": 1}


def test_rejects_nonoccurring_intent_evidence(tmp_path: Path) -> None:
    state = fixture(tmp_path)
    rows = validator.read_jsonl(state["reviewer_a"])
    rows[0]["review_frame"]["intent_evidence"] = [{"text": "missing", "occurrence": 1}]
    write_jsonl(state["reviewer_a"], rows)

    with pytest.raises(ValueError, match="intent evidence is not exact"):
        validate(state)


def test_rejects_registered_term_not_in_snapshot(tmp_path: Path) -> None:
    state = fixture(tmp_path)
    rows = validator.read_jsonl(state["reviewer_a"])
    rows[0]["registered_terms"] = ["pier"]
    write_jsonl(state["reviewer_a"], rows)

    with pytest.raises(ValueError, match="registered terms do not match"):
        validate(state)
