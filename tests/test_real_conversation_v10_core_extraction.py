from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CORE_PATH = ROOT / "workspace/audit/20260721-independent-semantic-holdout-v4/evaluate_semantic_holdout.py"
FROZEN = ROOT / "workspace/audit/20260721-independent-semantic-holdout-v4/frozen"


def load_core():
    spec = importlib.util.spec_from_file_location("real_v4_scoring_core", CORE_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_prevalidated_scoring_matches_the_preserved_v4_case_results_and_core_gates() -> None:
    core = load_core()
    scored = core.score_prevalidated(
        runtime_rows=core.read_jsonl(FROZEN / "runtime-input.jsonl"),
        generated_rows=core.read_jsonl(FROZEN / "generated-frames.jsonl"),
        corpus_rows=core.read_jsonl(FROZEN / "frozen-corpus.jsonl"),
        holdout_id="20260721-independent-semantic-holdout-v4",
    )
    expected_cases = core.read_jsonl(FROZEN / "results/first-run/case-results.jsonl")
    expected_summary = core.read_json(FROZEN / "results/first-run/summary.json")

    assert scored["case_results"] == expected_cases
    assert set(scored["summary"]["gates"]) == core.CORE_SCORE_GATES
    for gate in core.CORE_SCORE_GATES:
        assert scored["summary"]["gates"][gate] is expected_summary["gates"][gate]
    for field in (
        "holdout_id", "case_count", "exact_case_count", "session_count",
        "validation_error_session_count", "high_impact_false_exclusion_count",
        "question_mismatch_session_count", "unexpected_exception_count",
        "exclusion_precision", "existing_match_precision", "sessions",
    ):
        assert scored["summary"][field] == expected_summary[field]


def test_prevalidated_scoring_rejects_a_corpus_session_not_present_in_runtime() -> None:
    core = load_core()
    runtime = core.read_jsonl(FROZEN / "runtime-input.jsonl")
    generated = core.read_jsonl(FROZEN / "generated-frames.jsonl")
    corpus = core.read_jsonl(FROZEN / "frozen-corpus.jsonl")
    corpus[0] = {**corpus[0], "session_id": "unknown-session"}

    try:
        core.score_prevalidated(runtime_rows=runtime, generated_rows=generated, corpus_rows=corpus, holdout_id="fixture")
    except ValueError as exc:
        assert "unknown session" in str(exc)
    else:
        raise AssertionError("prevalidated scoring accepted a corpus session outside runtime input")
