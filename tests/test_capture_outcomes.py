from __future__ import annotations

from shared.tools.veil_capture_outcomes import (
    CONTRACT_VERSION,
    OUTCOME_EXCEPTION,
    OUTCOME_EXISTING_MATCH,
    OUTCOME_OBSERVE,
    analyze_capture_outcomes,
    extract_context_signals,
)


def _outcomes(text: str, registered_terms: set[str] | None = None) -> dict[str, str]:
    analysis = analyze_capture_outcomes(text, registered_terms)
    return {item.normalized: item.outcome for item in analysis.results}


def test_low_impact_repetition_stays_in_background() -> None:
    analysis = analyze_capture_outcomes("root clutter root clutter should be reviewed later.")

    assert _outcomes("root clutter root clutter should be reviewed later.")["root clutter"] == OUTCOME_OBSERVE
    assert analysis.user_action_required is False
    assert analysis.question_count == 0


def test_explicit_consistency_request_is_one_exception() -> None:
    analysis = analyze_capture_outcomes(
        "Use decision boundary consistently in every handoff. The decision boundary controls external writes."
    )

    assert [item.normalized for item in analysis.exceptions] == ["decision boundary"]
    assert analysis.exceptions[0].outcome == OUTCOME_EXCEPTION
    assert analysis.exceptions[0].impact == "high"
    assert analysis.question_count == 1


def test_quoted_english_consistency_request_is_exception() -> None:
    analysis = analyze_capture_outcomes('Use "decision boundary" consistently.')

    assert [item.normalized for item in analysis.exceptions] == ["decision boundary"]
    assert analysis.question_count == 1


def test_the_phrase_consistency_request_is_exception() -> None:
    analysis = analyze_capture_outcomes("Use the phrase decision boundary consistently.")

    assert [item.normalized for item in analysis.exceptions] == ["decision boundary"]


def test_registered_term_change_request_overrides_existing_match() -> None:
    analysis = analyze_capture_outcomes(
        "Change current state to present condition.",
        {"current state"},
    )

    assert [item.normalized for item in analysis.exceptions] == ["current state"]
    assert analysis.exceptions[0].signal == "change_request"
    assert analysis.exceptions[0].requested_preferred == "present condition"


def test_registered_term_registration_mapping_overrides_existing_match() -> None:
    analysis = analyze_capture_outcomes(
        "Register current state as present state in VEIL.",
        {"current state"},
    )

    assert [item.normalized for item in analysis.exceptions] == ["current state"]
    assert analysis.exceptions[0].signal == "registration_request"
    assert analysis.exceptions[0].requested_preferred == "present state"


def test_existing_term_continuation_stays_existing_match() -> None:
    analysis = analyze_capture_outcomes(
        "Use current state consistently.",
        {"current state"},
    )

    assert analysis.exceptions == ()
    assert _outcomes("Use current state consistently.", {"current state"})["current state"] == OUTCOME_EXISTING_MATCH


def test_explicit_conflict_request_is_exception() -> None:
    analysis = analyze_capture_outcomes(
        "Use present condition instead of current state.",
        {"current state"},
    )

    assert [item.normalized for item in analysis.exceptions] == ["current state"]
    assert analysis.exceptions[0].reason == "explicit_conflict_request"
    assert analysis.exceptions[0].requested_preferred == "present condition"


def test_japanese_unquoted_change_request_is_exception() -> None:
    analysis = analyze_capture_outcomes(
        "current state を present condition に変更する。",
        {"current state"},
    )

    assert [item.normalized for item in analysis.exceptions] == ["current state"]
    assert analysis.exceptions[0].requested_preferred == "present condition"


def test_japanese_quoted_change_request_is_exception() -> None:
    analysis = analyze_capture_outcomes(
        "「現在状態」を「現状」に変更する。",
        {"現在状態"},
    )

    assert [item.normalized for item in analysis.exceptions] == ["現在状態"]
    assert analysis.exceptions[0].requested_preferred == "現状"


def test_japanese_quoted_registration_mapping_is_exception() -> None:
    analysis = analyze_capture_outcomes(
        "「current state」を「present state」として登録する。",
        {"current state"},
    )

    assert [item.normalized for item in analysis.exceptions] == ["current state"]
    assert analysis.exceptions[0].requested_preferred == "present state"


def test_high_impact_local_definition_is_exception() -> None:
    analysis = analyze_capture_outcomes(
        "In this project, release readiness means every required delivery check is green. "
        "Release readiness blocks distribution."
    )

    assert [item.normalized for item in analysis.exceptions] == ["release readiness"]
    assert analysis.exceptions[0].impact == "high"


def test_medium_impact_definition_is_observed_without_question() -> None:
    outcomes = _outcomes("Draft warmth means a slightly friendlier first sentence.")

    assert outcomes["draft warmth"] == OUTCOME_OBSERVE


def test_registered_explicit_request_is_resolved_automatically() -> None:
    analysis = analyze_capture_outcomes(
        "Use current state consistently in every handoff.",
        {"current state"},
    )

    assert _outcomes("Use current state consistently in every handoff.", {"current state"})["current state"] == OUTCOME_EXISTING_MATCH
    assert analysis.user_action_required is False
    assert analysis.question_count == 0


def test_multiple_exceptions_are_batched_into_one_question() -> None:
    analysis = analyze_capture_outcomes(
        "Use decision boundary consistently. Always use release boundary."
    )

    assert {item.normalized for item in analysis.exceptions} == {"decision boundary", "release boundary"}
    assert analysis.question_count == 1


def test_japanese_consistency_request_with_english_term_is_detected() -> None:
    signals = extract_context_signals("decision boundary を一貫して使う。")

    assert [(item.normalized, item.kind) for item in signals] == [
        ("decision boundary", "consistency_request")
    ]


def test_quoted_japanese_consistency_request_is_detected() -> None:
    signals = extract_context_signals("「判断境界」という呼称に統一する。")

    assert signals[0].normalized == "判断境界"
    assert signals[0].kind == "consistency_request"


def test_unquoted_japanese_consistency_request_is_detected() -> None:
    analysis = analyze_capture_outcomes("今後は判断境界を一貫して使う。")

    assert [item.normalized for item in analysis.exceptions] == ["判断境界"]
    assert analysis.question_count == 1


def test_unquoted_japanese_registered_term_is_resolved_automatically() -> None:
    analysis = analyze_capture_outcomes("判断境界を一貫して使う。", {"判断境界"})

    assert analysis.exceptions == ()
    assert _outcomes("判断境界を一貫して使う。", {"判断境界"})["判断境界"] == OUTCOME_EXISTING_MATCH


def test_japanese_high_impact_definition_is_exception() -> None:
    analysis = analyze_capture_outcomes("配布境界とは、配布を阻止する条件を意味する。")

    assert [item.normalized for item in analysis.exceptions] == ["配布境界"]


def test_japanese_rejected_proposal_requires_no_action() -> None:
    analysis = analyze_capture_outcomes("「判断境界」を一貫して使うという提案は却下した。")

    assert analysis.user_action_required is False
    assert analysis.question_count == 0


def test_identifier_and_industry_noise_requires_no_action() -> None:
    analysis = analyze_capture_outcomes(
        "README.md --html-path config_key migration workflow database schema"
    )

    assert analysis.user_action_required is False
    assert analysis.question_count == 0


def test_payload_exposes_stable_summary_contract() -> None:
    payload = analyze_capture_outcomes("Use decision boundary consistently.").to_dict()

    assert payload["contract_version"] == CONTRACT_VERSION
    assert payload["summary"]["user_action_required"] is True
    assert payload["summary"]["question_count"] == 1
    assert payload["summary"]["counts"][OUTCOME_EXCEPTION] == 1
    assert payload["exceptions"][0]["normalized"] == "decision boundary"


def test_registration_intent_variants_preserve_the_requested_term() -> None:
    cases = {
        "Also register rollback window for the allowed reversal period.": "rollback window",
        'Register "green lane" as the approved path name.': "green lane",
        'Please also save the quoted wording "red lane" for the rejected path.': "red lane",
        'Please register the phrase "source of truth" for the single authoritative store.': "source of truth",
        'Use the phrase "no automatic write" as the durable safety rule and save it.': "no automatic write",
        "判断の永続記録は「判断記録」という名称で登録してください。": "判断記録",
        "戻せる期間は「ロールバック期間」として登録してください。": "ロールバック期間",
        "「復旧窓口」も利用者が回復操作を始める場所の名称として保存してください。": "復旧窓口",
    }

    for text, expected in cases.items():
        analysis = analyze_capture_outcomes(text)
        assert {item.normalized for item in analysis.exceptions} == {expected}, text
        assert analysis.question_count == 1, text


def test_change_and_conflict_variants_override_registered_matches() -> None:
    preferred_change = analyze_capture_outcomes(
        "Change the preferred wording from pull request to change request.",
        {"pull request"},
    )
    vocabulary_change = analyze_capture_outcomes(
        "Replace allowlist with approved list in the registered vocabulary.",
        {"allowlist"},
    )
    later_preference = analyze_capture_outcomes(
        "Use deployment window everywhere. Later in the same decision, use release window as the preferred form instead.",
        {"deployment window"},
    )
    japanese_conflict = analyze_capture_outcomes(
        "標準名は「除外リスト」にします。ただし同じ決定文で「ブロックリスト」を優先すると書かれています。",
        {"除外リスト"},
    )
    japanese_change = analyze_capture_outcomes(
        "「削除可能」は使わず、今後は「削除承認済み」を正式な表記に変更します。",
        {"削除可能"},
    )

    assert preferred_change.exceptions[0].normalized == "pull request"
    assert preferred_change.exceptions[0].requested_preferred == "change request"
    assert vocabulary_change.exceptions[0].normalized == "allowlist"
    assert vocabulary_change.exceptions[0].requested_preferred == "approved list"
    assert "release window" in {item.normalized for item in later_preference.exceptions}
    assert "ブロックリスト" in {item.normalized for item in japanese_conflict.exceptions}
    assert japanese_change.exceptions[0].normalized == "削除可能"
    assert japanese_change.exceptions[0].requested_preferred == "削除承認済み"
    assert all(item.question_count == 1 for item in (
        preferred_change,
        vocabulary_change,
        later_preference,
        japanese_conflict,
        japanese_change,
    ))


def test_definition_impact_and_descriptive_repetition_have_distinct_outcomes() -> None:
    production = analyze_capture_outcomes(
        "Production ready means all destructive paths have rollback evidence and an owner."
    )
    deletion = analyze_capture_outcomes(
        "A deletion authority means the named person or role allowed to approve irreversible removal."
    )
    workshop = analyze_capture_outcomes(
        "For this workshop, a snack pause means any break under ten minutes."
    )
    japanese_workshop = analyze_capture_outcomes(
        "この勉強会では、短い休憩を五分以内の中断と呼びます。"
    )
    repeated = analyze_capture_outcomes(
        "The deployment lane stayed green in both weekly reports."
    )
    japanese_repeated = analyze_capture_outcomes(
        "二週続けて配布経路を青い経路と呼んでいます。"
    )

    assert _outcomes("Production ready means all destructive paths have rollback evidence and an owner.")["production ready"] == OUTCOME_EXCEPTION
    assert _outcomes("A deletion authority means the named person or role allowed to approve irreversible removal.")["deletion authority"] == OUTCOME_EXCEPTION
    assert _outcomes("For this workshop, a snack pause means any break under ten minutes.")["snack pause"] == OUTCOME_OBSERVE
    assert _outcomes("この勉強会では、短い休憩を五分以内の中断と呼びます。")["短い休憩"] == OUTCOME_OBSERVE
    assert _outcomes("The deployment lane stayed green in both weekly reports.")["deployment lane"] == OUTCOME_OBSERVE
    assert _outcomes("二週続けて配布経路を青い経路と呼んでいます。")["青い経路"] == OUTCOME_OBSERVE
    assert production.question_count == deletion.question_count == 1
    assert workshop.question_count == japanese_workshop.question_count == 0
    assert repeated.question_count == japanese_repeated.question_count == 0


def test_capitalized_person_subject_is_silent_non_target() -> None:
    analysis = analyze_capture_outcomes("Nakamura will review the draft on Friday.")

    assert _outcomes("Nakamura will review the draft on Friday.")["nakamura"] == "exclude"
    assert analysis.question_count == 0


def test_complete_quoted_inventories_bind_intent_to_each_term() -> None:
    cases = (
        (
            'The complete durable inventory is two terms: register the phrase "evidence hinge" '
            'for the proof link, and save the quoted phrase "consent marker" for authorization.',
            {"evidence hinge", "consent marker"},
        ),
        (
            'The competing durable forms are exactly "pilot ring" and "trial ring": the first '
            'instruction prefers pilot ring, while a later instruction prefers trial ring.',
            {"pilot ring", "trial ring"},
        ),
        (
            'Exactly two durable definitions are intended: "custody breach" means loss of control, '
            'and "release embargo" means distribution is prohibited.',
            {"custody breach", "release embargo"},
        ),
        (
            '永続的な定義は二つだけです。「本人確認失敗」は本人性を証明できない状態を意味し、'
            '「緊急停止権限」は処理を止められる権限を意味します。',
            {"本人確認失敗", "緊急停止権限"},
        ),
    )

    for text, expected in cases:
        analysis = analyze_capture_outcomes(text)
        assert {item.normalized for item in analysis.exceptions} == expected, text
        assert analysis.question_count == 1, text


def test_quoted_meta_labels_are_not_terms() -> None:
    analysis = analyze_capture_outcomes(
        'Save the quoted phrase "consent marker" for the authorization signal.'
    )

    assert {item.normalized for item in analysis.exceptions} == {"consent marker"}


def test_repeated_description_and_temporary_definition_stay_background_only() -> None:
    cases = (
        ("Three monthly notes describe the shared queue as the handoff shelf.", "handoff shelf"),
        ("月次メモの三回で、共同確認の置き場を「確認棚」と説明しています。", "確認棚"),
        ("今回の工作教室に限り、机上整理は借りた色紙を箱へ戻すことを指します。", "机上整理"),
    )

    for text, term in cases:
        analysis = analyze_capture_outcomes(text)
        assert _outcomes(text)[term] == OUTCOME_OBSERVE, text
        assert analysis.question_count == 0, text
