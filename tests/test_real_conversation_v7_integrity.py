from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sqlite3
import sys
from types import ModuleType

import pytest


MODULE_PATH = Path(__file__).resolve().parents[1] / "workspace/audit/20260722-real-conversation-ux-v7/holdout_integrity.py"
SPEC = importlib.util.spec_from_file_location("v7_integrity", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
integrity = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(integrity)
EVALUATOR_PATH = MODULE_PATH.with_name("evaluate_real_holdout.py")


def write(path: Path, content: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")
    return path


def write_json(path: Path, value: object) -> Path:
    return write(path, json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def write_reviewed_inputs(reviewed: Path) -> None:
    write(
        reviewed / "corpus.jsonl",
        json.dumps(
            {
                "case_id": "fixture-case-1",
                "session_id": "s1",
                "context": "Define origin seal.",
                "registered_terms": ["present state"],
                "expected_outcome": "observe",
                "reason": "review-only evidence",
            }
        )
        + "\n",
    )
    write(reviewed / "canonical-snapshot.json", "[]\n")


def fixture(tmp_path: Path) -> dict[str, object]:
    root = tmp_path / "project"
    root.mkdir()
    procedure = write(
        root / "docs/procedure.md",
        '<!-- VEIL_BLIND_INPUTS: ["generator_procedure", "semantic_frame_schema", "runtime_input"] -->\n',
    )
    schema = write(root / "shared/schema.py", "SCHEMA = 2\n")
    normalization = write(root / "shared/normalization.py", "NORMALIZE = True\n")
    wrapper = write(root / "audit/evaluator.py", "WRAPPER = True\n")
    core = write(root / "audit/core.py", "CORE = True\n")
    dependency = write(root / "shared/imported_dependency.py", "DEPENDENCY = True\n")
    corpus = write(root / "frozen/frozen-corpus.jsonl", "not valid JSONL labels\n")
    runtime = write(
        root / "frozen/runtime-input.jsonl",
        json.dumps({"session_id": "s1", "source_text": "Define origin seal.", "registered_terms": []}) + "\n",
    )
    snapshot = write(root / "input/canonical-snapshot.json", "[]\n")
    matrix = write(root / "docs/matrix.md", "matrix\n")
    generated = write(root / "frozen/generated-frames.jsonl", json.dumps({"session_id": "s1", "payload": {}}) + "\n")
    manifest_path = root / "frozen/frozen-manifest.json"
    attestation_path = root / "frozen/freeze-attestation.json"
    result_dir = root / "frozen/results/first-run"
    paths = {
        "generator_procedure": procedure,
        "semantic_frame_schema": schema,
        "runtime_input": runtime,
        "reviewed_corpus": corpus,
        "canonical_snapshot": snapshot,
        "approved_evaluation_matrix": matrix,
        "evaluator_wrapper": wrapper,
        "evaluator_core": core,
        "normalization_source": normalization,
    }
    records = {key: integrity.file_record(root, path) for key, path in paths.items()}
    inventory = integrity.inventory_record(root, [
        integrity.relative_path(root, wrapper),
        integrity.relative_path(root, core),
        integrity.relative_path(root, schema),
        integrity.relative_path(root, normalization),
        integrity.relative_path(root, dependency),
    ])
    state = {"head": "fixture", "tracked_diff_sha256": "0" * 64, "execution_source_inventory": inventory}
    args = [
        "--corpus", integrity.relative_path(root, corpus),
        "--runtime-input", integrity.relative_path(root, runtime),
        "--generated-frames", integrity.relative_path(root, generated),
        "--manifest", integrity.relative_path(root, manifest_path),
        "--attestation", integrity.relative_path(root, attestation_path),
        "--result-dir", integrity.relative_path(root, result_dir),
    ]
    manifest = {
        "contract_version": "2",
        "holdout_id": "fixture-v7",
        "status": "frozen",
        "created_at": "2026-07-22T00:00:00+00:00",
        "frozen_at": "2026-07-22T00:00:00+00:00",
        "first_runtime_execution_at": None,
        **records,
        "corpus": records["reviewed_corpus"],
        "evaluator": records["evaluator_wrapper"],
        "protocol": records["generator_procedure"],
        "approved_matrix": records["approved_evaluation_matrix"],
        "evaluator_args": args,
        "host_generation": {"input": records["runtime_input"]["path"], "output": integrity.relative_path(root, generated)},
        "blind_output": {"path": integrity.relative_path(root, generated), "outer_fields": ["payload", "session_id"]},
        "source_state": state,
        "artifact_policy": {"owner": "fixture owner", "deletion_authority": "fixture authority"},
    }
    write_json(manifest_path, manifest)
    attestation = {
        "contract_version": "2",
        "holdout_id": "fixture-v7",
        "attested_at": "2026-07-22T00:00:00+00:00",
        "first_runtime_execution_at": None,
        **records,
        "corpus": records["reviewed_corpus"],
        "evaluator": records["evaluator_wrapper"],
        "protocol": records["generator_procedure"],
        "approved_matrix": records["approved_evaluation_matrix"],
        "manifest": integrity.file_record(root, manifest_path),
        "source_state": state,
        "pre_runtime_confirmation": {
            "review_complete": True,
            "runtime_has_seen_cases": False,
            "generated_frames_exist": False,
            "frozen_inputs_will_not_be_modified": True,
        },
    }
    write_json(attestation_path, attestation)
    return {
        "root": root,
        "paths": paths,
        "manifest": manifest_path,
        "attestation": attestation_path,
        "generated": generated,
        "corpus": corpus,
        "runtime": runtime,
        "result": result_dir,
        "args": args,
        "dependency": dependency,
    }


def run_preflight(state: dict[str, object]) -> dict[str, object]:
    return integrity.validate_preflight(
        project_root=state["root"],
        corpus=state["corpus"],
        runtime_input=state["runtime"],
        generated_frames=state["generated"],
        manifest_path=state["manifest"],
        attestation_path=state["attestation"],
        result_dir=state["result"],
        evaluator_args=state["args"],
        verify_git_state=False,
    )


def load_evaluator() -> ModuleType:
    sys.path.insert(0, str(EVALUATOR_PATH.parent))
    try:
        spec = importlib.util.spec_from_file_location("v7_evaluator_under_test", EVALUATOR_PATH)
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    finally:
        sys.path.pop(0)


def update_record(state: dict[str, object], record_id: str) -> None:
    record = integrity.file_record(state["root"], state["paths"][record_id])
    aliases = {
        "reviewed_corpus": "corpus",
        "evaluator_wrapper": "evaluator",
        "generator_procedure": "protocol",
        "approved_evaluation_matrix": "approved_matrix",
    }
    manifest = integrity.read_json(state["manifest"])
    manifest[record_id] = record
    if record_id in aliases:
        manifest[aliases[record_id]] = record
    write_json(state["manifest"], manifest)
    attestation = integrity.read_json(state["attestation"])
    attestation[record_id] = record
    if record_id in aliases:
        attestation[aliases[record_id]] = record
    attestation["manifest"] = integrity.file_record(state["root"], state["manifest"])
    write_json(state["attestation"], attestation)


def test_preflight_accepts_consistent_fixture_without_parsing_labels(tmp_path: Path) -> None:
    state = fixture(tmp_path)

    result = run_preflight(state)

    assert result["manifest"]["holdout_id"] == "fixture-v7"
    assert not state["result"].exists()


@pytest.mark.parametrize(
    ("document", "mutation"),
    [
        ("manifest", lambda value: value.__setitem__("unexpected", True)),
        ("attestation", lambda value: value.__setitem__("unexpected", True)),
        ("manifest", lambda value: value.pop("created_at")),
        ("attestation", lambda value: value.pop("attested_at")),
        ("manifest", lambda value: value.__setitem__("evaluator_args", "not-a-list")),
        ("manifest", lambda value: value.__setitem__("status", "draft")),
        ("attestation", lambda value: value.__setitem__("pre_runtime_confirmation", {"review_complete": True})),
    ],
)
def test_manifest_and_attestation_schema_rejects_unknown_missing_type_and_content_before_result_directory(
    tmp_path: Path, document: str, mutation: object
) -> None:
    state = fixture(tmp_path)
    value = integrity.read_json(state[document])
    mutation(value)
    write_json(state[document], value)

    with pytest.raises(ValueError):
        run_preflight(state)

    assert not state["result"].exists()


@pytest.mark.parametrize("record_id", integrity.RECORD_IDS)
def test_missing_required_record_fails_before_result_directory(tmp_path: Path, record_id: str) -> None:
    state = fixture(tmp_path)
    attestation = integrity.read_json(state["attestation"])
    del attestation[record_id]
    write_json(state["attestation"], attestation)

    with pytest.raises(ValueError):
        run_preflight(state)

    assert not state["result"].exists()


@pytest.mark.parametrize("record_id", integrity.RECORD_IDS)
def test_changed_frozen_input_fails_before_result_directory(tmp_path: Path, record_id: str) -> None:
    state = fixture(tmp_path)
    path = state["paths"][record_id]
    write(path, path.read_text(encoding="utf-8") + "changed\n")

    with pytest.raises(ValueError, match="mismatch"):
        run_preflight(state)

    assert not state["result"].exists()


def test_attestation_record_mismatch_fails_before_result_directory(tmp_path: Path) -> None:
    state = fixture(tmp_path)
    attestation = integrity.read_json(state["attestation"])
    attestation["evaluator_core"] = {**attestation["evaluator_core"], "bytes": 999}
    write_json(state["attestation"], attestation)

    with pytest.raises(ValueError, match="differ"):
        run_preflight(state)

    assert not state["result"].exists()


def test_unrecorded_generator_read_is_rejected_before_result_directory(tmp_path: Path) -> None:
    state = fixture(tmp_path)
    procedure = state["paths"]["generator_procedure"]
    write(
        procedure,
        '<!-- VEIL_BLIND_INPUTS: ["generator_procedure", "semantic_frame_schema", "runtime_input", "reviewed_corpus"] -->\n',
    )
    record = integrity.file_record(state["root"], procedure)
    for name in ("manifest", "attestation"):
        value = integrity.read_json(state[name])
        value["generator_procedure"] = record
        value["protocol"] = record
        write_json(state[name], value)
    # The attestation's manifest binding must track the intentionally updated manifest.
    attestation = integrity.read_json(state["attestation"])
    attestation["manifest"] = integrity.file_record(state["root"], state["manifest"])
    write_json(state["attestation"], attestation)

    with pytest.raises(ValueError, match="unrecorded or prohibited"):
        run_preflight(state)

    assert not state["result"].exists()


def test_invalid_blind_outer_envelope_fails_before_result_directory(tmp_path: Path) -> None:
    state = fixture(tmp_path)
    write(state["generated"], json.dumps({"session_id": "s1", "payload": {}, "label": "forbidden"}) + "\n")

    with pytest.raises(ValueError, match="outer envelope"):
        run_preflight(state)

    assert not state["result"].exists()


def test_changed_inventory_only_dependency_fails_before_result_directory(tmp_path: Path) -> None:
    state = fixture(tmp_path)
    write(state["dependency"], "DEPENDENCY = CHANGED\n")

    with pytest.raises(ValueError, match="execution_source_inventory mismatch"):
        run_preflight(state)

    assert not state["result"].exists()


def test_changed_exact_arguments_fail_before_result_directory(tmp_path: Path) -> None:
    state = fixture(tmp_path)
    altered_args = [*state["args"]]
    altered_args[-1] = "frozen/results/other"

    with pytest.raises(ValueError, match="arguments differ"):
        integrity.validate_preflight(
            project_root=state["root"],
            corpus=state["corpus"],
            runtime_input=state["runtime"],
            generated_frames=state["generated"],
            manifest_path=state["manifest"],
            attestation_path=state["attestation"],
            result_dir=state["result"],
            evaluator_args=altered_args,
            verify_git_state=False,
        )

    assert not state["result"].exists()


def test_freeze_writes_path_records_to_manifest_and_attestation(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    state = fixture(tmp_path)
    root = state["root"]
    reviewed = root / "reviewed"
    write_reviewed_inputs(reviewed)
    paths = state["paths"]
    inventory = [integrity.relative_path(root, paths["evaluator_wrapper"])]
    monkeypatch.setattr(
        integrity,
        "source_state",
        lambda project_root, inventory_paths: {
            "head": "fixture",
            "tracked_diff_sha256": "0" * 64,
            "execution_source_inventory": integrity.inventory_record(project_root, inventory_paths),
        },
    )

    summary = integrity.freeze_holdout(
        project_root=root,
        reviewed_dir=reviewed,
        frozen_dir=root / "new-frozen",
        holdout_id="fixture-v7-freeze",
        generator_procedure=paths["generator_procedure"],
        evaluation_matrix=paths["approved_evaluation_matrix"],
        evaluator_wrapper=paths["evaluator_wrapper"],
        evaluator_core=paths["evaluator_core"],
        semantic_frame_schema=paths["semantic_frame_schema"],
        normalization_source=paths["normalization_source"],
        inventory_paths=inventory,
    )

    manifest = integrity.read_json(root / "new-frozen/frozen-manifest.json")
    attestation = integrity.read_json(root / "new-frozen/freeze-attestation.json")
    assert summary["manifest"]["path"] == "new-frozen/frozen-manifest.json"
    for record_id in integrity.RECORD_IDS:
        assert set(manifest[record_id]) == {"path", "sha256", "bytes"}
        assert attestation[record_id] == manifest[record_id]
    runtime_rows = integrity.read_jsonl(root / "new-frozen/runtime-input.jsonl")
    assert runtime_rows == [{"session_id": "s1", "source_text": "Define origin seal.", "registered_terms": ["present state"]}]
    assert "expected_outcome" not in (root / "new-frozen/runtime-input.jsonl").read_text(encoding="utf-8")
    verified = integrity.validate_frozen_inputs(
        project_root=root,
        corpus=root / "new-frozen/frozen-corpus.jsonl",
        runtime_input=root / "new-frozen/runtime-input.jsonl",
        generated_frames=root / "new-frozen/generated-frames.jsonl",
        manifest_path=root / "new-frozen/frozen-manifest.json",
        attestation_path=root / "new-frozen/freeze-attestation.json",
        result_dir=root / "new-frozen/results/first-run",
        evaluator_args=manifest["evaluator_args"],
        expect_generated_frames=False,
        verify_git_state=False,
    )
    assert verified["manifest"]["holdout_id"] == "fixture-v7-freeze"


def test_freeze_rejects_prohibited_generator_read_before_creating_directory(tmp_path: Path) -> None:
    state = fixture(tmp_path)
    root = state["root"]
    reviewed = root / "reviewed"
    write_reviewed_inputs(reviewed)
    paths = state["paths"]
    write(
        paths["generator_procedure"],
        '<!-- VEIL_BLIND_INPUTS: ["generator_procedure", "semantic_frame_schema", "runtime_input", "reviewed_corpus"] -->\n',
    )

    with pytest.raises(ValueError, match="unrecorded or prohibited"):
        integrity.freeze_holdout(
            project_root=root,
            reviewed_dir=reviewed,
            frozen_dir=root / "rejected-frozen",
            holdout_id="fixture-v7-freeze",
            generator_procedure=paths["generator_procedure"],
            evaluation_matrix=paths["approved_evaluation_matrix"],
            evaluator_wrapper=paths["evaluator_wrapper"],
            evaluator_core=paths["evaluator_core"],
            semantic_frame_schema=paths["semantic_frame_schema"],
            normalization_source=paths["normalization_source"],
            inventory_paths=[integrity.relative_path(root, paths["evaluator_wrapper"])],
        )

    assert not (root / "rejected-frozen").exists()


@pytest.mark.parametrize("stage", ["after-corpus-copy", "after-record-hash", "after-manifest-write"])
def test_freeze_failure_never_leaves_final_directory_and_writes_external_failure_record(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, stage: str
) -> None:
    state = fixture(tmp_path)
    root = state["root"]
    reviewed = root / "reviewed"
    write_reviewed_inputs(reviewed)
    paths = state["paths"]
    inventory = [integrity.relative_path(root, paths["evaluator_wrapper"])]
    monkeypatch.setattr(
        integrity,
        "source_state",
        lambda project_root, inventory_paths: {
            "head": "fixture",
            "tracked_diff_sha256": "0" * 64,
            "execution_source_inventory": integrity.inventory_record(project_root, inventory_paths),
        },
    )

    def fail_at(actual_stage: str) -> None:
        if actual_stage == stage:
            raise OSError("injected freeze failure")

    with pytest.raises(OSError, match="injected freeze failure"):
        integrity.freeze_holdout(
            project_root=root,
            reviewed_dir=reviewed,
            frozen_dir=root / "atomic-frozen",
            holdout_id="fixture-v7-freeze",
            generator_procedure=paths["generator_procedure"],
            evaluation_matrix=paths["approved_evaluation_matrix"],
            evaluator_wrapper=paths["evaluator_wrapper"],
            evaluator_core=paths["evaluator_core"],
            semantic_frame_schema=paths["semantic_frame_schema"],
            normalization_source=paths["normalization_source"],
            inventory_paths=inventory,
            failure_hook=fail_at,
        )

    assert not (root / "atomic-frozen").exists()
    assert not list(root.glob(".atomic-frozen.staging-*"))
    failure_records = list(root.glob(".atomic-frozen.freeze-failure-*.json"))
    assert len(failure_records) == 1
    assert integrity.read_json(failure_records[0])["stage"] == stage


def test_actual_scored_runtime_uses_measured_zero_access_counters(tmp_path: Path) -> None:
    state = fixture(tmp_path)
    write(
        state["corpus"],
        json.dumps(
            {
                "case_id": "fixture-case-1",
                "session_id": "s1",
                "term": "origin seal",
                "expected_outcome": "exclude",
                "impact": "low",
            }
        ) + "\n",
    )
    update_record(state, "reviewed_corpus")
    payload = {
        "contract_version": "2",
        "frames": [],
        "critic": {
            "status": "confirmed",
            "confirmed_frame_ids": [],
            "rejected_frame_ids": [],
            "unresolved_frame_ids": [],
            "missing_frames": [],
        },
    }
    write(state["generated"], json.dumps({"session_id": "s1", "payload": payload}) + "\n")
    evaluator = load_evaluator()

    exit_code = evaluator.run(
        state["args"],
        project_root=state["root"],
        core_loader=lambda _path: evaluator.load_core(evaluator.CORE),
        verify_git_state=False,
    )

    assert exit_code == 0
    result_manifest = evaluator.read_json(state["result"] / "result-manifest.json")
    summary = evaluator.read_json(state["result"] / "summary.json")
    assert result_manifest["canonical_db_access_attempts"] == 0
    assert result_manifest["raw_text_fallback_attempts"] == 0
    assert result_manifest["semantic_frame_calls"] == 1
    assert summary["gates"]["no_canonical_db_access"] is True
    assert summary["gates"]["zero_raw_text_fallback"] is True


@pytest.mark.parametrize("forbidden_action", ["db", "raw-text"])
def test_forbidden_runtime_access_is_measured_and_recorded_as_runtime_error(
    tmp_path: Path, forbidden_action: str
) -> None:
    state = fixture(tmp_path)
    evaluator = load_evaluator()

    def fake_loader(_path: Path) -> ModuleType:
        module = ModuleType("fake_scoring_core")

        def main() -> int:
            state["result"].mkdir(parents=True)
            write_json(state["result"] / "result-manifest.json", {"status": "runtime-started"})
            if forbidden_action == "db":
                sqlite3.connect(":memory:")
            module.raw_text_fallback()
            return 0

        module.main = main
        return module

    exit_code = evaluator.run(
        state["args"], project_root=state["root"], core_loader=fake_loader, verify_git_state=False
    )

    assert exit_code == 1
    result_manifest = evaluator.read_json(state["result"] / "result-manifest.json")
    assert result_manifest["status"] == "runtime-error"
    assert result_manifest["canonical_db_access_attempts"] == (1 if forbidden_action == "db" else 0)
    assert result_manifest["raw_text_fallback_attempts"] == (1 if forbidden_action == "raw-text" else 0)
