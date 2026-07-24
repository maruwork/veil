"""Validate AI-authored decision frames and apply VEIL's local no-write policy.

This module intentionally does not infer semantic intent from raw text.  The
host AI supplies evidence-backed frames and a critic result; local VEIL treats
that payload as untrusted data, validates it against the exact source text,
then applies a deterministic outcome policy.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import re
from typing import Any, Iterable

from shared.tools.veil_capture_outcomes import extract_registered_matches
from shared.tools.veil_rule_store import normalize_term


CONTRACT_VERSION = "2"
OUTCOMES = ("exclude", "observe", "existing-match", "exception")
INTENTS = {"mention", "adopt", "rename", "define", "conflict"}
PERSISTENCE_VALUES = {"none", "temporary", "durable", "unclear"}
POLARITY_VALUES = {"affirmed", "negated", "reported"}
SCOPE_VALUES = {"one-off", "session", "project", "global", "unclear"}
IMPACT_VALUES = {"low", "medium", "high"}
CONFIDENCE_VALUES = {"low", "medium", "high"}
CRITIC_STATUS_VALUES = {"confirmed", "needs-review"}
PAYLOAD_FIELDS = {"contract_version", "frames", "critic"}
BLIND_GENERATED_ROW_FIELDS = frozenset({"session_id", "payload"})
BLIND_GENERATOR_JSONL_CONTRACT = (
    "For each runtime-input JSONL row, write exactly one JSON object with only "
    "session_id (copied verbatim from that input row) and payload (the contract-v2 "
    "semantic-frame payload). Do not add fields."
)
FRAME_FIELDS = {
    "frame_id",
    "term",
    "intent",
    "persistence",
    "polarity",
    "scope",
    "from_term",
    "preferred",
    "conflict_group",
    "impact",
    "term_evidence",
    "intent_evidence",
    "confidence",
}
EVIDENCE_FIELDS = {"text", "occurrence"}
CRITIC_FIELDS = {
    "status",
    "confirmed_frame_ids",
    "rejected_frame_ids",
    "unresolved_frame_ids",
    "missing_frames",
}


def build_blind_generated_row(session_id: str, payload: Any) -> dict[str, Any]:
    """Build the public JSONL envelope for a blind semantic-frame generator.

    ``session_id`` must be copied verbatim from one runtime-input row. ``payload``
    is validated later against that row's source text, so this helper enforces only
    the shared outer contract used by blind generators and evaluators.
    """
    if not isinstance(session_id, str) or not session_id:
        raise ValueError("session_id must be a non-empty string")
    if not isinstance(payload, dict):
        raise ValueError("payload must be an object")
    return {"session_id": session_id, "payload": payload}


class FrameValidationError(ValueError):
    def __init__(self, errors: Iterable[str]):
        self.errors = tuple(errors)
        super().__init__("; ".join(self.errors))


@dataclass(frozen=True)
class EvidenceRef:
    text: str
    occurrence: int


@dataclass(frozen=True)
class DecisionFrame:
    frame_id: str
    term: str
    normalized: str
    intent: str
    persistence: str
    polarity: str
    scope: str
    from_term: str | None
    preferred: str | None
    conflict_group: str | None
    impact: str
    term_evidence: EvidenceRef
    intent_evidence: tuple[EvidenceRef, ...]
    confidence: str


@dataclass(frozen=True)
class FrameOutcome:
    frame_id: str | None
    term: str
    normalized: str
    outcome: str
    reason: str
    impact: str
    registered: bool
    intent: str | None
    persistence: str | None
    polarity: str | None
    scope: str | None
    requested_preferred: str | None = None
    conflict_group: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class SemanticFrameAnalysis:
    results: tuple[FrameOutcome, ...]
    critic_status: str
    validated_frame_count: int

    @property
    def exceptions(self) -> tuple[FrameOutcome, ...]:
        return tuple(item for item in self.results if item.outcome == "exception")

    @property
    def user_action_required(self) -> bool:
        return bool(self.exceptions)

    @property
    def question_count(self) -> int:
        return 1 if self.user_action_required else 0

    def to_dict(self) -> dict[str, Any]:
        counts = {outcome: 0 for outcome in OUTCOMES}
        for item in self.results:
            counts[item.outcome] += 1
        return {
            "contract_version": CONTRACT_VERSION,
            "analysis_mode": "semantic-frames",
            "diagnostic_only": False,
            "write_allowed": False,
            "status": "ok",
            "summary": {
                "user_action_required": self.user_action_required,
                "question_count": self.question_count,
                "counts": counts,
                "automatic_processed": (
                    counts["exclude"] + counts["observe"] + counts["existing-match"]
                ),
                "validated_frame_count": self.validated_frame_count,
                "critic_status": self.critic_status,
            },
            "exceptions": [item.to_dict() for item in self.exceptions],
            "results": [item.to_dict() for item in self.results],
        }


def _require_string(
    value: Any,
    *,
    field: str,
    errors: list[str],
    allow_none: bool = False,
) -> str | None:
    if value is None and allow_none:
        return None
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{field} must be a non-empty string")
        return None
    return value.strip()


def _require_enum(
    value: Any,
    allowed: set[str],
    *,
    field: str,
    errors: list[str],
) -> str:
    if not isinstance(value, str) or value not in allowed:
        errors.append(f"{field} must be one of {sorted(allowed)}")
        return ""
    return value


def _reject_unknown_fields(
    value: dict[str, Any],
    allowed: set[str],
    *,
    field: str,
    errors: list[str],
) -> None:
    for name in sorted(set(value) - allowed):
        errors.append(f"{field}.{name} is not allowed")


def _parse_evidence(value: Any, *, field: str, errors: list[str]) -> EvidenceRef | None:
    if not isinstance(value, dict):
        errors.append(f"{field} must be an object")
        return None
    _reject_unknown_fields(value, EVIDENCE_FIELDS, field=field, errors=errors)
    text = _require_string(value.get("text"), field=f"{field}.text", errors=errors)
    occurrence = value.get("occurrence")
    if not isinstance(occurrence, int) or isinstance(occurrence, bool) or occurrence < 1:
        errors.append(f"{field}.occurrence must be a positive integer")
        occurrence = 1
    if text is None:
        return None
    return EvidenceRef(text=text, occurrence=occurrence)


def _resolve_evidence(source: str, evidence: EvidenceRef, *, field: str, errors: list[str]) -> None:
    starts = [match.start() for match in re.finditer(re.escape(evidence.text), source)]
    if len(starts) < evidence.occurrence:
        errors.append(
            f"{field} occurrence {evidence.occurrence} does not exist in the exact input text"
        )


def _parse_frame(value: Any, *, field: str, source: str, errors: list[str]) -> DecisionFrame | None:
    if not isinstance(value, dict):
        errors.append(f"{field} must be an object")
        return None
    _reject_unknown_fields(value, FRAME_FIELDS, field=field, errors=errors)
    frame_id = _require_string(value.get("frame_id"), field=f"{field}.frame_id", errors=errors)
    term = _require_string(value.get("term"), field=f"{field}.term", errors=errors)
    intent = _require_enum(value.get("intent"), INTENTS, field=f"{field}.intent", errors=errors)
    persistence = _require_enum(
        value.get("persistence"), PERSISTENCE_VALUES, field=f"{field}.persistence", errors=errors
    )
    polarity = _require_enum(
        value.get("polarity"), POLARITY_VALUES, field=f"{field}.polarity", errors=errors
    )
    scope = _require_enum(value.get("scope"), SCOPE_VALUES, field=f"{field}.scope", errors=errors)
    impact = _require_enum(value.get("impact"), IMPACT_VALUES, field=f"{field}.impact", errors=errors)
    confidence = _require_enum(
        value.get("confidence"), CONFIDENCE_VALUES, field=f"{field}.confidence", errors=errors
    )
    from_term = _require_string(
        value.get("from_term"), field=f"{field}.from_term", errors=errors, allow_none=True
    )
    preferred = _require_string(
        value.get("preferred"), field=f"{field}.preferred", errors=errors, allow_none=True
    )
    conflict_group = _require_string(
        value.get("conflict_group"),
        field=f"{field}.conflict_group",
        errors=errors,
        allow_none=True,
    )
    term_evidence = _parse_evidence(value.get("term_evidence"), field=f"{field}.term_evidence", errors=errors)
    raw_intent_evidence = value.get("intent_evidence")
    intent_evidence: list[EvidenceRef] = []
    if not isinstance(raw_intent_evidence, list) or not raw_intent_evidence:
        errors.append(f"{field}.intent_evidence must be a non-empty list")
    else:
        for index, item in enumerate(raw_intent_evidence):
            evidence = _parse_evidence(item, field=f"{field}.intent_evidence[{index}]", errors=errors)
            if evidence is not None:
                intent_evidence.append(evidence)

    if intent == "rename" and (from_term is None or preferred is None):
        errors.append(f"{field} rename intent requires from_term and preferred")
    if intent != "rename" and from_term is not None:
        errors.append(f"{field}.from_term is allowed only for rename intent")
    if intent != "rename" and preferred is not None:
        errors.append(f"{field}.preferred is allowed only for rename intent")
    if (
        intent == "rename"
        and term is not None
        and from_term is not None
        and normalize_term(term) != normalize_term(from_term)
    ):
        errors.append(f"{field}.term must identify the same wording as from_term for rename intent")
    if intent == "conflict" and conflict_group is None:
        errors.append(f"{field} conflict intent requires conflict_group")
    if intent != "conflict" and conflict_group is not None:
        errors.append(f"{field}.conflict_group is allowed only for conflict intent")

    if term_evidence is not None:
        _resolve_evidence(source, term_evidence, field=f"{field}.term_evidence", errors=errors)
        if term is not None and term not in term_evidence.text:
            errors.append(f"{field}.term must occur exactly in term_evidence.text")
    for index, evidence in enumerate(intent_evidence):
        _resolve_evidence(source, evidence, field=f"{field}.intent_evidence[{index}]", errors=errors)

    evidence_text = "\n".join(
        [term_evidence.text if term_evidence else "", *(item.text for item in intent_evidence)]
    )
    for name, supported_value in (("from_term", from_term), ("preferred", preferred)):
        if supported_value is not None and supported_value not in evidence_text:
            errors.append(f"{field}.{name} must occur exactly in cited evidence")

    if term is not None and not normalize_term(term):
        errors.append(f"{field}.term must contain a normalizable term")

    if None in (frame_id, term, term_evidence) or not all(
        (intent, persistence, polarity, scope, impact, confidence)
    ):
        return None
    return DecisionFrame(
        frame_id=frame_id,
        term=term,
        normalized=normalize_term(term),
        intent=intent,
        persistence=persistence,
        polarity=polarity,
        scope=scope,
        from_term=from_term,
        preferred=preferred,
        conflict_group=conflict_group,
        impact=impact,
        term_evidence=term_evidence,
        intent_evidence=tuple(intent_evidence),
        confidence=confidence,
    )


def _string_id_list(value: Any, *, field: str, errors: list[str]) -> list[str]:
    if not isinstance(value, list):
        errors.append(f"{field} must be a list")
        return []
    result: list[str] = []
    for index, item in enumerate(value):
        parsed = _require_string(item, field=f"{field}[{index}]", errors=errors)
        if parsed is not None:
            result.append(parsed)
    return result


def _frame_outcome(
    frame: DecisionFrame,
    *,
    registered: set[str],
    forced_exception: bool,
) -> FrameOutcome:
    is_registered = frame.normalized in registered
    preferred_normalized = normalize_term(frame.preferred or "")
    if forced_exception:
        outcome, reason = "exception", "extractor_critic_disagreement"
    elif frame.polarity in {"negated", "reported"} or frame.persistence == "none":
        outcome, reason = "exclude", "non_durable_or_non_authoritative_frame"
    elif (
        is_registered
        and frame.intent in {"mention", "adopt"}
        and (not preferred_normalized or preferred_normalized == frame.normalized)
    ):
        outcome, reason = "existing-match", "registered_term_match"
    elif frame.persistence == "temporary" or frame.scope == "one-off":
        outcome, reason = "observe", "temporary_or_one_off_frame"
    elif frame.intent in {"adopt", "rename", "conflict"}:
        outcome, reason = "exception", "affirmed_wording_decision"
    elif frame.intent == "define":
        if frame.persistence == "durable" or frame.impact == "high":
            outcome, reason = "exception", "durable_or_high_impact_definition"
        else:
            outcome, reason = "observe", "unclear_non_high_impact_definition"
    elif frame.intent == "mention":
        if frame.persistence == "unclear" and frame.confidence != "high":
            outcome, reason = "observe", "unclear_mention"
        else:
            outcome, reason = "exclude", "non_decision_mention"
    else:  # pragma: no cover - protected by enum validation
        outcome, reason = "observe", "unresolved_frame"
    return FrameOutcome(
        frame_id=frame.frame_id,
        term=frame.term,
        normalized=frame.normalized,
        outcome=outcome,
        reason=reason,
        impact=frame.impact,
        registered=is_registered,
        intent=frame.intent,
        persistence=frame.persistence,
        polarity=frame.polarity,
        scope=frame.scope,
        requested_preferred=frame.preferred,
        conflict_group=frame.conflict_group,
    )


def analyze_decision_frames(
    text: str,
    payload: Any,
    registered_terms: Iterable[str] | None = None,
) -> SemanticFrameAnalysis:
    errors: list[str] = []
    if not isinstance(payload, dict):
        raise FrameValidationError(["payload must be an object"])
    _reject_unknown_fields(payload, PAYLOAD_FIELDS, field="payload", errors=errors)
    if payload.get("contract_version") != CONTRACT_VERSION:
        errors.append(f"contract_version must be {CONTRACT_VERSION}")
    raw_frames = payload.get("frames")
    if not isinstance(raw_frames, list):
        errors.append("frames must be a list")
        raw_frames = []

    frames: list[DecisionFrame] = []
    for index, raw_frame in enumerate(raw_frames):
        frame = _parse_frame(raw_frame, field=f"frames[{index}]", source=text, errors=errors)
        if frame is not None:
            frames.append(frame)

    critic = payload.get("critic")
    if not isinstance(critic, dict):
        errors.append("critic must be an object")
        critic = {}
    else:
        _reject_unknown_fields(critic, CRITIC_FIELDS, field="critic", errors=errors)
    critic_status = _require_enum(
        critic.get("status"), CRITIC_STATUS_VALUES, field="critic.status", errors=errors
    )
    confirmed_ids = _string_id_list(
        critic.get("confirmed_frame_ids"), field="critic.confirmed_frame_ids", errors=errors
    )
    rejected_ids = _string_id_list(
        critic.get("rejected_frame_ids"), field="critic.rejected_frame_ids", errors=errors
    )
    unresolved_ids = _string_id_list(
        critic.get("unresolved_frame_ids"), field="critic.unresolved_frame_ids", errors=errors
    )
    raw_missing_frames = critic.get("missing_frames")
    if not isinstance(raw_missing_frames, list):
        errors.append("critic.missing_frames must be a list")
        raw_missing_frames = []
    for index, raw_frame in enumerate(raw_missing_frames):
        frame = _parse_frame(
            raw_frame,
            field=f"critic.missing_frames[{index}]",
            source=text,
            errors=errors,
        )
        if frame is not None:
            frames.append(frame)
            unresolved_ids.append(frame.frame_id)

    frame_ids = [frame.frame_id for frame in frames]
    if len(frame_ids) != len(set(frame_ids)):
        errors.append("frame_id values must be unique")
    critic_ids = confirmed_ids + rejected_ids + unresolved_ids
    if len(critic_ids) != len(set(critic_ids)):
        errors.append("critic frame-id lists must not overlap")
    if set(critic_ids) != set(frame_ids):
        errors.append("critic must classify every frame_id exactly once")
    if critic_status == "confirmed" and (unresolved_ids or raw_missing_frames):
        errors.append("confirmed critic status cannot contain unresolved or missing frames")
    if critic_status == "needs-review" and not (unresolved_ids or raw_missing_frames):
        errors.append("needs-review critic status requires an unresolved or missing frame")

    active_conflicts: dict[str, set[str]] = {}
    for frame in frames:
        if frame.frame_id in rejected_ids or frame.intent != "conflict" or frame.conflict_group is None:
            continue
        active_conflicts.setdefault(frame.conflict_group, set()).add(frame.normalized)
    for group, terms in active_conflicts.items():
        if len(terms) < 2:
            errors.append(f"conflict_group {group!r} requires at least two distinct active terms")

    if errors:
        raise FrameValidationError(errors)

    registered = {normalize_term(term) for term in (registered_terms or ()) if normalize_term(term)}
    outcomes: list[FrameOutcome] = []
    consumed: set[str] = set()
    for frame in frames:
        if frame.frame_id in rejected_ids:
            outcomes.append(
                FrameOutcome(
                    frame_id=frame.frame_id,
                    term=frame.term,
                    normalized=frame.normalized,
                    outcome="exclude",
                    reason="critic_rejected_spurious_frame",
                    impact=frame.impact,
                    registered=frame.normalized in registered,
                    intent=frame.intent,
                    persistence=frame.persistence,
                    polarity=frame.polarity,
                    scope=frame.scope,
                    requested_preferred=frame.preferred,
                    conflict_group=frame.conflict_group,
                )
            )
        else:
            outcomes.append(
                _frame_outcome(
                    frame,
                    registered=registered,
                    forced_exception=frame.frame_id in unresolved_ids,
                )
            )
        consumed.add(frame.normalized)

    for term, _count in extract_registered_matches(text, registered):
        if term in consumed:
            continue
        outcomes.append(
            FrameOutcome(
                frame_id=None,
                term=term,
                normalized=term,
                outcome="existing-match",
                reason="registered_term_match",
                impact="medium",
                registered=True,
                intent=None,
                persistence=None,
                polarity=None,
                scope=None,
            )
        )

    priority = {"exception": 0, "existing-match": 1, "observe": 2, "exclude": 3}
    outcomes.sort(key=lambda item: (priority[item.outcome], item.normalized, item.frame_id or ""))
    return SemanticFrameAnalysis(
        results=tuple(outcomes),
        critic_status=critic_status,
        validated_frame_count=len(frames),
    )
