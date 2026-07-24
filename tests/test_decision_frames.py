from __future__ import annotations

import pytest

from shared.tools.veil_decision_frames import (
    BLIND_GENERATED_ROW_FIELDS,
    FrameValidationError,
    analyze_decision_frames,
    build_blind_generated_row,
)


def _evidence(text: str, occurrence: int = 1) -> dict[str, object]:
    return {"text": text, "occurrence": occurrence}


def _frame(
    frame_id: str,
    term: str,
    evidence: str,
    *,
    intent: str = "adopt",
    persistence: str = "durable",
    polarity: str = "affirmed",
    scope: str = "project",
    from_term: str | None = None,
    preferred: str | None = None,
    conflict_group: str | None = None,
    impact: str = "medium",
    confidence: str = "high",
) -> dict[str, object]:
    return {
        "frame_id": frame_id,
        "term": term,
        "intent": intent,
        "persistence": persistence,
        "polarity": polarity,
        "scope": scope,
        "from_term": from_term,
        "preferred": preferred,
        "conflict_group": conflict_group,
        "impact": impact,
        "term_evidence": _evidence(evidence),
        "intent_evidence": [_evidence(evidence)],
        "confidence": confidence,
    }


def _payload(
    frames: list[dict[str, object]],
    *,
    confirmed: list[str] | None = None,
    rejected: list[str] | None = None,
    unresolved: list[str] | None = None,
    missing: list[dict[str, object]] | None = None,
) -> dict[str, object]:
    unresolved = unresolved or []
    missing = missing or []
    return {
        "contract_version": "2",
        "frames": frames,
        "critic": {
            "status": "needs-review" if unresolved or missing else "confirmed",
            "confirmed_frame_ids": confirmed or [],
            "rejected_frame_ids": rejected or [],
            "unresolved_frame_ids": unresolved,
            "missing_frames": missing,
        },
    }


def test_blind_generator_envelope_is_public_and_exact() -> None:
    payload = _payload([])

    assert BLIND_GENERATED_ROW_FIELDS == frozenset({"session_id", "payload"})
    assert build_blind_generated_row("session-1", payload) == {
        "session_id": "session-1",
        "payload": payload,
    }
    with pytest.raises(ValueError, match="session_id"):
        build_blind_generated_row("", payload)
    with pytest.raises(ValueError, match="payload"):
        build_blind_generated_row("session-1", [])


def test_no_frames_and_no_registered_match_requires_no_action() -> None:
    text = "The person's authentication factor, and its age, were logged."
    analysis = analyze_decision_frames(text, _payload([]))

    assert analysis.results == ()
    assert analysis.question_count == 0
    assert analysis.to_dict()["write_allowed"] is False


def test_exact_registered_match_without_frame_is_automatic() -> None:
    analysis = analyze_decision_frames(
        "The current state is shown in the report.",
        _payload([]),
        {"current state"},
    )

    assert [(item.normalized, item.outcome) for item in analysis.results] == [
        ("current state", "existing-match")
    ]
    assert analysis.question_count == 0


def test_affirmed_durable_adoption_is_one_exception() -> None:
    text = "Use origin seal for every project handoff."
    frame = _frame("f1", "origin seal", text, intent="adopt", scope="project")
    analysis = analyze_decision_frames(text, _payload([frame], confirmed=["f1"]))

    assert [item.outcome for item in analysis.results] == ["exception"]
    assert analysis.question_count == 1


def test_negated_adoption_is_silently_excluded() -> None:
    text = 'Never save "crystal staircase" in VEIL.'
    frame = _frame(
        "f1",
        "crystal staircase",
        text,
        intent="adopt",
        polarity="negated",
        persistence="none",
    )
    analysis = analyze_decision_frames(text, _payload([frame], confirmed=["f1"]))

    assert [item.outcome for item in analysis.results] == ["exclude"]
    assert analysis.question_count == 0


def test_temporary_one_off_definition_is_observed() -> None:
    text = "For this one exercise, arrival pocket means the check-in table."
    frame = _frame(
        "f1",
        "arrival pocket",
        text,
        intent="define",
        persistence="temporary",
        scope="one-off",
        impact="low",
    )
    analysis = analyze_decision_frames(text, _payload([frame], confirmed=["f1"]))

    assert [item.outcome for item in analysis.results] == ["observe"]
    assert analysis.question_count == 0


def test_rename_preserves_mapping_and_does_not_resolve_as_existing_match() -> None:
    text = "Rename current state to present state for future reports."
    frame = _frame(
        "f1",
        "current state",
        text,
        intent="rename",
        from_term="current state",
        preferred="present state",
    )
    analysis = analyze_decision_frames(
        text,
        _payload([frame], confirmed=["f1"]),
        {"current state"},
    )

    assert len(analysis.exceptions) == 1
    assert analysis.exceptions[0].requested_preferred == "present state"
    assert analysis.exceptions[0].registered is True


def test_conflicting_forms_are_batched_into_one_question() -> None:
    text = "Use canary cohort or preview cohort; the durable label remains unresolved."
    frames = [
        _frame(
            "f1",
            "canary cohort",
            text,
            intent="conflict",
            conflict_group="cohort-label",
            impact="high",
        ),
        _frame(
            "f2",
            "preview cohort",
            text,
            intent="conflict",
            conflict_group="cohort-label",
            impact="high",
        ),
    ]
    analysis = analyze_decision_frames(text, _payload(frames, confirmed=["f1", "f2"]))

    assert len(analysis.exceptions) == 2
    assert analysis.question_count == 1
    assert {item.conflict_group for item in analysis.exceptions} == {"cohort-label"}


def test_confirmed_critic_can_reject_a_spurious_extractor_frame() -> None:
    text = "Record elapsed probe time in quota_probe_ms."
    frame = _frame(
        "f1",
        "quota_probe_ms",
        text,
        intent="mention",
        persistence="none",
        scope="one-off",
        impact="low",
    )
    analysis = analyze_decision_frames(text, _payload([frame], rejected=["f1"]))

    assert analysis.critic_status == "confirmed"
    assert [item.reason for item in analysis.results] == ["critic_rejected_spurious_frame"]
    assert analysis.question_count == 0


def test_material_critic_disagreement_forces_one_exception() -> None:
    text = "Use service bulletin in future reports."
    frame = _frame("f1", "service bulletin", text, intent="adopt")
    analysis = analyze_decision_frames(text, _payload([frame], unresolved=["f1"]))

    assert analysis.critic_status == "needs-review"
    assert [item.reason for item in analysis.exceptions] == ["extractor_critic_disagreement"]
    assert analysis.question_count == 1


def test_critic_missing_frame_is_validated_and_forced_to_exception() -> None:
    text = "Distribution lock controls every release."
    missing = _frame(
        "m1",
        "Distribution lock",
        text,
        intent="define",
        impact="high",
    )
    analysis = analyze_decision_frames(text, _payload([], missing=[missing]))

    assert analysis.validated_frame_count == 1
    assert [item.reason for item in analysis.exceptions] == ["extractor_critic_disagreement"]


@pytest.mark.parametrize(
    ("payload_edit", "message"),
    [
        (lambda payload: payload.update({"unexpected": True}), "payload.unexpected is not allowed"),
        (
            lambda payload: payload["frames"][0].update({"term_evidence": _evidence("not present")}),
            "does not exist in the exact input text",
        ),
        (
            lambda payload: payload["critic"].update({"confirmed_frame_ids": []}),
            "critic must classify every frame_id exactly once",
        ),
    ],
)
def test_invalid_untrusted_payload_is_rejected(payload_edit, message: str) -> None:
    text = "Use origin seal for every project handoff."
    frame = _frame("f1", "origin seal", text)
    payload = _payload([frame], confirmed=["f1"])
    payload_edit(payload)

    with pytest.raises(FrameValidationError, match=message):
        analyze_decision_frames(text, payload)


def test_rename_term_must_be_the_from_term() -> None:
    text = "Rename current state to present state."
    frame = _frame(
        "f1",
        "present state",
        text,
        intent="rename",
        from_term="current state",
        preferred="present state",
    )

    with pytest.raises(FrameValidationError, match="same wording as from_term"):
        analyze_decision_frames(text, _payload([frame], confirmed=["f1"]))
