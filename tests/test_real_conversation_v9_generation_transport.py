from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest


MODULE_PATH = Path(__file__).resolve().parents[1] / "workspace/audit/20260722-real-conversation-ux-v9/validate_generated_payloads.py"
SPEC = importlib.util.spec_from_file_location("v9_generated_payloads", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)


SOURCE = "\u7528\u8a9e\uff1d\u4eee\u5206\u985e\u3002"


def payload(evidence: str) -> dict[str, object]:
    return {
        "contract_version": "2",
        "frames": [{"frame_id": "f1", "term": "\u7528\u8a9e", "intent": "define", "persistence": "unclear", "polarity": "affirmed", "scope": "unclear", "from_term": None, "preferred": None, "conflict_group": None, "impact": "low", "term_evidence": {"text": evidence, "occurrence": 1}, "intent_evidence": [{"text": evidence, "occurrence": 1}], "confidence": "medium"}],
        "critic": {"status": "confirmed", "confirmed_frame_ids": ["f1"], "rejected_frame_ids": [], "unresolved_frame_ids": [], "missing_frames": []},
    }


def write_jsonl(path: Path, row: dict[str, object]) -> None:
    path.write_text(json.dumps(row, ensure_ascii=True, separators=(",", ":")) + "\n", encoding="utf-8", newline="\n")


def test_preserves_fullwidth_equals_as_exact_escaped_evidence(tmp_path: Path) -> None:
    runtime, output = tmp_path / "runtime.jsonl", tmp_path / "output.jsonl"
    write_jsonl(runtime, {"session_id": "s1", "source_text": SOURCE, "registered_terms": []})
    write_jsonl(output, {"session_id": "s1", "payload": payload("\u7528\u8a9e\uff1d\u4eee\u5206\u985e")})

    result = validator.validate_generated_payloads(runtime_input=runtime, generated_frames=output)

    assert result["status"] == "passed"
    assert all(byte < 128 for byte in output.read_bytes())


def test_rejects_ascii_equals_substitution(tmp_path: Path) -> None:
    runtime, output = tmp_path / "runtime.jsonl", tmp_path / "output.jsonl"
    write_jsonl(runtime, {"session_id": "s1", "source_text": SOURCE, "registered_terms": []})
    write_jsonl(output, {"session_id": "s1", "payload": payload("\u7528\u8a9e=\u4eee\u5206\u985e")})

    with pytest.raises(ValueError, match="does not exist in the exact input text"):
        validator.validate_generated_payloads(runtime_input=runtime, generated_frames=output)
