"""One-shot v10 evaluator: frozen preflight, real v4 kernel, terminal result."""
from __future__ import annotations

import argparse
import importlib.util
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[3]
RUN = Path(__file__).resolve().parent
CORE_GATES = frozenset(("all_case_outcomes_exact", "zero_high_impact_false_exclusions", "exclusion_precision_at_least_0_99", "existing_match_precision_at_least_0_99", "all_question_counts_exact", "zero_unexpected_exception_terms", "zero_contract_validation_errors"))
ALL_GATES = CORE_GATES | {"zero_raw_text_fallback", "no_canonical_db_access", "source_state_unchanged"}


def local_module(name: str, filename: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, RUN / filename)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load v10 local module: {filename}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class RuntimeAudit:
    def __init__(self) -> None:
        self.db_attempts = 0
        self.raw_fallback_attempts = 0

    def deny_db(self, *args: Any, **kwargs: Any) -> None:
        self.db_attempts += 1
        raise RuntimeError("canonical DB access is forbidden during v10 evaluation")

    def deny_raw_text_fallback(self, *_args: Any, **_kwargs: Any) -> None:
        self.raw_fallback_attempts += 1
        raise RuntimeError("raw-text fallback is forbidden during v10 evaluation")

    def snapshot(self) -> dict[str, int]:
        return {"canonical_db_access_attempts": self.db_attempts, "raw_text_fallback_attempts": self.raw_fallback_attempts}


def rows(path: Path) -> list[dict[str, Any]]:
    values = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]
    if not values or any(not isinstance(value, dict) for value in values):
        raise ValueError(f"invalid JSONL: {path}")
    return values


def require_label_free_runtime(runtime_rows: list[dict[str, Any]], audit: RuntimeAudit) -> list[dict[str, Any]]:
    """Reject a fallback-shaped runtime row before real-core scoring.

    The production evaluator never reconstructs missing source text from a raw
    transcript or any other artifact. The deny hook is therefore a real
    execution boundary, not a manifest-only counter.
    """
    for row in runtime_rows:
        source = row.get("source_text") if isinstance(row, dict) else None
        terms = row.get("registered_terms") if isinstance(row, dict) else None
        if not isinstance(source, str) or not source or not isinstance(terms, list) or any(not isinstance(term, str) for term in terms):
            audit.deny_raw_text_fallback(row if isinstance(row, dict) else {}, "missing label-free runtime source_text")
    return runtime_rows


def write(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=True, indent=2) + "\n", encoding="utf-8", newline="\n")


def fixed_args(frozen: Path) -> list[str]:
    return ["--corpus", (frozen / "frozen-corpus.jsonl").resolve().relative_to(ROOT).as_posix(), "--runtime-input", (frozen / "runtime-input.jsonl").resolve().relative_to(ROOT).as_posix(), "--generated-frames", (frozen / "generated-frames.jsonl").resolve().relative_to(ROOT).as_posix(), "--manifest", (frozen / "frozen-manifest.json").resolve().relative_to(ROOT).as_posix(), "--attestation", (frozen / "freeze-attestation.json").resolve().relative_to(ROOT).as_posix(), "--result-dir", (frozen / "results/first-run").resolve().relative_to(ROOT).as_posix()]


def evaluate(frozen: Path) -> int:
    frozen = frozen.resolve()
    manifest_path, attestation_path = frozen / "frozen-manifest.json", frozen / "freeze-attestation.json"
    corpus, runtime, generated, result = frozen / "frozen-corpus.jsonl", frozen / "runtime-input.jsonl", frozen / "generated-frames.jsonl", frozen / "results/first-run"
    args = fixed_args(frozen)
    integrity = local_module("veil_v10_integrity_for_evaluator", "holdout_integrity.py")
    adapter = local_module("veil_v10_adapter_for_evaluator", "adapter_core.py")
    manifest = integrity.validate_preflight(root=ROOT, corpus=corpus, runtime_input=runtime, generated_frames=generated, manifest_path=manifest_path, attestation_path=attestation_path, result_dir=result, evaluator_args=args)
    impl = integrity.load_impl()
    before = impl.verify_source_state(ROOT, manifest["source_state"])
    result.mkdir(parents=True, exist_ok=False)
    audit = RuntimeAudit()
    initial = {"contract_version": "2", "holdout_id": manifest["holdout_id"], "status": "runtime-started", "started_at": datetime.now(timezone.utc).isoformat(), "source_state_before": before, "runtime_access": audit.snapshot()}
    write(result / "result-manifest.json", initial)
    try:
        with patch.object(sqlite3, "connect", audit.deny_db):
            scored = adapter.score_with_real_v4_core(root=ROOT, runtime_rows=require_label_free_runtime(rows(runtime), audit), generated_rows=rows(generated), corpus_rows=rows(corpus), holdout_id=manifest["holdout_id"])
        after = impl.verify_source_state(ROOT, manifest["source_state"])
        gates = {**scored["summary"]["gates"], "zero_raw_text_fallback": audit.raw_fallback_attempts == 0, "no_canonical_db_access": audit.db_attempts == 0, "source_state_unchanged": after == before}
        if set(gates) != ALL_GATES:
            raise ValueError("v10 terminal gate set is invalid")
        summary = {**scored["summary"], "status": "passed" if all(gates.values()) else "failed", "gates": gates}
        (result / "case-results.jsonl").write_text("".join(json.dumps(row, ensure_ascii=True) + "\n" for row in scored["case_results"]), encoding="utf-8", newline="\n")
        write(result / "summary.json", summary)
        write(result / "result-manifest.json", {**initial, "status": "scored", "completed_at": datetime.now(timezone.utc).isoformat(), "source_state_after": after, "runtime_access": audit.snapshot(), "gates": gates})
        return 0 if all(gates.values()) else 1
    except Exception as exc:
        write(result / "result-manifest.json", {**initial, "status": "runtime-error", "completed_at": datetime.now(timezone.utc).isoformat(), "runtime_access": audit.snapshot(), "runtime_error": {"type": type(exc).__name__, "message": str(exc)}})
        return 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--frozen-dir", type=Path, required=True)
    args = parser.parse_args()
    frozen = (args.frozen_dir if args.frozen_dir.is_absolute() else ROOT / args.frozen_dir).resolve()
    if frozen != RUN / "frozen":
        raise ValueError("v10 evaluator accepts only its declared frozen directory")
    return evaluate(frozen)


if __name__ == "__main__":
    raise SystemExit(main())
