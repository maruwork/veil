from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest


MODULE_PATH = Path(__file__).resolve().parents[1] / "workspace/audit/20260722-real-conversation-ux-v8/holdout_integrity.py"
SPEC = importlib.util.spec_from_file_location("v8_integrity", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
integrity = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(integrity)


def write(path: Path, value: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="utf-8", newline="\n")
    return path


def jsonl(value: dict[str, object]) -> str:
    return json.dumps(value, ensure_ascii=True) + "\n"


def fixture(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> dict[str, object]:
    root = tmp_path / "project"
    root.mkdir()
    reviewed = root / "reviewed"
    context = "pier means work, governance means controls"
    rows = [
        {"case_id": "pier", "session_id": "s1", "context": context, "registered_terms": [], "expected_outcome": "observe"},
        {"case_id": "governance", "session_id": "s1", "context": context, "registered_terms": [], "expected_outcome": "observe"},
    ]
    write(reviewed / "corpus.jsonl", "".join(jsonl(row) for row in rows))
    write(reviewed / "canonical-snapshot.json", json.dumps({"contract_version": "2", "read_at": "now", "source": "read-only canonical DB readback", "normalized_active_terms": []}) + "\n")
    procedure = write(root / "docs/procedure.md", '<!-- VEIL_BLIND_INPUTS: ["generator_procedure", "semantic_frame_schema", "runtime_input"] -->\n')
    sources = {
        "generator_procedure": procedure,
        "semantic_frame_schema": write(root / "shared/schema.py", "schema\n"),
        "approved_evaluation_matrix": write(root / "docs/matrix.md", "matrix\n"),
        "evaluator_wrapper": write(root / "audit/wrapper.py", "wrapper\n"),
        "evaluator_core": write(root / "audit/core.py", "core\n"),
        "normalization_source": write(root / "shared/normalization.py", "normalize\n"),
        "payload_validator": write(root / "audit/payload.py", "payload\n"),
    }
    inventory_paths = [integrity.relative_path(root, sources["evaluator_wrapper"])]
    monkeypatch.setattr(integrity, "git_state", lambda project_root, paths: {"head": "fixture", "tracked_diff_sha256": "0" * 64, "execution_source_inventory": integrity.inventory(project_root, paths)})
    return {"root": root, "reviewed": reviewed, "sources": sources, "inventory": inventory_paths, "frozen": root / "frozen"}


def freeze(state: dict[str, object], **kwargs: object) -> dict[str, object]:
    return integrity.freeze_holdout(project_root=state["root"], reviewed_dir=state["reviewed"], frozen_dir=state["frozen"], holdout_id="fixture-v8", sources=state["sources"], inventory_paths=state["inventory"], **kwargs)


def test_freeze_deduplicates_runtime_by_session_and_validates_read_only(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    state = fixture(tmp_path, monkeypatch)

    summary = freeze(state)

    runtime = integrity.read_jsonl(state["frozen"] / "runtime-input.jsonl")
    manifest = integrity.read_json(state["frozen"] / "frozen-manifest.json")
    assert runtime == [{"session_id": "s1", "source_text": "pier means work, governance means controls", "registered_terms": []}]
    assert summary["manifest"]["path"] == "frozen/frozen-manifest.json"
    verified = integrity.validate_frozen_inputs(project_root=state["root"], frozen_dir=state["frozen"], evaluator_args=manifest["evaluator_args"], expect_generated=False, verify_git_state=False)
    assert verified["manifest"]["holdout_id"] == "fixture-v8"
    assert not (state["frozen"] / "generated-frames.jsonl").exists()


@pytest.mark.parametrize("stage", ["after-corpus-copy", "after-snapshot-copy", "after-manifest-write"])
def test_failed_freeze_never_leaves_final_directory(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, stage: str) -> None:
    state = fixture(tmp_path, monkeypatch)

    def fail(actual: str) -> None:
        if actual == stage:
            raise OSError("injected failure")

    with pytest.raises(OSError, match="injected failure"):
        freeze(state, failure_hook=fail)

    assert not state["frozen"].exists()
    assert len(list(state["root"].glob(".frozen.freeze-failure-*.json"))) == 1


def test_freeze_rejects_inconsistent_runtime_rows_before_final_directory(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    state = fixture(tmp_path, monkeypatch)
    corpus = state["reviewed"] / "corpus.jsonl"
    rows = integrity.read_jsonl(corpus)
    rows[1]["context"] = "different context"
    write(corpus, "".join(jsonl(row) for row in rows))

    with pytest.raises(ValueError, match="inconsistent runtime"):
        freeze(state)

    assert not state["frozen"].exists()
