from __future__ import annotations

import json

from shared.tools.veil_capture_outcomes import analyze_capture_outcomes
from shared.tools.veil_capture_taxonomy import capture_taxonomy_payload
from .test_capture_classifier import _js_capture_runtime, _run_node_script


def _js_analyze(text: str, registered_terms: set[str] | None = None) -> dict[str, object]:
    rows = [{"termNormalized": term} for term in sorted(registered_terms or set())]
    script = f"""
const _captureConfig = {json.dumps(capture_taxonomy_payload(), ensure_ascii=False)};
const registeredRows = {json.dumps(rows, ensure_ascii=False)}.map(dataset => ({{ dataset }}));
const document = {{
  querySelectorAll: (selector) => selector === '#tbody tr' ? registeredRows : []
}};
function message(key) {{ return key; }}
{_js_capture_runtime()}
const result = analyzeCaptureOutcomes({json.dumps(text, ensure_ascii=False)});
process.stdout.write(JSON.stringify(result));
"""
    return json.loads(_run_node_script(script))


def test_html_low_impact_repetition_is_hidden_observation() -> None:
    payload = _js_analyze("root clutter root clutter should be reviewed later.")
    outcomes = {item["normalized"]: item["outcome"] for item in payload["results"]}

    assert payload["contract_version"] == "1"
    assert payload["analysis_mode"] == "raw-text-diagnostic"
    assert payload["diagnostic_only"] is True
    assert payload["write_allowed"] is False
    assert outcomes["root clutter"] == "observe"
    assert payload["summary"]["user_action_required"] is False
    assert payload["summary"]["question_count"] == 0


def test_html_high_impact_definition_is_one_exception() -> None:
    payload = _js_analyze(
        "In this project, release readiness means every required delivery check is green. "
        "Release readiness blocks distribution."
    )

    assert [item["normalized"] for item in payload["exceptions"]] == ["release readiness"]
    assert payload["summary"]["question_count"] == 1


def test_html_multiple_exceptions_are_batched() -> None:
    payload = _js_analyze("Use decision boundary consistently. Always use release boundary.")

    assert {item["normalized"] for item in payload["exceptions"]} == {
        "decision boundary",
        "release boundary",
    }
    assert payload["summary"]["question_count"] == 1


def test_html_explicit_quoted_and_phrase_requests_are_exceptions() -> None:
    quoted = _js_analyze('Use "decision boundary" consistently.')
    phrase = _js_analyze("Use the phrase decision boundary consistently.")

    assert [item["normalized"] for item in quoted["exceptions"]] == ["decision boundary"]
    assert [item["normalized"] for item in phrase["exceptions"]] == ["decision boundary"]


def test_html_registered_change_overrides_existing_match() -> None:
    payload = _js_analyze("Change current state to present condition.", {"current state"})

    assert [item["normalized"] for item in payload["exceptions"]] == ["current state"]
    assert payload["exceptions"][0]["requested_preferred"] == "present condition"


def test_html_registration_mapping_overrides_existing_match() -> None:
    payload = _js_analyze("Register current state as present state in VEIL.", {"current state"})

    assert [item["normalized"] for item in payload["exceptions"]] == ["current state"]
    assert payload["exceptions"][0]["requested_preferred"] == "present state"


def test_html_japanese_change_and_registration_mappings_are_exceptions() -> None:
    change = _js_analyze("「現在状態」を「現状」に変更する。", {"現在状態"})
    registration = _js_analyze(
        "「current state」を「present state」として登録する。",
        {"current state"},
    )

    assert change["exceptions"][0]["requested_preferred"] == "現状"
    assert registration["exceptions"][0]["requested_preferred"] == "present state"


def test_html_registered_request_is_existing_match_without_question() -> None:
    payload = _js_analyze("Use current state consistently in every handoff.", {"current state"})
    outcomes = {item["normalized"]: item["outcome"] for item in payload["results"]}

    assert outcomes["current state"] == "existing-match"
    assert payload["summary"]["user_action_required"] is False


def test_html_and_python_match_on_decision_terms() -> None:
    cases = [
        ("root clutter root clutter should be reviewed later.", set(), {"root clutter"}),
        ("Use decision boundary consistently in every handoff.", set(), {"decision boundary"}),
        (
            "In this project, release readiness means every required delivery check is green.",
            set(),
            {"release readiness"},
        ),
        ("Use current state consistently in every handoff.", {"current state"}, {"current state"}),
        ("今後は判断境界を一貫して使う。", set(), {"判断境界"}),
        ("判断境界を一貫して使う。", {"判断境界"}, {"判断境界"}),
        ("配布境界とは、配布を阻止する条件を意味する。", set(), {"配布境界"}),
        ('Use "decision boundary" consistently.', set(), {"decision boundary"}),
        ("Use the phrase decision boundary consistently.", set(), {"decision boundary"}),
        ("Change current state to present condition.", {"current state"}, {"current state"}),
        ("Register current state as present state in VEIL.", {"current state"}, {"current state"}),
        ("Also register rollback window for the allowed reversal period.", set(), {"rollback window"}),
        ('Register "green lane" as the approved path name.', set(), {"green lane"}),
        (
            'Use the phrase "no automatic write" as the durable safety rule and save it.',
            set(),
            {"no automatic write"},
        ),
        (
            "Change the preferred wording from pull request to change request.",
            {"pull request"},
            {"pull request"},
        ),
        (
            "Use deployment window everywhere. Later in the same decision, use release window as the preferred form instead.",
            {"deployment window"},
            {"deployment window", "release window"},
        ),
        (
            "「削除可能」は使わず、今後は「削除承認済み」を正式な表記に変更します。",
            {"削除可能"},
            {"削除可能"},
        ),
        (
            "Production ready means all destructive paths have rollback evidence and an owner.",
            set(),
            {"production ready"},
        ),
        ("For this workshop, a snack pause means any break under ten minutes.", set(), {"snack pause"}),
        ("The deployment lane stayed green in both weekly reports.", set(), {"deployment lane"}),
        ("二週続けて配布経路を青い経路と呼んでいます。", set(), {"青い経路"}),
        ("Three monthly notes describe the shared queue as the handoff shelf.", set(), {"handoff shelf"}),
        ("月次メモの三回で、共同確認の置き場を「確認棚」と説明しています。", set(), {"確認棚"}),
        ("今回の工作教室に限り、机上整理は借りた色紙を箱へ戻すことを指します。", set(), {"机上整理"}),
        ("Nakamura will review the draft on Friday.", set(), {"nakamura"}),
    ]
    for text, registered, decision_terms in cases:
        python_results = {
            item.normalized: item.outcome
            for item in analyze_capture_outcomes(text, registered).results
            if item.normalized in decision_terms
        }
        html_payload = _js_analyze(text, registered)
        html_results = {
            item["normalized"]: item["outcome"]
            for item in html_payload["results"]
            if item["normalized"] in decision_terms
        }

        assert html_results == python_results


def test_html_and_python_match_exact_exception_sets_for_natural_intent_variants() -> None:
    cases = [
        ("Also register rollback window for the allowed reversal period.", set()),
        ('Please also save the quoted wording "red lane" for the rejected path.', set()),
        ('Please register the phrase "source of truth" for the single authoritative store.', set()),
        ('Use the phrase "no automatic write" as the durable safety rule and save it.', set()),
        ("判断の永続記録は「判断記録」という名称で登録してください。", set()),
        ("戻せる期間は「ロールバック期間」として登録してください。", set()),
        ("Replace allowlist with approved list in the registered vocabulary.", {"allowlist"}),
        (
            "標準名は「除外リスト」にします。ただし同じ決定文で「ブロックリスト」を優先すると書かれています。",
            {"除外リスト"},
        ),
        ("この勉強会では、短い休憩を五分以内の中断と呼びます。", set()),
    ]

    for text, registered in cases:
        python = analyze_capture_outcomes(text, registered)
        html = _js_analyze(text, registered)
        assert {item["normalized"] for item in html["exceptions"]} == {
            item.normalized for item in python.exceptions
        }, text
        assert html["summary"]["question_count"] == python.question_count, text


def test_html_and_python_match_complete_quoted_inventory_exception_sets() -> None:
    cases = (
        'The complete durable inventory is two terms: register the phrase "evidence hinge" '
        'for the proof link, and save the quoted phrase "consent marker" for authorization.',
        'The competing durable forms are exactly "pilot ring" and "trial ring": the first '
        'instruction prefers pilot ring, while a later instruction prefers trial ring.',
        'Exactly two durable definitions are intended: "custody breach" means loss of control, '
        'and "release embargo" means distribution is prohibited.',
        '永続的な定義は二つだけです。「本人確認失敗」は本人性を証明できない状態を意味し、'
        '「緊急停止権限」は処理を止められる権限を意味します。',
    )

    for text in cases:
        python = analyze_capture_outcomes(text)
        html = _js_analyze(text)
        assert {item["normalized"] for item in html["exceptions"]} == {
            item.normalized for item in python.exceptions
        }, text
        assert html["summary"]["question_count"] == 1, text
