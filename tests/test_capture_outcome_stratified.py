from __future__ import annotations

import hashlib
import json
from pathlib import Path

from shared.tools.veil_capture_outcomes import analyze_capture_outcomes
from shared.tools.veil_capture_taxonomy import capture_taxonomy_payload
from .test_capture_classifier import _js_capture_runtime, _run_node_script


FIXTURE = Path(__file__).with_name("fixtures") / "veil_capture_outcome_stratified.json"
DEVELOPMENT_CORPUS_SHA256 = "ce886ed91e77950dce5561a465d7c0504ba3d189dfe7ba75692a652c640fbb6d"


def _cases() -> list[dict[str, object]]:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def _assert_expected(case: dict[str, object], actual: dict[str, str], exceptions: set[str], question_count: int) -> None:
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


def test_html_outcomes_pass_development_corpus_and_match_python() -> None:
    cases = _cases()
    inputs = [
        {
            "case_id": case["case_id"],
            "text": case["text"],
            "registered": case["registered"],
        }
        for case in cases
    ]
    script = f"""
const _captureConfig = {json.dumps(capture_taxonomy_payload(), ensure_ascii=False)};
let activeRows = [];
const document = {{ querySelectorAll: (selector) => selector === '#tbody tr' ? activeRows : [] }};
function message(key) {{ return key; }}
{_js_capture_runtime()}
const inputs = {json.dumps(inputs, ensure_ascii=False)};
const output = inputs.map(item => {{
  activeRows = item.registered.map(term => ({{ dataset: {{ termNormalized: term }} }}));
  return {{ case_id: item.case_id, analysis: analyzeCaptureOutcomes(item.text) }};
}});
process.stdout.write(JSON.stringify(output));
"""
    html_by_id = {
        item["case_id"]: item["analysis"]
        for item in json.loads(_run_node_script(script))
    }

    for case in cases:
        html = html_by_id[case["case_id"]]
        html_actual = {item["normalized"]: item["outcome"] for item in html["results"]}
        html_exceptions = {item["normalized"] for item in html["exceptions"]}
        _assert_expected(case, html_actual, html_exceptions, html["summary"]["question_count"])

        python = analyze_capture_outcomes(str(case["text"]), set(case["registered"]))
        python_actual = {item.normalized: item.outcome for item in python.results}
        for term in case["expected"]:
            assert html_actual.get(term) == python_actual.get(term), case["case_id"]
