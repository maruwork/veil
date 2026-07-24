from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest


MODULE_PATH = Path(__file__).resolve().parents[1] / "workspace/audit/20260722-real-conversation-ux-v8/validate_generated_payloads.py"
SPEC = importlib.util.spec_from_file_location("v8_generated_payloads", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)


def write_jsonl(path: Path, row: dict[str, object], *, ensure_ascii: bool) -> None:
    path.write_text(json.dumps(row, ensure_ascii=ensure_ascii, separators=(",", ":")) + "\n", encoding="utf-8")


def valid_payload(*, evidence: str) -> dict[str, object]:
    return {
        "contract_version": "2",
        "frames": [
            {
                "frame_id": "f1",
                "term": "旧記法",
                "intent": "rename",
                "persistence": "durable",
                "polarity": "affirmed",
                "scope": "project",
                "from_term": "旧記法",
                "preferred": "新記法",
                "conflict_group": None,
                "impact": "medium",
                "term_evidence": {"text": "旧記法", "occurrence": 1},
                "intent_evidence": [{"text": evidence, "occurrence": 1}],
                "confidence": "high",
            }
        ],
        "critic": {
            "status": "confirmed",
            "confirmed_frame_ids": ["f1"],
            "rejected_frame_ids": [],
            "unresolved_frame_ids": [],
            "missing_frames": [],
        },
    }


def runtime_row() -> dict[str, object]:
    return {"session_id": "rehearsal-ja-01", "source_text": "文書内の旧記法を新記法に一括置換する。", "registered_terms": []}


def test_ascii_escaped_non_ascii_payload_preserves_exact_evidence(tmp_path: Path) -> None:
    runtime = tmp_path / "runtime.jsonl"
    output = tmp_path / "generated.jsonl"
    write_jsonl(runtime, runtime_row(), ensure_ascii=False)
    write_jsonl(
        output,
        {"session_id": "rehearsal-ja-01", "payload": valid_payload(evidence="旧記法を新記法に一括置換する")},
        ensure_ascii=True,
    )

    result = validator.validate_generated_payloads(runtime_input=runtime, generated_frames=output)

    assert result["status"] == "passed"
    assert result["runtime_row_count"] == 1
    assert result["output_row_count"] == 1
    assert result["validated_frame_count"] == 1
    assert all(byte < 128 for byte in output.read_bytes())


def test_rejects_evidence_mismatch_before_any_evaluation(tmp_path: Path) -> None:
    runtime = tmp_path / "runtime.jsonl"
    output = tmp_path / "generated.jsonl"
    write_jsonl(runtime, runtime_row(), ensure_ascii=False)
    write_jsonl(
        output,
        {"session_id": "rehearsal-ja-01", "payload": valid_payload(evidence="存在しない根拠")},
        ensure_ascii=True,
    )

    with pytest.raises(ValueError, match="does not exist in the exact input text"):
        validator.validate_generated_payloads(runtime_input=runtime, generated_frames=output)


def test_rejects_non_ascii_generated_bytes(tmp_path: Path) -> None:
    runtime = tmp_path / "runtime.jsonl"
    output = tmp_path / "generated.jsonl"
    write_jsonl(runtime, runtime_row(), ensure_ascii=False)
    write_jsonl(
        output,
        {"session_id": "rehearsal-ja-01", "payload": valid_payload(evidence="旧記法を新記法に一括置換する")},
        ensure_ascii=False,
    )

    with pytest.raises(ValueError, match="ASCII-only JSON escapes"):
        validator.validate_generated_payloads(runtime_input=runtime, generated_frames=output)
