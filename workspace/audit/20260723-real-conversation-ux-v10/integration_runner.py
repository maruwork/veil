"""Disposable v10 integration path: strict preflight then the real v4 kernel."""
from __future__ import annotations

import hashlib
import json
import sqlite3
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable
from unittest.mock import patch

from adapter_core import load_real_v4_core, score_with_real_v4_core


MANIFEST_FIELDS = frozenset(("contract_version", "holdout_id", "status", "evaluator_args", "runtime_input", "reviewed_corpus", "source_state"))
ATTESTATION_FIELDS = frozenset(("contract_version", "holdout_id", "manifest", "runtime_input", "reviewed_corpus", "source_state"))
CORE_GATES = frozenset(("all_case_outcomes_exact", "zero_high_impact_false_exclusions", "exclusion_precision_at_least_0_99", "existing_match_precision_at_least_0_99", "all_question_counts_exact", "zero_unexpected_exception_terms", "zero_contract_validation_errors"))
ALL_GATES = CORE_GATES | {"zero_raw_text_fallback", "no_canonical_db_access", "source_state_unchanged"}
_ACTIVE_AUDIT: "RuntimeAudit | None" = None


class RuntimeAudit:
    def __init__(self) -> None:
        self.canonical_db_access_attempts = 0
        self.raw_text_fallback_attempts = 0

    def forbid_db_connect(self, *args: Any, **kwargs: Any) -> None:
        self.canonical_db_access_attempts += 1
        raise RuntimeError("canonical DB access is forbidden during v10 scoring")

    def forbid_raw_text_fallback(self, *args: Any, **kwargs: Any) -> None:
        self.raw_text_fallback_attempts += 1
        raise RuntimeError("raw-text fallback is forbidden during v10 scoring")

    def snapshot(self) -> dict[str, int]:
        return {"canonical_db_access_attempts": self.canonical_db_access_attempts, "raw_text_fallback_attempts": self.raw_text_fallback_attempts}


def raw_text_fallback(*args: Any, **kwargs: Any) -> None:
    if _ACTIVE_AUDIT is None:
        raise RuntimeError("raw-text fallback hook is unavailable outside v10 scoring")
    _ACTIVE_AUDIT.forbid_raw_text_fallback(*args, **kwargs)


def _json(path: Path) -> Any:
    def unique(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        item: dict[str, Any] = {}
        for key, value in pairs:
            if key in item:
                raise ValueError(f"duplicate JSON key in {path.name}: {key}")
            item[key] = value
        return item
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique)


def _rows(path: Path) -> list[dict[str, Any]]:
    values = [_json_line(line, path) for line in path.read_text(encoding="utf-8").splitlines()]
    if not values or any(not isinstance(value, dict) for value in values):
        raise ValueError(f"{path.name} must contain JSON objects")
    return values


def _json_line(line: str, path: Path) -> Any:
    if not line:
        raise ValueError(f"{path.name} contains a blank line")
    return json.loads(line)


def _record(root: Path, path: Path) -> dict[str, Any]:
    data = path.read_bytes()
    return {"path": path.resolve().relative_to(root.resolve()).as_posix(), "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)}


def _verify_record(root: Path, item: Any, path: Path, name: str) -> None:
    if not isinstance(item, dict) or set(item) != {"path", "sha256", "bytes"} or item != _record(root, path):
        raise ValueError(f"{name} record differs from the supplied file")


def compute_source_state(root: Path, inventory: list[Path]) -> dict[str, Any]:
    records = [_record(root, path) for path in inventory]
    if len({item["path"] for item in records}) != len(records) or not records:
        raise ValueError("execution source inventory is empty or duplicate")
    digest = hashlib.sha256()
    for item, path in zip(records, inventory):
        data = path.read_bytes(); digest.update(item["path"].encode("utf-8")); digest.update(b"\0"); digest.update(len(data).to_bytes(8, "big")); digest.update(data)
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, capture_output=True, text=True, check=False).stdout.strip()
    diff = subprocess.run(["git", "diff", "--binary"], cwd=root, capture_output=True, check=False).stdout
    return {"head": head, "tracked_diff_sha256": hashlib.sha256(diff).hexdigest(), "inventory_sha256": digest.hexdigest(), "inventory": records}


def preflight(*, root: Path, manifest_path: Path, attestation_path: Path, corpus: Path, runtime: Path, generated: Path, result_dir: Path, args: list[str]) -> dict[str, Any]:
    if result_dir.exists():
        raise ValueError("first-run result directory already exists")
    manifest, attestation = _json(manifest_path), _json(attestation_path)
    if not isinstance(manifest, dict) or set(manifest) != MANIFEST_FIELDS or not isinstance(attestation, dict) or set(attestation) != ATTESTATION_FIELDS:
        raise ValueError("v10 metadata field contract is invalid")
    if manifest["contract_version"] != "2" or attestation["contract_version"] != "2" or manifest["status"] != "frozen" or manifest["holdout_id"] != attestation["holdout_id"] or manifest["evaluator_args"] != args:
        raise ValueError("v10 metadata identity or command is invalid")
    _verify_record(root, manifest["runtime_input"], runtime, "runtime input")
    _verify_record(root, manifest["reviewed_corpus"], corpus, "reviewed corpus")
    if attestation["runtime_input"] != manifest["runtime_input"] or attestation["reviewed_corpus"] != manifest["reviewed_corpus"] or attestation["source_state"] != manifest["source_state"] or attestation["manifest"] != _record(root, manifest_path):
        raise ValueError("v10 attestation parity is invalid")
    core = load_real_v4_core(root)
    runtime_by_session, generated_by_session = core.validate_blind_inputs(_rows(runtime), _rows(generated))
    from shared.tools.veil_decision_frames import FrameValidationError, analyze_decision_frames  # noqa: PLC0415
    for session_id, generated_row in generated_by_session.items():
        try:
            analyze_decision_frames(runtime_by_session[session_id]["source_text"], generated_row["payload"], runtime_by_session[session_id]["registered_terms"])
        except FrameValidationError as exc:
            raise ValueError(f"generated payload is invalid before labels: {exc}") from exc
    return manifest


def run_once(*, root: Path, manifest_path: Path, attestation_path: Path, corpus: Path, runtime: Path, generated: Path, result_dir: Path, args: list[str], inventory: list[Path], after_runtime_start: Callable[[], None] | None = None) -> int:
    manifest = preflight(root=root, manifest_path=manifest_path, attestation_path=attestation_path, corpus=corpus, runtime=runtime, generated=generated, result_dir=result_dir, args=args)
    before = compute_source_state(root, inventory)
    if before != manifest["source_state"]:
        raise ValueError("source state changed before runtime start")
    result_dir.mkdir(parents=True, exist_ok=False)
    audit = RuntimeAudit()
    initial = {"contract_version": "2", "holdout_id": manifest["holdout_id"], "status": "runtime-started", "started_at": datetime.now(timezone.utc).isoformat(), "source_state_before": before, "runtime_access": audit.snapshot()}
    (result_dir / "result-manifest.json").write_text(json.dumps(initial, ensure_ascii=True), encoding="utf-8")
    try:
        if after_runtime_start is not None:
            after_runtime_start()
        global _ACTIVE_AUDIT
        _ACTIVE_AUDIT = audit
        try:
            with patch.object(sqlite3, "connect", audit.forbid_db_connect):
                scored = score_with_real_v4_core(root=root, runtime_rows=_rows(runtime), generated_rows=_rows(generated), corpus_rows=_rows(corpus), holdout_id=manifest["holdout_id"])
        finally:
            _ACTIVE_AUDIT = None
        after = compute_source_state(root, inventory)
        gates = {**scored["summary"]["gates"], "zero_raw_text_fallback": audit.raw_text_fallback_attempts == 0, "no_canonical_db_access": audit.canonical_db_access_attempts == 0, "source_state_unchanged": after == before}
        if set(gates) != ALL_GATES:
            raise ValueError("real-core score did not return the exact v10 gates")
        summary = {**scored["summary"], "status": "passed" if all(gates.values()) else "failed", "gates": gates}
        (result_dir / "case-results.jsonl").write_text("".join(json.dumps(item, ensure_ascii=True) + "\n" for item in scored["case_results"]), encoding="utf-8")
        (result_dir / "summary.json").write_text(json.dumps(summary, ensure_ascii=True), encoding="utf-8")
        terminal = {**initial, "status": "scored", "completed_at": datetime.now(timezone.utc).isoformat(), "source_state_after": after, "runtime_access": audit.snapshot(), "gates": gates}
        (result_dir / "result-manifest.json").write_text(json.dumps(terminal, ensure_ascii=True), encoding="utf-8")
        return 0 if all(gates.values()) else 1
    except Exception as exc:
        terminal = {**initial, "status": "runtime-error", "completed_at": datetime.now(timezone.utc).isoformat(), "runtime_access": audit.snapshot(), "runtime_error": {"type": type(exc).__name__, "message": str(exc)}}
        (result_dir / "result-manifest.json").write_text(json.dumps(terminal, ensure_ascii=True), encoding="utf-8")
        return 1
