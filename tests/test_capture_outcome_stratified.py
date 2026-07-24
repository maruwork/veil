from __future__ import annotations

import hashlib
import json
from pathlib import Path

from shared.tools.veil_capture_outcomes import analyze_capture_outcomes


FIXTURE = Path(__file__).with_name("fixtures") / "veil_capture_outcome_stratified.json"
DEVELOPMENT_CORPUS_SHA256 = "ce886ed91e77950dce5561a465d7c0504ba3d189dfe7ba75692a652c640fbb6d"


def _cases() -> list[dict[str, object]]:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def _assert_expected(
    case: dict[str, object],
    actual: dict[str, str],
    exceptions: set[str],
    question_count: int,
) -> None:
    expected = dict(case["expected"])
    expected_exceptions = {term for term, outcome in expected.items() if outcome == "exception"}
    assert {term: actual.get(term) for term in expected} == expected, case["case_id"]
    assert exceptions == expected_exceptions, case["case_id"]
    assert question_count == (1 if expected_exceptions else 0), case["case_id"]


def test_development_corpus_is_locked_at_100_cases() -> None:
    cases = _cases()
    digest = hashlib.sha256(
        json.dumps(cases, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()

    assert len(cases) == 100
    assert digest == DEVELOPMENT_CORPUS_SHA256


def test_python_outcomes_pass_development_corpus() -> None:
    for case in _cases():
        analysis = analyze_capture_outcomes(str(case["text"]), set(case["registered"]))
        actual = {item.normalized: item.outcome for item in analysis.results}
        exceptions = {item.normalized for item in analysis.exceptions}

        _assert_expected(case, actual, exceptions, analysis.question_count)
