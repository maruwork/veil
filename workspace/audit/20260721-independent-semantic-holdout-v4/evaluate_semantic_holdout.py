from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from dataclasses import asdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from typing import Any, Iterable

from shared.tools.veil_decision_frames import BLIND_GENERATED_ROW_FIELDS


PROJECT_ROOT = Path(__file__).resolve().parents[3]
GENERATED_FIELDS = BLIND_GENERATED_ROW_FIELDS
RUNTIME_FIELDS = {"session_id", "source_text", "registered_terms"}
CORE_SCORE_GATES = frozenset(
    {
        "all_case_outcomes_exact",
        "zero_high_impact_false_exclusions",
        "exclusion_precision_at_least_0_99",
        "existing_match_precision_at_least_0_99",
        "all_question_counts_exact",
        "zero_unexpected_exception_terms",
        "zero_contract_validation_errors",
    }
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate a frozen contract-v2 semantic holdout once.")
    parser.add_argument("--corpus", type=Path, required=True)
    parser.add_argument("--runtime-input", type=Path, required=True)
    parser.add_argument("--generated-frames", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--attestation", type=Path, required=True)
    parser.add_argument("--result-dir", type=Path, required=True)
    return parser.parse_args()


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def file_record(path: Path) -> dict[str, Any]:
    data = path.read_bytes()
    return {"sha256": sha256_bytes(data), "bytes": len(data)}


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
        raise ValueError(f"{path.name} must contain a JSON object")
    return value


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            raise ValueError(f"{path.name}:{line_number}: blank JSONL line")
        value = json.loads(line, object_pairs_hook=reject_duplicate_keys)
        if not isinstance(value, dict):
            raise ValueError(f"{path.name}:{line_number}: row must be an object")
        rows.append(value)
    return rows


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def resolve_project_path(path: Path) -> Path:
    resolved = path if path.is_absolute() else PROJECT_ROOT / path
    resolved = resolved.resolve()
    try:
        resolved.relative_to(PROJECT_ROOT)
    except ValueError as exc:
        raise ValueError(f"path is outside the project root: {path}") from exc
    return resolved


def assert_file_record(path: Path, expected: Any, *, label: str) -> None:
    if not path.is_file():
        raise ValueError(f"{label} is missing: {path}")
    if not isinstance(expected, dict):
        raise ValueError(f"{label} record is invalid")
    actual = file_record(path)
    for field in ("sha256", "bytes"):
        if actual[field] != expected.get(field):
            raise ValueError(f"{label} {field} mismatch")


def git_output(*args: str) -> bytes:
    completed = subprocess.run(
        ["git", *args],
        cwd=PROJECT_ROOT,
        check=True,
        capture_output=True,
    )
    return completed.stdout


def compute_source_state(manifest: dict[str, Any]) -> dict[str, Any]:
    expected = manifest.get("source_state")
    if not isinstance(expected, dict):
        raise ValueError("manifest source_state is invalid")
    inventory = expected.get("release_scope_inventory")
    if not isinstance(inventory, list) or not inventory:
        raise ValueError("manifest source inventory is invalid")
    hasher = hashlib.sha256()
    current_records: list[dict[str, Any]] = []
    seen: set[str] = set()
    for index, record in enumerate(inventory):
        if not isinstance(record, dict) or set(record) != {"path", "sha256", "bytes"}:
            raise ValueError(f"source inventory record {index + 1} is invalid")
        relative = record["path"]
        if not isinstance(relative, str) or relative in seen:
            raise ValueError(f"source inventory path {index + 1} is invalid or duplicate")
        seen.add(relative)
        path = resolve_project_path(Path(relative))
        assert_file_record(path, record, label=f"source inventory path {relative}")
        data = path.read_bytes()
        normalized = Path(relative).as_posix()
        current_records.append({"path": normalized, **file_record(path)})
        hasher.update(normalized.encode("utf-8"))
        hasher.update(b"\0")
        hasher.update(len(data).to_bytes(8, "big"))
        hasher.update(data)
    current = {
        "head": git_output("rev-parse", "HEAD").decode("ascii").strip(),
        "tracked_diff_sha256": sha256_bytes(
            git_output("diff", "--binary", "--no-ext-diff", "HEAD", "--", ".")
        ),
        "release_scope_inventory_sha256": hasher.hexdigest(),
        "release_scope_inventory": current_records,
    }
    if current != expected:
        raise ValueError("source state changed after freeze")
    return current


def validate_preflight(args: argparse.Namespace) -> tuple[dict[str, Any], dict[str, Any], dict[str, Path]]:
    paths = {
        "corpus": resolve_project_path(args.corpus),
        "runtime_input": resolve_project_path(args.runtime_input),
        "generated_frames": resolve_project_path(args.generated_frames),
        "manifest": resolve_project_path(args.manifest),
        "attestation": resolve_project_path(args.attestation),
        "result_dir": resolve_project_path(args.result_dir),
    }
    if paths["result_dir"].exists():
        raise ValueError(f"result directory already exists: {paths['result_dir']}")
    manifest = read_json(paths["manifest"])
    attestation = read_json(paths["attestation"])
    if manifest.get("contract_version") != "2" or attestation.get("contract_version") != "2":
        raise ValueError("manifest and attestation must use contract version 2")
    if manifest.get("status") != "frozen":
        raise ValueError("manifest status must be frozen")
    if manifest.get("first_runtime_execution_at") is not None:
        raise ValueError("manifest first_runtime_execution_at must remain null")
    if attestation.get("first_runtime_execution_at") is not None:
        raise ValueError("attestation first_runtime_execution_at must remain null")
    if manifest.get("holdout_id") != attestation.get("holdout_id"):
        raise ValueError("manifest and attestation holdout IDs differ")
    if sys.argv[1:] != manifest.get("evaluator_args"):
        raise ValueError("evaluator arguments differ from the frozen exact command")

    for key, cli_key in (("corpus", "corpus"), ("runtime_input", "runtime_input")):
        record = manifest.get(key)
        if not isinstance(record, dict) or resolve_project_path(Path(str(record.get("path", "")))) != paths[cli_key]:
            raise ValueError(f"manifest {key} path differs from the evaluator command")
        assert_file_record(paths[cli_key], record, label=key)
        assert_file_record(paths[cli_key], attestation.get(key), label=f"attested {key}")

    manifest_generated = manifest.get("host_generation", {}).get("output")
    if not isinstance(manifest_generated, str) or resolve_project_path(Path(manifest_generated)) != paths["generated_frames"]:
        raise ValueError("generated-frame path differs from the frozen host-generation contract")
    assert_file_record(paths["manifest"], attestation.get("manifest"), label="attested manifest")

    for key in ("protocol", "approved_matrix", "evaluator"):
        record = manifest.get(key)
        if not isinstance(record, dict) or not isinstance(record.get("path"), str):
            raise ValueError(f"manifest {key} record is invalid")
        current_path = resolve_project_path(Path(record["path"]))
        assert_file_record(current_path, record, label=key)
        assert_file_record(current_path, attestation.get(key), label=f"attested {key}")
    if attestation.get("source_state") != manifest.get("source_state"):
        raise ValueError("attested source state differs from the manifest")
    compute_source_state(manifest)
    assert_file_record(paths["generated_frames"], file_record(paths["generated_frames"]), label="generated frames")
    return manifest, attestation, paths


def validate_blind_inputs(
    runtime_rows: list[dict[str, Any]], generated_rows: list[dict[str, Any]]
) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    runtime_by_session: dict[str, dict[str, Any]] = {}
    for index, row in enumerate(runtime_rows):
        if set(row) != RUNTIME_FIELDS:
            raise ValueError(f"runtime row {index + 1} has an invalid field set")
        session_id = row.get("session_id")
        if not isinstance(session_id, str) or not session_id or session_id in runtime_by_session:
            raise ValueError(f"runtime row {index + 1} has an invalid or duplicate session_id")
        if not isinstance(row.get("source_text"), str):
            raise ValueError(f"runtime row {index + 1} has invalid source_text")
        registered = row.get("registered_terms")
        if not isinstance(registered, list) or any(not isinstance(term, str) for term in registered):
            raise ValueError(f"runtime row {index + 1} has invalid registered_terms")
        runtime_by_session[session_id] = row

    generated_by_session: dict[str, dict[str, Any]] = {}
    for index, row in enumerate(generated_rows):
        if set(row) != GENERATED_FIELDS:
            raise ValueError(f"generated row {index + 1} has an invalid field set")
        session_id = row.get("session_id")
        if not isinstance(session_id, str) or not session_id or session_id in generated_by_session:
            raise ValueError(f"generated row {index + 1} has an invalid or duplicate session_id")
        if not isinstance(row.get("payload"), dict):
            raise ValueError(f"generated row {index + 1} has an invalid payload")
        generated_by_session[session_id] = row
    if set(generated_by_session) != set(runtime_by_session):
        raise ValueError("generated-frame session IDs do not exactly match blind runtime input")
    return runtime_by_session, generated_by_session


def match_expected_rows(
    expected_rows: list[dict[str, Any]], outcomes: list[Any], normalize_term: Any
) -> tuple[list[tuple[dict[str, Any], Any | None]], list[Any]]:
    unmatched = list(range(len(outcomes)))
    matches: list[tuple[dict[str, Any], Any | None]] = []
    for expected in expected_rows:
        normalized = normalize_term(expected["term"])
        exact = [index for index in unmatched if outcomes[index].normalized == normalized]
        preferred = [
            index
            for index in unmatched
            if outcomes[index].requested_preferred
            and normalize_term(outcomes[index].requested_preferred) == normalized
        ]
        candidates = exact or preferred
        if candidates:
            selected = candidates[0]
            unmatched.remove(selected)
            matches.append((expected, outcomes[selected]))
        else:
            matches.append((expected, None))
    return matches, [outcomes[index] for index in unmatched]


def score_prevalidated(
    *,
    runtime_rows: list[dict[str, Any]],
    generated_rows: list[dict[str, Any]],
    corpus_rows: list[dict[str, Any]],
    holdout_id: str,
) -> dict[str, Any]:
    """Score parsed inputs without manifest, path, result-directory, or DB work.

    This is the real v4 scoring kernel for adapters that have already completed
    their own integrity preflight.  It retains v4 matching and metric behavior
    while returning data for the caller to own terminal persistence and gates.
    """
    if not isinstance(holdout_id, str) or not holdout_id:
        raise ValueError("holdout_id must be a non-empty string")
    runtime_by_session, generated_by_session = validate_blind_inputs(runtime_rows, generated_rows)
    if str(PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT))
    from shared.tools.veil_decision_frames import FrameValidationError, analyze_decision_frames  # noqa: PLC0415
    from shared.tools.veil_rule_store import normalize_term  # noqa: PLC0415

    corpus_by_session: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in corpus_rows:
        session_id = row.get("session_id")
        if not isinstance(session_id, str) or session_id not in runtime_by_session:
            raise ValueError("corpus contains an invalid or unknown session ID")
        corpus_by_session[session_id].append(row)
    if set(corpus_by_session) != set(runtime_by_session):
        raise ValueError("corpus session IDs do not match blind runtime input")

    case_results: list[dict[str, Any]] = []
    session_results: list[dict[str, Any]] = []
    effective_units: list[dict[str, Any]] = []
    validation_error_count = 0
    unexpected_exception_count = 0
    high_impact_false_exclusion_count = 0
    question_mismatch_count = 0

    for session_id, runtime in runtime_by_session.items():
        expected_rows = corpus_by_session[session_id]
        payload = generated_by_session[session_id]["payload"]
        errors: list[str] = []
        outcomes: list[Any] = []
        validated_frame_count = 0
        critic_status: str | None = None
        try:
            analysis = analyze_decision_frames(runtime["source_text"], payload, registered_terms=runtime["registered_terms"])
            outcomes = list(analysis.results)
            validated_frame_count = analysis.validated_frame_count
            critic_status = analysis.critic_status
        except FrameValidationError as exc:
            errors = list(exc.errors)
            validation_error_count += 1

        matches, unmatched = match_expected_rows(expected_rows, outcomes, normalize_term)
        actual_exception_terms = [outcome.normalized for outcome in outcomes if outcome.outcome == "exception"]
        expected_exception_terms = {normalize_term(row["term"]) for row in expected_rows if row["expected_outcome"] == "exception"}
        unexpected_exceptions = [outcome for outcome in unmatched if outcome.outcome == "exception"]
        unexpected_exception_count += len(unexpected_exceptions)
        expected_question_count = 1 if expected_exception_terms else 0
        actual_question_count = 1 if actual_exception_terms else 0
        question_matches = expected_question_count == actual_question_count
        if not question_matches:
            question_mismatch_count += 1

        for expected, outcome in matches:
            actual_outcome = outcome.outcome if outcome is not None else "exclude"
            actual_reason = outcome.reason if outcome is not None else "no-semantic-frame"
            exact = actual_outcome == expected["expected_outcome"]
            high_impact_false_exclusion = expected["impact"] == "high" and expected["expected_outcome"] == "exception" and actual_outcome != "exception"
            if high_impact_false_exclusion:
                high_impact_false_exclusion_count += 1
            case_results.append({"case_id": expected["case_id"], "session_id": session_id, "term": expected["term"], "expected_outcome": expected["expected_outcome"], "actual_outcome": actual_outcome, "actual_reason": actual_reason, "impact": expected["impact"], "exact_match": exact, "high_impact_false_exclusion": high_impact_false_exclusion, "matched_frame_id": outcome.frame_id if outcome is not None else None})
            effective_units.append({"expected_outcome": expected["expected_outcome"], "actual_outcome": actual_outcome})
        for outcome in unmatched:
            effective_units.append({"expected_outcome": None, "actual_outcome": outcome.outcome})
        session_results.append({"session_id": session_id, "validation_errors": errors, "validated_frame_count": validated_frame_count, "critic_status": critic_status, "expected_question_count": expected_question_count, "actual_question_count": actual_question_count, "question_count_matches": question_matches, "unexpected_exception_count": len(unexpected_exceptions), "unmatched_runtime_results": [asdict(outcome) for outcome in unmatched]})

    expected_count = len(case_results)
    exact_count = sum(item["exact_match"] for item in case_results)
    actual_excludes = [unit for unit in effective_units if unit["actual_outcome"] == "exclude"]
    true_excludes = sum(unit["expected_outcome"] == "exclude" for unit in actual_excludes)
    exclusion_precision = true_excludes / len(actual_excludes) if actual_excludes else 1.0
    actual_existing = [unit for unit in effective_units if unit["actual_outcome"] == "existing-match"]
    true_existing = sum(unit["expected_outcome"] == "existing-match" for unit in actual_existing)
    existing_precision = true_existing / len(actual_existing) if actual_existing else 1.0
    gates = {
        "all_case_outcomes_exact": exact_count == expected_count,
        "zero_high_impact_false_exclusions": high_impact_false_exclusion_count == 0,
        "exclusion_precision_at_least_0_99": exclusion_precision >= 0.99,
        "existing_match_precision_at_least_0_99": existing_precision >= 0.99,
        "all_question_counts_exact": question_mismatch_count == 0,
        "zero_unexpected_exception_terms": unexpected_exception_count == 0,
        "zero_contract_validation_errors": validation_error_count == 0,
    }
    return {"case_results": case_results, "summary": {"holdout_id": holdout_id, "status": "passed" if all(gates.values()) else "failed", "case_count": expected_count, "exact_case_count": exact_count, "session_count": len(session_results), "validation_error_session_count": validation_error_count, "high_impact_false_exclusion_count": high_impact_false_exclusion_count, "question_mismatch_session_count": question_mismatch_count, "unexpected_exception_count": unexpected_exception_count, "exclusion_precision": exclusion_precision, "existing_match_precision": existing_precision, "gates": gates, "sessions": session_results}}


def runtime_access_snapshot() -> dict[str, Any]:
    """Return runtime-access evidence; v7 replaces this with fail-closed counters."""
    return {
        "canonical_db_access_performed": False,
        "raw_text_fallback_count": 0,
    }


def main() -> int:
    args = parse_args()
    manifest, _attestation, paths = validate_preflight(args)

    # Blind artifacts are parsed and cross-checked before expected labels are read.
    runtime_rows = read_jsonl(paths["runtime_input"])
    generated_rows = read_jsonl(paths["generated_frames"])
    runtime_by_session, generated_by_session = validate_blind_inputs(runtime_rows, generated_rows)

    first_runtime_at = utc_now()
    paths["result_dir"].mkdir(parents=True, exist_ok=False)
    result_manifest_path = paths["result_dir"] / "result-manifest.json"
    access_evidence = runtime_access_snapshot()
    result_manifest: dict[str, Any] = {
        "contract_version": "2",
        "holdout_id": manifest["holdout_id"],
        "status": "runtime-started",
        "first_runtime_execution_at": first_runtime_at,
        "frozen_manifest": file_record(paths["manifest"]),
        "freeze_attestation": file_record(paths["attestation"]),
        "generated_frames": file_record(paths["generated_frames"]),
        "source_state_before": manifest["source_state"],
        **access_evidence,
    }
    write_json(result_manifest_path, result_manifest)

    if str(PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT))
    from shared.tools.veil_decision_frames import (  # noqa: PLC0415
        FrameValidationError,
        analyze_decision_frames,
    )
    from shared.tools.veil_rule_store import normalize_term  # noqa: PLC0415

    # Expected labels become visible to the evaluator only after blind generation is complete.
    corpus_rows = read_jsonl(paths["corpus"])
    corpus_by_session: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in corpus_rows:
        session_id = row.get("session_id")
        if not isinstance(session_id, str) or session_id not in runtime_by_session:
            raise ValueError("corpus contains an invalid or unknown session ID")
        corpus_by_session[session_id].append(row)
    if set(corpus_by_session) != set(runtime_by_session):
        raise ValueError("corpus session IDs do not match blind runtime input")

    case_results: list[dict[str, Any]] = []
    session_results: list[dict[str, Any]] = []
    effective_units: list[dict[str, Any]] = []
    validation_error_count = 0
    unexpected_exception_count = 0
    high_impact_false_exclusion_count = 0
    question_mismatch_count = 0

    for session_id, runtime in runtime_by_session.items():
        expected_rows = corpus_by_session[session_id]
        payload = generated_by_session[session_id]["payload"]
        errors: list[str] = []
        outcomes: list[Any] = []
        validated_frame_count = 0
        critic_status: str | None = None
        try:
            analysis = analyze_decision_frames(
                runtime["source_text"], payload, registered_terms=runtime["registered_terms"]
            )
            outcomes = list(analysis.results)
            validated_frame_count = analysis.validated_frame_count
            critic_status = analysis.critic_status
        except FrameValidationError as exc:
            errors = list(exc.errors)
            validation_error_count += 1

        matches, unmatched = match_expected_rows(expected_rows, outcomes, normalize_term)
        actual_exception_terms = [outcome.normalized for outcome in outcomes if outcome.outcome == "exception"]
        expected_exception_terms = {
            normalize_term(row["term"]) for row in expected_rows if row["expected_outcome"] == "exception"
        }
        unexpected_exceptions = [outcome for outcome in unmatched if outcome.outcome == "exception"]
        unexpected_exception_count += len(unexpected_exceptions)

        expected_question_count = 1 if expected_exception_terms else 0
        actual_question_count = 1 if actual_exception_terms else 0
        question_matches = expected_question_count == actual_question_count
        if not question_matches:
            question_mismatch_count += 1

        for expected, outcome in matches:
            actual_outcome = outcome.outcome if outcome is not None else "exclude"
            actual_reason = outcome.reason if outcome is not None else "no-semantic-frame"
            exact = actual_outcome == expected["expected_outcome"]
            high_impact_false_exclusion = (
                expected["impact"] == "high"
                and expected["expected_outcome"] == "exception"
                and actual_outcome != "exception"
            )
            if high_impact_false_exclusion:
                high_impact_false_exclusion_count += 1
            record = {
                "case_id": expected["case_id"],
                "session_id": session_id,
                "term": expected["term"],
                "expected_outcome": expected["expected_outcome"],
                "actual_outcome": actual_outcome,
                "actual_reason": actual_reason,
                "impact": expected["impact"],
                "exact_match": exact,
                "high_impact_false_exclusion": high_impact_false_exclusion,
                "matched_frame_id": outcome.frame_id if outcome is not None else None,
            }
            case_results.append(record)
            effective_units.append(
                {
                    "expected_outcome": expected["expected_outcome"],
                    "actual_outcome": actual_outcome,
                }
            )

        for outcome in unmatched:
            effective_units.append({"expected_outcome": None, "actual_outcome": outcome.outcome})

        session_results.append(
            {
                "session_id": session_id,
                "validation_errors": errors,
                "validated_frame_count": validated_frame_count,
                "critic_status": critic_status,
                "expected_question_count": expected_question_count,
                "actual_question_count": actual_question_count,
                "question_count_matches": question_matches,
                "unexpected_exception_count": len(unexpected_exceptions),
                "unmatched_runtime_results": [asdict(outcome) for outcome in unmatched],
            }
        )

    expected_count = len(case_results)
    exact_count = sum(record["exact_match"] for record in case_results)
    actual_excludes = [unit for unit in effective_units if unit["actual_outcome"] == "exclude"]
    true_excludes = sum(unit["expected_outcome"] == "exclude" for unit in actual_excludes)
    exclusion_precision = true_excludes / len(actual_excludes) if actual_excludes else 1.0
    actual_existing = [unit for unit in effective_units if unit["actual_outcome"] == "existing-match"]
    true_existing = sum(unit["expected_outcome"] == "existing-match" for unit in actual_existing)
    existing_precision = true_existing / len(actual_existing) if actual_existing else 1.0

    source_state_after = compute_source_state(manifest)
    gates = {
        "all_case_outcomes_exact": exact_count == expected_count,
        "zero_high_impact_false_exclusions": high_impact_false_exclusion_count == 0,
        "exclusion_precision_at_least_0_99": exclusion_precision >= 0.99,
        "existing_match_precision_at_least_0_99": existing_precision >= 0.99,
        "all_question_counts_exact": question_mismatch_count == 0,
        "zero_unexpected_exception_terms": unexpected_exception_count == 0,
        "zero_contract_validation_errors": validation_error_count == 0,
        "zero_raw_text_fallback": result_manifest["raw_text_fallback_count"] == 0,
        "no_canonical_db_access": result_manifest["canonical_db_access_performed"] is False,
        "source_state_unchanged": source_state_after == manifest["source_state"],
    }
    passed = all(gates.values())
    summary = {
        "holdout_id": manifest["holdout_id"],
        "status": "passed" if passed else "failed",
        "case_count": expected_count,
        "exact_case_count": exact_count,
        "session_count": len(session_results),
        "validation_error_session_count": validation_error_count,
        "high_impact_false_exclusion_count": high_impact_false_exclusion_count,
        "question_mismatch_session_count": question_mismatch_count,
        "unexpected_exception_count": unexpected_exception_count,
        "exclusion_precision": exclusion_precision,
        "existing_match_precision": existing_precision,
        "gates": gates,
        "sessions": session_results,
    }
    case_results_path = paths["result_dir"] / "case-results.jsonl"
    summary_path = paths["result_dir"] / "summary.json"
    write_jsonl(case_results_path, case_results)
    write_json(summary_path, summary)
    result_manifest.update(
        {
            "status": "passed" if passed else "failed",
            "completed_at": utc_now(),
            "case_results": file_record(case_results_path),
            "summary": file_record(summary_path),
            "source_state_after": source_state_after,
            "gates": gates,
        }
    )
    write_json(result_manifest_path, result_manifest)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except Exception as exc:
        # If runtime already started, preserve the failure beside the immutable
        # first-run evidence. Preflight failures never create or overwrite a
        # result directory.
        try:
            failure_args = parse_args()
            failure_dir = resolve_project_path(failure_args.result_dir)
            failure_manifest_path = failure_dir / "result-manifest.json"
            if failure_manifest_path.is_file():
                failure_manifest = read_json(failure_manifest_path)
                if failure_manifest.get("status") == "runtime-started":
                    failure_manifest.update(
                        {
                            "status": "runtime-error",
                            "failed_at": utc_now(),
                            "error_type": type(exc).__name__,
                            "error": str(exc),
                        }
                    )
                    write_json(failure_manifest_path, failure_manifest)
        except Exception:
            pass
        raise
