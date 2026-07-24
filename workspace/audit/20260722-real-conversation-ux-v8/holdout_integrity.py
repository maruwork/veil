"""V8-only atomic freeze and read-only frozen-input verification."""

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
    "generator_procedure", "semantic_frame_schema", "runtime_input", "reviewed_corpus",
    "canonical_snapshot", "approved_evaluation_matrix", "evaluator_wrapper", "evaluator_core",
    "normalization_source", "payload_validator",
)
MANIFEST_FIELDS = frozenset({
    "contract_version", "holdout_id", "status", "created_at", "frozen_at", "first_runtime_execution_at",
    *RECORD_IDS, "corpus", "evaluator", "protocol", "approved_matrix", "evaluator_args",
    "host_generation", "blind_output", "source_state", "artifact_policy",
})
ATTESTATION_FIELDS = frozenset({
    "contract_version", "holdout_id", "attested_at", "first_runtime_execution_at", *RECORD_IDS,
    "corpus", "evaluator", "protocol", "approved_matrix", "manifest", "source_state",
    "pre_runtime_confirmation",
})
RUNTIME_FIELDS = frozenset({"session_id", "source_text", "registered_terms"})
BLIND_INPUTS = {"generator_procedure", "semantic_frame_schema", "runtime_input"}
BLIND_INPUT_DECLARATION = re.compile(r"^<!-- VEIL_BLIND_INPUTS: (\[[^\n]+\]) -->$", re.MULTILINE)


def reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


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
        value = json.loads(line, object_pairs_hook=reject_duplicate_keys)
        if not isinstance(value, dict):
            raise ValueError(f"{path.name}:{number}: row must be an object")
        rows.append(value)
    return rows


def project_path(root: Path, path: Path | str) -> Path:
    candidate = Path(path)
    if candidate.is_absolute():
        raise ValueError(f"path must be project-relative: {path}")
    resolved = (root / candidate).resolve()
    try:
        resolved.relative_to(root.resolve())
    except ValueError as exc:
        raise ValueError(f"path is outside project root: {path}") from exc
    return resolved


def relative_path(root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError as exc:
        raise ValueError(f"path is outside project root: {path}") from exc


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def record(root: Path, path: Path, *, declared_path: Path | None = None) -> dict[str, Any]:
    if not path.is_file():
        raise ValueError(f"required file is missing: {path}")
    data = path.read_bytes()
    return {"path": relative_path(root, declared_path or path), "sha256": sha256_bytes(data), "bytes": len(data)}


def inventory(root: Path, paths: Iterable[str]) -> dict[str, Any]:
    records: list[dict[str, Any]] = []
    seen: set[str] = set()
    digest = hashlib.sha256()
    total = 0
    for raw in paths:
        item = record(root, project_path(root, raw))
        if item["path"] in seen:
            raise ValueError(f"duplicate inventory path: {item['path']}")
        seen.add(item["path"])
        records.append(item)
        data = project_path(root, item["path"]).read_bytes()
        digest.update(item["path"].encode("utf-8")); digest.update(b"\0")
        digest.update(len(data).to_bytes(8, "big")); digest.update(data)
        total += len(data)
    if not records:
        raise ValueError("execution source inventory must not be empty")
    return {"sha256": digest.hexdigest(), "bytes": total, "records": records}


def git_state(root: Path, inventory_paths: Iterable[str]) -> dict[str, Any]:
    def output(*args: str) -> bytes:
        return subprocess.run(["git", *args], cwd=root, check=True, capture_output=True).stdout
    return {
        "head": output("rev-parse", "HEAD").decode("ascii").strip(),
        "tracked_diff_sha256": sha256_bytes(output("diff", "--binary", "--no-ext-diff", "HEAD", "--", ".")),
        "execution_source_inventory": inventory(root, inventory_paths),
    }


def validate_procedure(path: Path) -> None:
    matches = BLIND_INPUT_DECLARATION.findall(path.read_text(encoding="utf-8"))
    if len(matches) != 1:
        raise ValueError("generator procedure must declare VEIL_BLIND_INPUTS exactly once")
    values = json.loads(matches[0], object_pairs_hook=reject_duplicate_keys)
    if not isinstance(values, list) or set(values) != BLIND_INPUTS or len(values) != len(BLIND_INPUTS):
        raise ValueError("generator procedure declares an unrecorded or prohibited blind input")


def runtime_from_corpus(corpus: Path) -> list[dict[str, Any]]:
    """Create one label-free row per session, even with several reviewed targets."""
    rows_by_session: dict[str, dict[str, Any]] = {}
    for number, row in enumerate(read_jsonl(corpus), start=1):
        session_id, context, registered = row.get("session_id"), row.get("context"), row.get("registered_terms")
        if not isinstance(session_id, str) or not session_id or not isinstance(context, str) or not context:
            raise ValueError(f"reviewed corpus row {number} has invalid session/context")
        if not isinstance(registered, list) or any(not isinstance(term, str) for term in registered):
            raise ValueError(f"reviewed corpus row {number} has invalid registered_terms")
        value = {"session_id": session_id, "source_text": context, "registered_terms": registered}
        prior = rows_by_session.setdefault(session_id, value)
        if prior != value:
            raise ValueError(f"reviewed corpus session {session_id} has inconsistent runtime inputs")
    if not rows_by_session:
        raise ValueError("reviewed corpus must contain at least one row")
    return list(rows_by_session.values())


def _require_fields(value: Any, fields: frozenset[str], label: str) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != fields:
        raise ValueError(f"{label} field set is invalid")
    return value


def _validate_metadata(manifest: Any, attestation: Any) -> tuple[dict[str, Any], dict[str, Any]]:
    m = _require_fields(manifest, MANIFEST_FIELDS, "manifest")
    a = _require_fields(attestation, ATTESTATION_FIELDS, "attestation")
    if m["contract_version"] != CONTRACT_VERSION or a["contract_version"] != CONTRACT_VERSION or m["status"] != "frozen":
        raise ValueError("contract version or frozen status is invalid")
    if m["holdout_id"] != a["holdout_id"] or not isinstance(m["holdout_id"], str) or not m["holdout_id"]:
        raise ValueError("holdout identity is invalid")
    if m["first_runtime_execution_at"] is not None or a["first_runtime_execution_at"] is not None:
        raise ValueError("first runtime execution must remain null")
    for name in ("created_at", "frozen_at"):
        if not isinstance(m[name], str) or not m[name]: raise ValueError(f"manifest {name} is invalid")
    if not isinstance(a["attested_at"], str) or not a["attested_at"]: raise ValueError("attestation timestamp is invalid")
    aliases = {"corpus": "reviewed_corpus", "evaluator": "evaluator_wrapper", "protocol": "generator_procedure", "approved_matrix": "approved_evaluation_matrix"}
    for alias, item in aliases.items():
        if m[alias] != m[item] or a[alias] != a[item]: raise ValueError(f"{alias} alias is inconsistent")
    if a["pre_runtime_confirmation"] != {"review_complete": True, "runtime_has_seen_cases": False, "generated_frames_exist": False, "frozen_inputs_will_not_be_modified": True}:
        raise ValueError("pre-runtime confirmation is invalid")
    if not isinstance(m["evaluator_args"], list) or any(not isinstance(v, str) for v in m["evaluator_args"]):
        raise ValueError("evaluator arguments are invalid")
    if not isinstance(m["blind_output"], dict) or set(m["blind_output"]) != {"path", "outer_fields"} or m["blind_output"]["outer_fields"] != ["payload", "session_id"]:
        raise ValueError("blind output declaration is invalid")
    return m, a


def _check_record(root: Path, value: Any, label: str, actual_path: Path | None = None) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != {"path", "sha256", "bytes"}:
        raise ValueError(f"{label} record is invalid")
    path = actual_path or project_path(root, value["path"])
    if record(root, path, declared_path=project_path(root, value["path"])) != value:
        raise ValueError(f"{label} path, hash, or byte count mismatch")
    return value


def _check_state(root: Path, state: Any, *, verify_git_state: bool) -> None:
    if not isinstance(state, dict) or set(state) != {"head", "tracked_diff_sha256", "execution_source_inventory"}:
        raise ValueError("source state is invalid")
    inv = state["execution_source_inventory"]
    if not isinstance(inv, dict) or set(inv) != {"sha256", "bytes", "records"} or not isinstance(inv["records"], list):
        raise ValueError("source inventory is invalid")
    paths = [item["path"] for item in inv["records"] if isinstance(item, dict) and isinstance(item.get("path"), str)]
    if len(paths) != len(inv["records"]) or inventory(root, paths) != inv:
        raise ValueError("execution source inventory mismatch")
    if verify_git_state and git_state(root, paths) != state:
        raise ValueError("source state changed after freeze")


def validate_frozen_inputs(*, project_root: Path, frozen_dir: Path, evaluator_args: list[str], expect_generated: bool, verify_git_state: bool = True) -> dict[str, Any]:
    root, frozen = project_root.resolve(), project_path(project_root.resolve(), relative_path(project_root.resolve(), frozen_dir))
    manifest_path, attestation_path = frozen / "frozen-manifest.json", frozen / "freeze-attestation.json"
    generated, result_dir = frozen / "generated-frames.jsonl", frozen / "results/first-run"
    if result_dir.exists(): raise ValueError("first-run result already exists")
    if generated.exists() != expect_generated: raise ValueError("reserved generated output has an invalid existence state")
    m, a = _validate_metadata(read_json(manifest_path), read_json(attestation_path))
    if m["evaluator_args"] != evaluator_args: raise ValueError("evaluator arguments differ from frozen command")
    for item in RECORD_IDS:
        if m[item] != a[item]: raise ValueError(f"manifest and attestation differ for {item}")
        _check_record(root, m[item], item)
    _check_record(root, a["manifest"], "attested manifest")
    if m["source_state"] != a["source_state"]: raise ValueError("manifest and attestation source state differ")
    _check_state(root, m["source_state"], verify_git_state=verify_git_state)
    validate_procedure(project_path(root, m["generator_procedure"]["path"]))
    if m["blind_output"]["path"] != relative_path(root, generated): raise ValueError("blind output path differs")
    return {"manifest": m, "attestation": a}


def freeze_holdout(*, project_root: Path, reviewed_dir: Path, frozen_dir: Path, holdout_id: str, sources: dict[str, Path], inventory_paths: Iterable[str], failure_hook: Callable[[str], None] | None = None) -> dict[str, Any]:
    root = project_root.resolve(); frozen = project_path(root, relative_path(root, frozen_dir)); reviewed = project_path(root, relative_path(root, reviewed_dir))
    if frozen.exists(): raise ValueError(f"frozen directory already exists: {frozen}")
    required = {"generator_procedure", "semantic_frame_schema", "approved_evaluation_matrix", "evaluator_wrapper", "evaluator_core", "normalization_source", "payload_validator"}
    if set(sources) != required: raise ValueError("v8 freeze source set is invalid")
    for path in [reviewed / "corpus.jsonl", reviewed / "canonical-snapshot.json", *sources.values()]:
        if not path.is_file(): raise ValueError(f"required freeze input is missing: {path}")
    validate_procedure(sources["generator_procedure"])
    staging = frozen.with_name(f".{frozen.name}.staging-{uuid4().hex}")
    failure = frozen.with_name(f".{frozen.name}.freeze-failure-{uuid4().hex}.json")
    stage = "before-staging"
    def checkpoint(name: str) -> None:
        nonlocal stage; stage = name
        if failure_hook: failure_hook(name)
    def write(path: Path, value: dict[str, Any]) -> None:
        path.write_text(json.dumps(value, ensure_ascii=True, indent=2) + "\n", encoding="utf-8", newline="\n")
    try:
        checkpoint("before-staging"); staging.mkdir(parents=False); checkpoint("after-staging")
        staged_corpus, staged_snapshot, staged_runtime = staging / "frozen-corpus.jsonl", staging / "canonical-snapshot.json", staging / "runtime-input.jsonl"
        shutil.copyfile(reviewed / "corpus.jsonl", staged_corpus); checkpoint("after-corpus-copy")
        shutil.copyfile(reviewed / "canonical-snapshot.json", staged_snapshot); checkpoint("after-snapshot-copy")
        staged_runtime.write_text("".join(json.dumps(row, ensure_ascii=True, separators=(",", ":")) + "\n" for row in runtime_from_corpus(reviewed / "corpus.jsonl")), encoding="utf-8", newline="\n"); checkpoint("after-runtime-derive")
        final = {"reviewed_corpus": frozen / staged_corpus.name, "canonical_snapshot": frozen / staged_snapshot.name, "runtime_input": frozen / staged_runtime.name}
        records = {**{name: record(root, path) for name, path in sources.items()}, **{name: record(root, staging / path.name, declared_path=path) for name, path in final.items()}}
        state = git_state(root, list(inventory_paths)); now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
        manifest_path, attestation_path, generated, result_dir = frozen / "frozen-manifest.json", frozen / "freeze-attestation.json", frozen / "generated-frames.jsonl", frozen / "results/first-run"
        args = ["--corpus", relative_path(root, final["reviewed_corpus"]), "--runtime-input", relative_path(root, final["runtime_input"]), "--generated-frames", relative_path(root, generated), "--manifest", relative_path(root, manifest_path), "--attestation", relative_path(root, attestation_path), "--result-dir", relative_path(root, result_dir)]
        manifest = {"contract_version": CONTRACT_VERSION, "holdout_id": holdout_id, "status": "frozen", "created_at": now, "frozen_at": now, "first_runtime_execution_at": None, **records, "corpus": records["reviewed_corpus"], "evaluator": records["evaluator_wrapper"], "protocol": records["generator_procedure"], "approved_matrix": records["approved_evaluation_matrix"], "evaluator_args": args, "host_generation": {"input": records["runtime_input"]["path"], "output": relative_path(root, generated)}, "blind_output": {"path": relative_path(root, generated), "outer_fields": ["payload", "session_id"]}, "source_state": state, "artifact_policy": {"owner": "VEIL evaluation owner", "deletion_authority": "repository owner only"}}
        staged_manifest, staged_attestation = staging / manifest_path.name, staging / attestation_path.name
        write(staged_manifest, manifest); checkpoint("after-manifest-write")
        attestation = {"contract_version": CONTRACT_VERSION, "holdout_id": holdout_id, "attested_at": now, "first_runtime_execution_at": None, **records, "corpus": records["reviewed_corpus"], "evaluator": records["evaluator_wrapper"], "protocol": records["generator_procedure"], "approved_matrix": records["approved_evaluation_matrix"], "manifest": record(root, staged_manifest, declared_path=manifest_path), "source_state": state, "pre_runtime_confirmation": {"review_complete": True, "runtime_has_seen_cases": False, "generated_frames_exist": False, "frozen_inputs_will_not_be_modified": True}}
        write(staged_attestation, attestation); checkpoint("after-attestation-write")
        m, a = _validate_metadata(read_json(staged_manifest), read_json(staged_attestation))
        for name in RECORD_IDS:
            if m[name] != a[name]: raise ValueError(f"staged manifest/attestation differ for {name}")
            declared = project_path(root, m[name]["path"])
            actual = staging / declared.name if declared.parent == frozen else declared
            _check_record(root, m[name], name, actual)
        _check_record(root, a["manifest"], "staged attested manifest", staged_manifest)
        _check_state(root, m["source_state"], verify_git_state=True); checkpoint("before-rename")
        staging.replace(frozen); checkpoint("after-rename")
        return {"manifest": record(root, manifest_path), "attestation": record(root, attestation_path)}
    except Exception as exc:
        if staging.exists(): shutil.rmtree(staging)
        if not frozen.exists(): write(failure, {"status": "freeze-failed", "stage": stage, "error_type": type(exc).__name__, "error": str(exc)})
        raise
