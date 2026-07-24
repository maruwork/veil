"""Shared freeze and preflight checks for the v7 real-conversation holdout.

This module deliberately keeps all validation local and performs no canonical
DB access. ``validate_preflight`` never creates the result directory and never
parses the reviewed corpus; callers must run it before scoring labels.
"""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
from typing import Any, Callable, Iterable
from uuid import uuid4


CONTRACT_VERSION = "2"
RECORD_IDS = (
    "generator_procedure",
    "semantic_frame_schema",
    "runtime_input",
    "reviewed_corpus",
    "canonical_snapshot",
    "approved_evaluation_matrix",
    "evaluator_wrapper",
    "evaluator_core",
    "normalization_source",
)
BLIND_OUTPUT_FIELDS = {"session_id", "payload"}
RUNTIME_FIELDS = {"session_id", "source_text", "registered_terms"}
BLIND_INPUT_IDS = {"generator_procedure", "semantic_frame_schema", "runtime_input"}
BLIND_INPUT_DECLARATION = re.compile(r"^<!-- VEIL_BLIND_INPUTS: (\[[^\n]+\]) -->$", re.MULTILINE)
MANIFEST_FIELDS = frozenset(
    {
        "contract_version", "holdout_id", "status", "created_at", "frozen_at",
        "first_runtime_execution_at", *RECORD_IDS, "corpus", "evaluator", "protocol",
        "approved_matrix", "evaluator_args", "host_generation", "blind_output",
        "source_state", "artifact_policy",
    }
)
ATTESTATION_FIELDS = frozenset(
    {
        "contract_version", "holdout_id", "attested_at", "first_runtime_execution_at",
        *RECORD_IDS, "corpus", "evaluator", "protocol", "approved_matrix", "manifest",
        "source_state", "pre_runtime_confirmation",
    }
)


def reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise ValueError(f"duplicate JSON key: {key}")
        value[key] = item
    return value


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=reject_duplicate_keys)
    if not isinstance(value, dict):
        raise ValueError(f"{path.name} must contain an object")
    return value


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            raise ValueError(f"{path.name}:{number}: blank JSONL line")
        row = json.loads(line, object_pairs_hook=reject_duplicate_keys)
        if not isinstance(row, dict):
            raise ValueError(f"{path.name}:{number}: row must be an object")
        rows.append(row)
    return rows


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def resolve_project_path(project_root: Path, relative: str | Path) -> Path:
    candidate = Path(relative)
    if candidate.is_absolute():
        raise ValueError(f"path must be project-relative: {relative}")
    path = (project_root / candidate).resolve()
    try:
        path.relative_to(project_root.resolve())
    except ValueError as exc:
        raise ValueError(f"path is outside project root: {relative}") from exc
    return path


def relative_path(project_root: Path, path: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(project_root.resolve()).as_posix()
    except ValueError as exc:
        raise ValueError(f"path is outside project root: {path}") from exc


def file_record(project_root: Path, path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise ValueError(f"required file is missing: {path}")
    data = path.read_bytes()
    return {"path": relative_path(project_root, path), "sha256": sha256_bytes(data), "bytes": len(data)}


def file_record_as(project_root: Path, path: Path, declared_path: Path) -> dict[str, Any]:
    """Hash ``path`` while binding it to its eventual project-relative name."""
    if not path.is_file():
        raise ValueError(f"required file is missing: {path}")
    data = path.read_bytes()
    return {"path": relative_path(project_root, declared_path), "sha256": sha256_bytes(data), "bytes": len(data)}


def _validate_record(project_root: Path, record: Any, *, label: str) -> dict[str, Any]:
    if not isinstance(record, dict) or set(record) != {"path", "sha256", "bytes"}:
        raise ValueError(f"{label} must be a path/sha256/bytes record")
    path_value = record["path"]
    if not isinstance(path_value, str) or not path_value:
        raise ValueError(f"{label}.path is invalid")
    if not isinstance(record["sha256"], str) or len(record["sha256"]) != 64:
        raise ValueError(f"{label}.sha256 is invalid")
    if not isinstance(record["bytes"], int) or record["bytes"] < 0:
        raise ValueError(f"{label}.bytes is invalid")
    path = resolve_project_path(project_root, path_value)
    actual = file_record(project_root, path)
    if actual != record:
        raise ValueError(f"{label} path, sha256, or bytes mismatch")
    return actual


def inventory_record(project_root: Path, relative_paths: Iterable[str]) -> dict[str, Any]:
    records: list[dict[str, Any]] = []
    seen: set[str] = set()
    hasher = hashlib.sha256()
    total_bytes = 0
    for raw in relative_paths:
        path = resolve_project_path(project_root, raw)
        record = file_record(project_root, path)
        normalized = record["path"]
        if normalized in seen:
            raise ValueError(f"duplicate inventory path: {normalized}")
        seen.add(normalized)
        records.append(record)
        data = path.read_bytes()
        hasher.update(normalized.encode("utf-8"))
        hasher.update(b"\0")
        hasher.update(len(data).to_bytes(8, "big"))
        hasher.update(data)
        total_bytes += len(data)
    if not records:
        raise ValueError("execution source inventory must not be empty")
    return {"sha256": hasher.hexdigest(), "bytes": total_bytes, "records": records}


def _validate_inventory(project_root: Path, value: Any) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != {"sha256", "bytes", "records"}:
        raise ValueError("execution_source_inventory is invalid")
    records = value["records"]
    if not isinstance(records, list) or not records:
        raise ValueError("execution_source_inventory.records is invalid")
    expected_paths: list[str] = []
    for index, record in enumerate(records, start=1):
        if not isinstance(record, dict) or set(record) != {"path", "sha256", "bytes"}:
            raise ValueError(f"execution_source_inventory record {index} is invalid")
        expected_paths.append(str(record["path"]))
    actual = inventory_record(project_root, expected_paths)
    if actual != value:
        raise ValueError("execution_source_inventory mismatch")
    return actual


def _git_output(project_root: Path, *args: str) -> bytes:
    return subprocess.run(["git", *args], cwd=project_root, check=True, capture_output=True).stdout


def source_state(project_root: Path, inventory_paths: Iterable[str]) -> dict[str, Any]:
    return {
        "head": _git_output(project_root, "rev-parse", "HEAD").decode("ascii").strip(),
        "tracked_diff_sha256": sha256_bytes(
            _git_output(project_root, "diff", "--binary", "--no-ext-diff", "HEAD", "--", ".")
        ),
        "execution_source_inventory": inventory_record(project_root, inventory_paths),
    }


def _validate_source_state(project_root: Path, value: Any, *, verify_git_state: bool) -> None:
    if not isinstance(value, dict) or set(value) != {"head", "tracked_diff_sha256", "execution_source_inventory"}:
        raise ValueError("source_state is invalid")
    inventory = _validate_inventory(project_root, value["execution_source_inventory"])
    if verify_git_state:
        actual = source_state(project_root, [record["path"] for record in inventory["records"]])
        if actual != value:
            raise ValueError("source_state changed after freeze")


def _same_record(manifest: dict[str, Any], attestation: dict[str, Any], record_id: str) -> None:
    if manifest.get(record_id) != attestation.get(record_id):
        raise ValueError(f"manifest and attestation differ for {record_id}")


def _require_exact_fields(value: Any, fields: frozenset[str], *, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be an object")
    actual = set(value)
    if actual != fields:
        missing = sorted(fields - actual)
        unknown = sorted(actual - fields)
        raise ValueError(f"{label} field set is invalid: missing={missing}, unknown={unknown}")
    return value


def _require_nonempty_string(value: Any, *, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be a non-empty string")
    return value


def _require_timestamp(value: Any, *, label: str) -> None:
    text = _require_nonempty_string(value, label=label)
    try:
        datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"{label} must be an ISO-8601 timestamp") from exc


def _validate_metadata_shape(manifest: Any, attestation: Any) -> tuple[dict[str, Any], dict[str, Any]]:
    manifest_value = _require_exact_fields(manifest, MANIFEST_FIELDS, label="manifest")
    attestation_value = _require_exact_fields(attestation, ATTESTATION_FIELDS, label="attestation")
    if manifest_value["contract_version"] != CONTRACT_VERSION or attestation_value["contract_version"] != CONTRACT_VERSION:
        raise ValueError("manifest and attestation must use contract version 2")
    if manifest_value["status"] != "frozen":
        raise ValueError("manifest status must be frozen")
    if manifest_value["first_runtime_execution_at"] is not None or attestation_value["first_runtime_execution_at"] is not None:
        raise ValueError("first_runtime_execution_at must remain null")
    if _require_nonempty_string(manifest_value["holdout_id"], label="manifest.holdout_id") != _require_nonempty_string(
        attestation_value["holdout_id"], label="attestation.holdout_id"
    ):
        raise ValueError("manifest and attestation holdout IDs differ")
    _require_timestamp(manifest_value["created_at"], label="manifest.created_at")
    _require_timestamp(manifest_value["frozen_at"], label="manifest.frozen_at")
    _require_timestamp(attestation_value["attested_at"], label="attestation.attested_at")
    if not isinstance(manifest_value["evaluator_args"], list) or any(not isinstance(item, str) for item in manifest_value["evaluator_args"]):
        raise ValueError("manifest.evaluator_args must be a string list")
    blind_output = manifest_value["blind_output"]
    if not isinstance(blind_output, dict) or set(blind_output) != {"path", "outer_fields"}:
        raise ValueError("blind_output is invalid")
    if not isinstance(blind_output["path"], str) or blind_output["outer_fields"] != sorted(BLIND_OUTPUT_FIELDS):
        raise ValueError("blind_output values are invalid")
    host_generation = manifest_value["host_generation"]
    if not isinstance(host_generation, dict) or set(host_generation) != {"input", "output"}:
        raise ValueError("host_generation is invalid")
    if host_generation.get("input") != manifest_value["runtime_input"]["path"] or host_generation.get("output") != blind_output["path"]:
        raise ValueError("host_generation paths are inconsistent")
    artifact_policy = manifest_value["artifact_policy"]
    if not isinstance(artifact_policy, dict) or set(artifact_policy) != {"owner", "deletion_authority"}:
        raise ValueError("artifact_policy is invalid")
    _require_nonempty_string(artifact_policy["owner"], label="artifact_policy.owner")
    _require_nonempty_string(artifact_policy["deletion_authority"], label="artifact_policy.deletion_authority")
    confirmation = attestation_value["pre_runtime_confirmation"]
    expected_confirmation = {
        "review_complete": True,
        "runtime_has_seen_cases": False,
        "generated_frames_exist": False,
        "frozen_inputs_will_not_be_modified": True,
    }
    if confirmation != expected_confirmation:
        raise ValueError("pre_runtime_confirmation is invalid")
    aliases = {
        "corpus": "reviewed_corpus",
        "evaluator": "evaluator_wrapper",
        "protocol": "generator_procedure",
        "approved_matrix": "approved_evaluation_matrix",
    }
    for alias, record_id in aliases.items():
        if manifest_value[alias] != manifest_value[record_id] or attestation_value[alias] != attestation_value[record_id]:
            raise ValueError(f"legacy alias {alias} is inconsistent with {record_id}")
    return manifest_value, attestation_value


def _validate_runtime_and_output(runtime_path: Path, output_path: Path) -> None:
    runtime_rows = read_jsonl(runtime_path)
    output_rows = read_jsonl(output_path)
    runtime_sessions: set[str] = set()
    for number, row in enumerate(runtime_rows, start=1):
        if set(row) != RUNTIME_FIELDS:
            raise ValueError(f"runtime row {number} has an invalid field set")
        session_id = row.get("session_id")
        if not isinstance(session_id, str) or not session_id or session_id in runtime_sessions:
            raise ValueError(f"runtime row {number} has an invalid session_id")
        if not isinstance(row.get("source_text"), str) or not isinstance(row.get("registered_terms"), list):
            raise ValueError(f"runtime row {number} is invalid")
        runtime_sessions.add(session_id)
    output_sessions: set[str] = set()
    for number, row in enumerate(output_rows, start=1):
        if set(row) != BLIND_OUTPUT_FIELDS or not isinstance(row.get("session_id"), str) or not isinstance(row.get("payload"), dict):
            raise ValueError(f"blind output row {number} has an invalid outer envelope")
        if row["session_id"] in output_sessions:
            raise ValueError(f"blind output row {number} has a duplicate session_id")
        output_sessions.add(row["session_id"])
    if output_sessions != runtime_sessions:
        raise ValueError("blind output session IDs do not exactly match runtime input")


def validate_generator_procedure(path: Path) -> None:
    """Require a machine-checkable declaration of the generator's only reads."""
    matches = BLIND_INPUT_DECLARATION.findall(path.read_text(encoding="utf-8"))
    if len(matches) != 1:
        raise ValueError("generator procedure must declare VEIL_BLIND_INPUTS exactly once")
    try:
        declared = json.loads(matches[0], object_pairs_hook=reject_duplicate_keys)
    except json.JSONDecodeError as exc:
        raise ValueError("generator procedure has invalid VEIL_BLIND_INPUTS JSON") from exc
    if not isinstance(declared, list) or any(not isinstance(value, str) for value in declared):
        raise ValueError("generator procedure blind input declaration must be a string list")
    if set(declared) != BLIND_INPUT_IDS or len(declared) != len(BLIND_INPUT_IDS):
        raise ValueError("generator procedure declares an unrecorded or prohibited blind input")


def runtime_input_from_reviewed_corpus(corpus_path: Path) -> list[dict[str, Any]]:
    """Derive the label-free blind input that the freeze tool owns.

    The reviewed corpus is allowed to contain expected outcomes and review
    evidence.  The runtime input deliberately copies only the session ID,
    exact context, and already-read canonical terms, so the generator cannot
    receive labels or reviewer reasoning through this boundary.
    """
    runtime_rows: list[dict[str, Any]] = []
    session_ids: set[str] = set()
    for number, row in enumerate(read_jsonl(corpus_path), start=1):
        session_id = row.get("session_id")
        context = row.get("context")
        registered_terms = row.get("registered_terms")
        if not isinstance(session_id, str) or not session_id or session_id in session_ids:
            raise ValueError(f"reviewed corpus row {number} has an invalid session_id")
        if not isinstance(context, str) or not context:
            raise ValueError(f"reviewed corpus row {number} has an invalid context")
        if not isinstance(registered_terms, list) or any(not isinstance(term, str) for term in registered_terms):
            raise ValueError(f"reviewed corpus row {number} has invalid registered_terms")
        session_ids.add(session_id)
        runtime_rows.append(
            {
                "session_id": session_id,
                "source_text": context,
                "registered_terms": registered_terms,
            }
        )
    if not runtime_rows:
        raise ValueError("reviewed corpus must contain at least one row")
    return runtime_rows


def validate_frozen_inputs(
    *,
    project_root: Path,
    corpus: Path,
    runtime_input: Path,
    generated_frames: Path,
    manifest_path: Path,
    attestation_path: Path,
    result_dir: Path,
    evaluator_args: list[str],
    expect_generated_frames: bool,
    verify_git_state: bool = True,
) -> dict[str, Any]:
    """Verify the frozen package without creating files or parsing labels.

    G6 calls this before blind generation and therefore requires the reserved
    output to be absent.  G8 calls it through ``validate_preflight`` after G7,
    requiring that same output to exist before its envelope is inspected.
    """
    root = project_root.resolve()
    supplied = {
        "reviewed_corpus": resolve_project_path(root, relative_path(root, corpus)),
        "runtime_input": resolve_project_path(root, relative_path(root, runtime_input)),
        "manifest": resolve_project_path(root, relative_path(root, manifest_path)),
        "attestation": resolve_project_path(root, relative_path(root, attestation_path)),
        "generated_frames": resolve_project_path(root, relative_path(root, generated_frames)),
        "result_dir": resolve_project_path(root, relative_path(root, result_dir)),
    }
    if supplied["result_dir"].exists():
        raise ValueError(f"result directory already exists: {supplied['result_dir']}")
    if supplied["generated_frames"].exists() != expect_generated_frames:
        state = "exist" if expect_generated_frames else "not exist"
        raise ValueError(f"reserved blind output must {state}: {supplied['generated_frames']}")
    manifest, attestation = _validate_metadata_shape(
        read_json(supplied["manifest"]), read_json(supplied["attestation"])
    )
    if manifest["evaluator_args"] != evaluator_args:
        raise ValueError("evaluator arguments differ from frozen exact command")
    seen_paths: set[str] = set()
    for record_id in RECORD_IDS:
        _same_record(manifest, attestation, record_id)
        actual = _validate_record(root, manifest.get(record_id), label=record_id)
        if actual["path"] in seen_paths:
            raise ValueError(f"duplicate frozen record path: {actual['path']}")
        seen_paths.add(actual["path"])
    validate_generator_procedure(resolve_project_path(root, manifest["generator_procedure"]["path"]))
    if manifest["reviewed_corpus"]["path"] != relative_path(root, supplied["reviewed_corpus"]):
        raise ValueError("reviewed corpus differs from evaluator command")
    if manifest["runtime_input"]["path"] != relative_path(root, supplied["runtime_input"]):
        raise ValueError("runtime input differs from evaluator command")
    manifest_record = attestation["manifest"]
    if _validate_record(root, manifest_record, label="attested manifest") != file_record(root, supplied["manifest"]):
        raise ValueError("attested manifest differs from evaluator command")
    if manifest["source_state"] != attestation["source_state"]:
        raise ValueError("manifest and attestation source_state differ")
    _validate_source_state(root, manifest["source_state"], verify_git_state=verify_git_state)
    blind_output = manifest["blind_output"]
    if blind_output["path"] != relative_path(root, supplied["generated_frames"]):
        raise ValueError("blind output differs from evaluator command")
    if blind_output["outer_fields"] != sorted(BLIND_OUTPUT_FIELDS):
        raise ValueError("blind output outer field contract is invalid")
    return {"manifest": manifest, "attestation": attestation}


def validate_preflight(
    *,
    project_root: Path,
    corpus: Path,
    runtime_input: Path,
    generated_frames: Path,
    manifest_path: Path,
    attestation_path: Path,
    result_dir: Path,
    evaluator_args: list[str],
    verify_git_state: bool = True,
) -> dict[str, Any]:
    """Verify frozen inputs and the blind output before labels are parsed."""
    verified = validate_frozen_inputs(
        project_root=project_root,
        corpus=corpus,
        runtime_input=runtime_input,
        generated_frames=generated_frames,
        manifest_path=manifest_path,
        attestation_path=attestation_path,
        result_dir=result_dir,
        evaluator_args=evaluator_args,
        expect_generated_frames=True,
        verify_git_state=verify_git_state,
    )
    root = project_root.resolve()
    supplied_runtime = resolve_project_path(root, relative_path(root, runtime_input))
    supplied_output = resolve_project_path(root, relative_path(root, generated_frames))
    _validate_runtime_and_output(supplied_runtime, supplied_output)
    return verified


def freeze_holdout(
    *,
    project_root: Path,
    reviewed_dir: Path,
    frozen_dir: Path,
    holdout_id: str,
    generator_procedure: Path,
    evaluation_matrix: Path,
    evaluator_wrapper: Path,
    evaluator_core: Path,
    semantic_frame_schema: Path,
    normalization_source: Path,
    inventory_paths: Iterable[str],
    failure_hook: Callable[[str], None] | None = None,
) -> dict[str, Any]:
    """Atomically create the v7 immutable package; never runs evaluation.

    All output is built and checked below a uniquely named sibling staging
    directory.  The reserved final directory appears only after one rename.
    A failed attempt leaves a diagnostic record beside, never inside, that
    final directory so it cannot be mistaken for a valid frozen holdout.
    """
    root = project_root.resolve()
    frozen = resolve_project_path(root, relative_path(root, frozen_dir))
    if frozen.exists():
        raise ValueError(f"frozen directory already exists: {frozen}")
    reviewed = resolve_project_path(root, relative_path(root, reviewed_dir))
    sources = {
        "reviewed_corpus": reviewed / "corpus.jsonl",
        "canonical_snapshot": reviewed / "canonical-snapshot.json",
        "generator_procedure": generator_procedure,
        "approved_evaluation_matrix": evaluation_matrix,
        "evaluator_wrapper": evaluator_wrapper,
        "evaluator_core": evaluator_core,
        "semantic_frame_schema": semantic_frame_schema,
        "normalization_source": normalization_source,
    }
    for path in sources.values():
        if not path.is_file():
            raise ValueError(f"required freeze input is missing: {path}")
    validate_generator_procedure(sources["generator_procedure"])
    staging = frozen.with_name(f".{frozen.name}.staging-{uuid4().hex}")
    failure_record = frozen.with_name(f".{frozen.name}.freeze-failure-{uuid4().hex}.json")
    stage_name = "before-staging"

    def checkpoint(name: str) -> None:
        nonlocal stage_name
        stage_name = name
        if failure_hook is not None:
            failure_hook(name)

    def write_json(path: Path, value: dict[str, Any]) -> None:
        path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    try:
        checkpoint("before-staging")
        staging.mkdir(parents=False)
        checkpoint("after-staging")
        staged_corpus = staging / "frozen-corpus.jsonl"
        staged_runtime = staging / "runtime-input.jsonl"
        frozen_corpus = frozen / staged_corpus.name
        frozen_runtime = frozen / staged_runtime.name
        shutil.copyfile(sources["reviewed_corpus"], staged_corpus)
        checkpoint("after-corpus-copy")
        runtime_rows = runtime_input_from_reviewed_corpus(sources["reviewed_corpus"])
        staged_runtime.write_text(
            "".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n" for row in runtime_rows),
            encoding="utf-8",
        )
        checkpoint("after-runtime-derive")
        records = {
            **{key: file_record(root, value) for key, value in sources.items() if key != "reviewed_corpus"},
            "reviewed_corpus": file_record_as(root, staged_corpus, frozen_corpus),
            "runtime_input": file_record_as(root, staged_runtime, frozen_runtime),
        }
        checkpoint("after-record-hash")
        inventory = list(inventory_paths)
        state = source_state(root, inventory)
        now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
        manifest_path = frozen / "frozen-manifest.json"
        attestation_path = frozen / "freeze-attestation.json"
        staged_manifest = staging / manifest_path.name
        staged_attestation = staging / attestation_path.name
        generated = frozen / "generated-frames.jsonl"
        result_dir = frozen / "results/first-run"
        evaluator_args = [
            "--corpus", relative_path(root, frozen_corpus),
            "--runtime-input", relative_path(root, frozen_runtime),
            "--generated-frames", relative_path(root, generated),
            "--manifest", relative_path(root, manifest_path),
            "--attestation", relative_path(root, attestation_path),
            "--result-dir", relative_path(root, result_dir),
        ]
        manifest = {
            "contract_version": CONTRACT_VERSION,
            "holdout_id": holdout_id,
            "status": "frozen",
            "created_at": now,
            "frozen_at": now,
            "first_runtime_execution_at": None,
            **records,
            "corpus": records["reviewed_corpus"],
            "evaluator": records["evaluator_wrapper"],
            "protocol": records["generator_procedure"],
            "approved_matrix": records["approved_evaluation_matrix"],
            "evaluator_args": evaluator_args,
            "host_generation": {"input": records["runtime_input"]["path"], "output": relative_path(root, generated)},
            "blind_output": {"path": relative_path(root, generated), "outer_fields": sorted(BLIND_OUTPUT_FIELDS)},
            "source_state": state,
            "artifact_policy": {"owner": "VEIL evaluation owner", "deletion_authority": "repository owner only"},
        }
        write_json(staged_manifest, manifest)
        checkpoint("after-manifest-write")
        attestation = {
            "contract_version": CONTRACT_VERSION,
            "holdout_id": holdout_id,
            "attested_at": now,
            "first_runtime_execution_at": None,
            **records,
            "corpus": records["reviewed_corpus"],
            "evaluator": records["evaluator_wrapper"],
            "protocol": records["generator_procedure"],
            "approved_matrix": records["approved_evaluation_matrix"],
            "manifest": file_record_as(root, staged_manifest, manifest_path),
            "source_state": state,
            "pre_runtime_confirmation": {
                "review_complete": True,
                "runtime_has_seen_cases": False,
                "generated_frames_exist": False,
                "frozen_inputs_will_not_be_modified": True,
            },
        }
        write_json(staged_attestation, attestation)
        checkpoint("after-attestation-write")
        staged_manifest_value, staged_attestation_value = _validate_metadata_shape(
            read_json(staged_manifest), read_json(staged_attestation)
        )
        for record_id in RECORD_IDS:
            _same_record(staged_manifest_value, staged_attestation_value, record_id)
            declared = resolve_project_path(root, staged_manifest_value[record_id]["path"])
            actual_path = staging / declared.relative_to(frozen) if declared.is_relative_to(frozen) else declared
            if file_record_as(root, actual_path, declared) != staged_manifest_value[record_id]:
                raise ValueError(f"staged {record_id} path, sha256, or bytes mismatch")
        if file_record_as(root, staged_manifest, manifest_path) != staged_attestation_value["manifest"]:
            raise ValueError("staged attested manifest is invalid")
        _validate_source_state(root, staged_manifest_value["source_state"], verify_git_state=True)
        checkpoint("before-rename")
        if frozen.exists():
            raise ValueError(f"frozen directory already exists: {frozen}")
        staging.replace(frozen)
        checkpoint("after-rename")
        return {
            "manifest": file_record(root, manifest_path),
            "attestation": file_record(root, attestation_path),
        }
    except Exception as exc:
        if staging.exists():
            shutil.rmtree(staging)
        if not frozen.exists():
            failure_record.write_text(
                json.dumps(
                    {
                        "status": "freeze-failed",
                        "stage": stage_name,
                        "error_type": type(exc).__name__,
                        "error": str(exc),
                    },
                    ensure_ascii=False,
                    indent=2,
                ) + "\n",
                encoding="utf-8",
            )
        raise
