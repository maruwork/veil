from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys
import sqlite3
from unittest.mock import patch

import pytest


ROOT = Path(__file__).resolve().parents[1]
V11 = ROOT / "workspace/audit/20260723-real-conversation-ux-v11"
V4 = ROOT / "workspace/audit/20260721-independent-semantic-holdout-v4/frozen"


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    sys.path.insert(0, str(path.parent))
    try:
        spec.loader.exec_module(module)
    finally:
        sys.path.remove(str(path.parent))
    return module


def fixture_rows() -> tuple[list[dict], list[dict], list[dict]]:
    rows = []
    for name in ("runtime-input.jsonl", "generated-frames.jsonl", "frozen-corpus.jsonl"):
        rows.append([json.loads(line) for line in (V4 / name).read_text(encoding="utf-8").splitlines() if line])
    return rows[0], rows[1], rows[2]


def test_production_boundary_scores_with_real_v4_core_without_fallback() -> None:
    boundary = load("v11_boundary_normal", V11 / "core_boundary.py")
    audit = load("v11_audit_normal", V11 / "runtime_audit.py").RuntimeAudit()
    runtime, generated, corpus = fixture_rows()
    result = boundary.score_real_core(runtime_rows=runtime, generated_rows=generated, corpus_rows=corpus, holdout_id="v11-disposable", raw_text_fallback=audit.deny_raw_text_fallback)
    assert result["summary"]["holdout_id"] == "v11-disposable"
    assert audit.raw_text_fallback_attempts == 0


def test_production_boundary_measures_and_rejects_raw_text_fallback() -> None:
    boundary = load("v11_boundary_fallback", V11 / "core_boundary.py")
    audit = load("v11_audit_fallback", V11 / "runtime_audit.py").RuntimeAudit()
    runtime, generated, corpus = fixture_rows()
    malformed = [dict(runtime[0])]
    malformed[0].pop("source_text")
    with pytest.raises(RuntimeError, match="raw-text fallback"):
        boundary.score_real_core(runtime_rows=malformed, generated_rows=generated, corpus_rows=corpus, holdout_id="v11-disposable", raw_text_fallback=audit.deny_raw_text_fallback)
    assert audit.raw_text_fallback_attempts == 1


def test_production_v10_evaluator_hook_measures_missing_runtime_source() -> None:
    evaluator = load("v10_production_evaluator_hook", ROOT / "workspace/audit/20260723-real-conversation-ux-v10/evaluate_real_holdout.py")
    audit = evaluator.RuntimeAudit()
    with pytest.raises(RuntimeError, match="raw-text fallback"):
        evaluator.require_label_free_runtime([{"session_id": "disposable", "registered_terms": []}], audit)
    assert audit.snapshot() == {"canonical_db_access_attempts": 0, "raw_text_fallback_attempts": 1}


def test_production_boundary_rejects_real_core_db_access() -> None:
    boundary = load("v11_boundary_db", V11 / "core_boundary.py")
    audit = load("v11_audit_db", V11 / "runtime_audit.py").RuntimeAudit()
    runtime, generated, corpus = fixture_rows()
    import shared.tools.veil_decision_frames as frames

    def db_attempt(*_args, **_kwargs):
        sqlite3.connect(":memory:")

    with patch.object(frames, "analyze_decision_frames", db_attempt), patch.object(sqlite3, "connect", audit.deny_db_connect):
        with pytest.raises(RuntimeError, match="canonical DB access"):
            boundary.score_real_core(runtime_rows=runtime, generated_rows=generated, corpus_rows=corpus, holdout_id="v11-disposable", raw_text_fallback=audit.deny_raw_text_fallback)
    assert audit.snapshot() == {"canonical_db_access_attempts": 1, "raw_text_fallback_attempts": 0}


def test_production_boundary_surfaces_real_core_post_start_exception() -> None:
    boundary = load("v11_boundary_exception", V11 / "core_boundary.py")
    audit = load("v11_audit_exception", V11 / "runtime_audit.py").RuntimeAudit()
    runtime, generated, corpus = fixture_rows()
    import shared.tools.veil_decision_frames as frames

    def explode(*_args, **_kwargs):
        raise ValueError("disposable post-start core failure")

    with patch.object(frames, "analyze_decision_frames", explode):
        with pytest.raises(ValueError, match="post-start core failure"):
            boundary.score_real_core(runtime_rows=runtime, generated_rows=generated, corpus_rows=corpus, holdout_id="v11-disposable", raw_text_fallback=audit.deny_raw_text_fallback)
    assert audit.snapshot() == {"canonical_db_access_attempts": 0, "raw_text_fallback_attempts": 0}


def test_declared_source_state_change_is_measurable(tmp_path: Path) -> None:
    state = load("v11_source_state", V11 / "source_state.py")
    declared = tmp_path / "declared.py"
    declared.write_text("before\n", encoding="utf-8")
    before = state.compute(ROOT, [V11 / "core_boundary.py", declared])
    declared.write_text("after\n", encoding="utf-8")
    after = state.compute(ROOT, [V11 / "core_boundary.py", declared])
    assert after != before


def test_terminal_runner_records_scored_real_core_result(tmp_path: Path) -> None:
    runner = load("v11_terminal_normal", V11 / "evaluator_runner.py")
    runtime, generated, corpus = fixture_rows()
    probe = tmp_path / "declared.py"; probe.write_text("stable\n", encoding="utf-8")
    result = tmp_path / "results/first-run"
    assert runner.run_once(root=ROOT, holdout_id="v11-disposable", runtime_rows=runtime, generated_rows=generated, corpus_rows=corpus, result_dir=result, inventory=[V11 / "evaluator_runner.py", V11 / "core_boundary.py", probe]) == 0
    terminal = json.loads((result / "result-manifest.json").read_text(encoding="utf-8"))
    assert terminal["status"] == "scored"
    assert all(terminal["gates"].values())


def test_terminal_runner_records_raw_fallback_runtime_error(tmp_path: Path) -> None:
    runner = load("v11_terminal_raw", V11 / "evaluator_runner.py")
    runtime, generated, corpus = fixture_rows()
    malformed = [dict(runtime[0])]; malformed[0].pop("source_text")
    probe = tmp_path / "declared.py"; probe.write_text("stable\n", encoding="utf-8")
    result = tmp_path / "results/first-run"
    assert runner.run_once(root=ROOT, holdout_id="v11-disposable", runtime_rows=malformed, generated_rows=generated, corpus_rows=corpus, result_dir=result, inventory=[V11 / "evaluator_runner.py", V11 / "core_boundary.py", probe]) == 1
    terminal = json.loads((result / "result-manifest.json").read_text(encoding="utf-8"))
    assert terminal["status"] == "runtime-error"
    assert terminal["runtime_access"] == {"canonical_db_access_attempts": 0, "raw_text_fallback_attempts": 1}


def test_terminal_runner_records_source_state_change_as_failed_gate(tmp_path: Path) -> None:
    runner = load("v11_terminal_source", V11 / "evaluator_runner.py")
    runtime, generated, corpus = fixture_rows()
    probe = tmp_path / "declared.py"; probe.write_text("before\n", encoding="utf-8")
    result = tmp_path / "results/first-run"
    assert runner.run_once(root=ROOT, holdout_id="v11-disposable", runtime_rows=runtime, generated_rows=generated, corpus_rows=corpus, result_dir=result, inventory=[V11 / "evaluator_runner.py", V11 / "core_boundary.py", probe], after_runtime_start=lambda: probe.write_text("after\n", encoding="utf-8")) == 1
    terminal = json.loads((result / "result-manifest.json").read_text(encoding="utf-8"))
    assert terminal["status"] == "scored"
    assert terminal["gates"]["source_state_unchanged"] is False
