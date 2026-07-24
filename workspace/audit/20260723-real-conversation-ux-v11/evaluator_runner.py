"""Terminal-result runner shared by v11 production evaluation and disposable acceptance tests."""
from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable
from unittest.mock import patch

from core_boundary import score_real_core
from runtime_audit import RuntimeAudit
from source_state import compute


CORE_GATES = frozenset(("all_case_outcomes_exact", "zero_high_impact_false_exclusions", "exclusion_precision_at_least_0_99", "existing_match_precision_at_least_0_99", "all_question_counts_exact", "zero_unexpected_exception_terms", "zero_contract_validation_errors"))
ALL_GATES = CORE_GATES | {"zero_raw_text_fallback", "no_canonical_db_access", "source_state_unchanged"}


def _write(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")


def run_once(
    *,
    root: Path,
    holdout_id: str,
    runtime_rows: list[dict[str, Any]],
    generated_rows: list[dict[str, Any]],
    corpus_rows: list[dict[str, Any]],
    result_dir: Path,
    inventory: list[Path],
    after_runtime_start: Callable[[], None] | None = None,
) -> int:
    if result_dir.exists():
        raise ValueError("first-run result directory already exists")
    before = compute(root, inventory)
    result_dir.mkdir(parents=True, exist_ok=False)
    audit = RuntimeAudit()
    initial = {"contract_version": "2", "holdout_id": holdout_id, "status": "runtime-started", "started_at": datetime.now(timezone.utc).isoformat(), "source_state_before": before, "runtime_access": audit.snapshot()}
    _write(result_dir / "result-manifest.json", initial)
    try:
        if after_runtime_start is not None:
            after_runtime_start()
        with patch.object(sqlite3, "connect", audit.deny_db_connect):
            scored = score_real_core(runtime_rows=runtime_rows, generated_rows=generated_rows, corpus_rows=corpus_rows, holdout_id=holdout_id, raw_text_fallback=audit.deny_raw_text_fallback)
        after = compute(root, inventory)
        gates = {**scored["summary"]["gates"], "zero_raw_text_fallback": audit.raw_text_fallback_attempts == 0, "no_canonical_db_access": audit.canonical_db_access_attempts == 0, "source_state_unchanged": after == before}
        if set(gates) != ALL_GATES:
            raise ValueError("terminal gate set is invalid")
        _write(result_dir / "summary.json", {**scored["summary"], "status": "passed" if all(gates.values()) else "failed", "gates": gates})
        (result_dir / "case-results.jsonl").write_text("".join(json.dumps(row, ensure_ascii=True) + "\n" for row in scored["case_results"]), encoding="utf-8")
        _write(result_dir / "result-manifest.json", {**initial, "status": "scored", "completed_at": datetime.now(timezone.utc).isoformat(), "source_state_after": after, "runtime_access": audit.snapshot(), "gates": gates})
        return 0 if all(gates.values()) else 1
    except Exception as exc:
        _write(result_dir / "result-manifest.json", {**initial, "status": "runtime-error", "completed_at": datetime.now(timezone.utc).isoformat(), "runtime_access": audit.snapshot(), "runtime_error": {"type": type(exc).__name__, "message": str(exc)}})
        return 1
