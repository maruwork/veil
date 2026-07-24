from __future__ import annotations

from dataclasses import asdict, dataclass
import re
from typing import Any, Iterable

from shared.tools.veil_capture_classifier import (
    ClassifiedTerm,
    extract_classified_terms,
    sanitize_capture_text,
)
from shared.tools.veil_capture_taxonomy import (
    LABEL_COINED_OR_SHORTENED,
    LABEL_FILE_CONFIG_IDENTIFIER,
    LABEL_INDUSTRY_TERM,
    LABEL_OTHER,
    LABEL_UNKNOWN,
)
from shared.tools.veil_rule_store import normalize_term


CONTRACT_VERSION = "1"
OUTCOME_EXCLUDE = "exclude"
OUTCOME_OBSERVE = "observe"
OUTCOME_EXISTING_MATCH = "existing-match"
OUTCOME_EXCEPTION = "exception"
ALL_OUTCOMES = (
    OUTCOME_EXCLUDE,
    OUTCOME_OBSERVE,
    OUTCOME_EXISTING_MATCH,
    OUTCOME_EXCEPTION,
)

_LATIN_TERM = r"[A-Za-z][A-Za-z0-9_-]*(?:[ \t]+[A-Za-z][A-Za-z0-9_-]*){0,3}"
_LATIN_TERM_LAZY = r"[A-Za-z][A-Za-z0-9_-]*(?:[ \t]+[A-Za-z][A-Za-z0-9_-]*){0,5}?"
_JA_TERM = r"[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fffー]{2,30}?"
_MIXED_TERM = rf"(?:{_LATIN_TERM}|{_JA_TERM})"
_JA_SENTENCE_PREFIX = (
    r"(?:^|[。！？\r\n]\s*)"
    r"(?:(?:この(?:プロジェクト|リポジトリ|チーム|文脈)では|今後(?:は)?|これから(?:は)?|VEILでは)\s*)?"
)
_QUOTED_VALUE = r"[^\"'」』\r\n]{2,60}"
_QUOTED_TERM = rf"[\"'「『](?P<term>{_QUOTED_VALUE})[\"'」』]"
_HIGH_IMPACT_RE = re.compile(
    r"\b(?:always|must|required|every|block(?:s|ed|ing)?|control(?:s|led|ling)?|"
    r"release|distribution|canonical|external|security|delete|write|commit|push|"
    r"production|destructive|rollback|irreversible|removal|authority|approve)\b|"
    r"必ず|常に|全(?:て|部)|阻止|制御|配布|正本|外部|安全|削除|書(?:き)?込|コミット|プッシュ",
    re.IGNORECASE,
)
_TRIM_LEADING_WORDS_RE = re.compile(
    r"^(?:in this project|in this repository|in this repo|in this team|in this context|"
    r"the|a|an|our|this)\s+",
    re.IGNORECASE,
)
_NON_INTENT_RE = re.compile(
    r"\b(?:did not|do not|does not|nobody asked|not an instruction|test fixture|sample text|"
    r"rejected proposal|under discussion|no action|explains how|log recorded)\b|"
    r"(?:提案は却下|却下した|指示ではない|登録しない|変更しない|統一しない|検討中|例文|テスト用)",
    re.IGNORECASE,
)
_QUOTED_META_TERMS = {
    "quoted phrase",
    "quoted term",
    "quoted wording",
    "the phrase",
    "the term",
    "というフレーズ",
    "という表記",
    "引用語",
}
_REPEATED_DESCRIPTION_RE = re.compile(
    r"(?:\b(?:two|three|four|five|multiple|repeated|monthly|weekly|twice|\d+\s+times?)\b"
    r"[^.!?\r\n]{0,140}\b(?:describe|described|call|called|refer(?:red)?\s+to|label(?:led)?|name(?:d)?)\b)"
    r"|(?:(?:二|三|四|五|[2-9])(?:回|件|週|か月|ヶ月)|月次|週次|毎週|繰り返し)"
    r"[^。！？\r\n]{0,140}(?:説明|呼|記載|表現)",
    re.IGNORECASE,
)
_DURABLE_CONFLICT_RE = re.compile(
    r"\b(?:competing|conflicting)\s+(?:durable\s+)?(?:forms?|terms?|wording)\b"
    r"|\b(?:first|earlier).{0,100}\bprefers?\b.{0,100}\b(?:later|while)\b"
    r"|競合(?:する)?(?:永続)?候補|同じ[^。！？\r\n]{0,80}(?:前半|先).{0,80}(?:後半|後).{0,80}優先",
    re.IGNORECASE,
)
_DURABLE_DEFINITION_RE = re.compile(
    r"\b(?:durable|persistent|permanent|canonical)\s+definitions?\b"
    r"|永続的な定義|永続(?:化)?する定義|正本(?:の)?定義",
    re.IGNORECASE,
)
_DURABLE_INVENTORY_RE = re.compile(
    r"\b(?:complete|exactly|only)\b[^.!?\r\n]{0,80}\b(?:durable|persist(?:ed|ence|ent)?)\b"
    r"|\b(?:durable|persistent)\b[^.!?\r\n]{0,80}\b(?:inventory|terms?\s+intended)\b"
    r"|永続化?(?:を意図)?する(?:用語|語|候補)[^。！？\r\n]{0,40}(?:二つ|2つ|だけ)"
    r"|永続(?:候補|語)[^。！？\r\n]{0,40}(?:二つ|2つ|だけ)",
    re.IGNORECASE,
)
_TEMPORARY_SCOPE_RE = re.compile(
    r"\b(?:for|in)\s+this\s+(?:single|one-off|temporary|classroom|workshop|exercise)\b"
    r"|\b(?:this|one)\s+(?:single|one-off|temporary)\b"
    r"|(?:今回|この一回|一回限り|一度限り)[^。！？\r\n]{0,30}(?:に限り|だけ|のみ)"
    r"|この(?:工作教室|勉強会|演習|例|図)(?:に限り|だけ|では)",
    re.IGNORECASE,
)
_REPEATED_EDGE_STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "but", "by", "for", "from", "has", "have",
    "in", "is", "it", "of", "on", "or", "that", "the", "this", "to", "was", "were", "with",
}



@dataclass(frozen=True)
class ContextSignal:
    term: str
    normalized: str
    kind: str
    reason: str
    impact: str
    position: int
    evidence: str
    requested_preferred: str | None = None


@dataclass(frozen=True)
class CaptureOutcome:
    term: str
    normalized: str
    outcome: str
    reason: str
    impact: str
    confidence: float
    occurrences: int = 1
    registered: bool = False
    signal: str | None = None
    requested_preferred: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class CaptureAnalysis:
    results: tuple[CaptureOutcome, ...]

    @property
    def exceptions(self) -> tuple[CaptureOutcome, ...]:
        return tuple(item for item in self.results if item.outcome == OUTCOME_EXCEPTION)

    @property
    def user_action_required(self) -> bool:
        return bool(self.exceptions)

    @property
    def question_count(self) -> int:
        return 1 if self.user_action_required else 0

    def to_dict(self) -> dict[str, Any]:
        counts = {name: 0 for name in ALL_OUTCOMES}
        for item in self.results:
            counts[item.outcome] += 1
        return {
            "contract_version": CONTRACT_VERSION,
            "analysis_mode": "raw-text-diagnostic",
            "diagnostic_only": True,
            "write_allowed": False,
            "summary": {
                "user_action_required": self.user_action_required,
                "question_count": self.question_count,
                "counts": counts,
                "automatic_processed": (
                    counts[OUTCOME_EXCLUDE]
                    + counts[OUTCOME_OBSERVE]
                    + counts[OUTCOME_EXISTING_MATCH]
                ),
            },
            "exceptions": [item.to_dict() for item in self.exceptions],
            "results": [item.to_dict() for item in self.results],
        }


def _sentence_evidence(text: str, position: int) -> str:
    start, end = _sentence_bounds(text, position)
    return re.sub(r"\s+", " ", text[start:end]).strip()[:240]


def _sentence_bounds(text: str, position: int) -> tuple[int, int]:
    start = max(text.rfind("\n", 0, position), text.rfind(".", 0, position), text.rfind("。", 0, position)) + 1
    ends = [end for end in (text.find("\n", position), text.find(".", position), text.find("。", position)) if end >= 0]
    return start, min(ends) if ends else len(text)


def _clean_signal_term(term: str) -> str:
    value = re.sub(r"\s+", " ", term).strip(" \t,.;:!?、。・")
    previous = None
    while value and value != previous:
        previous = value
        value = _TRIM_LEADING_WORDS_RE.sub("", value).strip()
    value = re.sub(r"\s+(?:consistently|everywhere|always)$", "", value, flags=re.IGNORECASE).strip()
    return value


def _impact(kind: str, evidence: str) -> str:
    if kind in {"repeat_observation", "descriptive_definition", "non_target"}:
        return "low"
    if kind in {"consistency_request", "registration_request", "change_request"}:
        return "high"
    return "high" if _HIGH_IMPACT_RE.search(evidence) else "medium"


def _mask_non_authoritative_text(text: str) -> str:
    def spaces(match: re.Match[str]) -> str:
        return " " * (match.end() - match.start())

    masked = re.sub(r"```[\s\S]*?```", spaces, text or "")
    masked = re.sub(r"`[^`\r\n]*`", spaces, masked)
    masked = re.sub(r'"[^"\r\n]{8,}"', spaces, masked)
    masked = re.sub(r"'[^'\r\n]{8,}'", spaces, masked)
    return masked


def _record_signal(
    signals: dict[str, ContextSignal],
    *,
    term: str,
    kind: str,
    reason: str,
    position: int,
    text: str,
    requested_preferred: str | None = None,
) -> None:
    cleaned = _clean_signal_term(term)
    normalized = normalize_term(cleaned)
    if not normalized or len(normalized) < 2:
        return
    if normalized in _QUOTED_META_TERMS:
        return
    evidence = _sentence_evidence(text, position)
    if _NON_INTENT_RE.search(evidence):
        return
    preferred = _clean_signal_term(requested_preferred or "") or None
    signal = ContextSignal(
        term=cleaned,
        normalized=normalized,
        kind=kind,
        reason=reason,
        impact=_impact(kind, evidence),
        position=position,
        evidence=evidence,
        requested_preferred=preferred,
    )
    current = signals.get(normalized)
    priority = {
        "non_target": 0,
        "repeat_observation": 0,
        "descriptive_definition": 1,
        "consistency_request": 1,
        "local_definition": 2,
        "registration_request": 3,
        "change_request": 4,
    }
    if (
        current is None
        or priority.get(signal.kind, 0) > priority.get(current.kind, 0)
        or (current.impact != "high" and signal.impact == "high")
        or (current.requested_preferred is None and signal.requested_preferred is not None)
    ):
        signals[normalized] = signal


def _quoted_signal_spec(
    text: str,
    match: re.Match[str],
) -> tuple[str, str] | None:
    position = match.start("term")
    sentence_start, sentence_end = _sentence_bounds(text, position)
    evidence = text[sentence_start:sentence_end]
    previous_end = max(0, sentence_start - 1)
    previous_start = max(
        text.rfind("\n", 0, previous_end),
        text.rfind(".", 0, previous_end),
        text.rfind("。", 0, previous_end),
    ) + 1
    scoped_evidence = text[previous_start:sentence_end]
    before = text[max(sentence_start, match.start() - 80):match.start()]
    after = text[match.end():min(sentence_end, match.end() + 120)]
    term = match.group("term")
    quoted_term = re.escape(term)

    english_negation = re.search(
        rf"\b(?:do\s+not|don't|never)\s+(?:register|save|record|remember|persist)"
        rf"[^.!?\r\n]{{0,50}}[\"']{quoted_term}[\"']",
        evidence,
        re.IGNORECASE,
    )
    japanese_negation = re.search(
        rf"[「『]{quoted_term}[」』][^。！？\r\n]{{0,30}}"
        r"(?:登録|保存|記録|永続化|規則化)(?:は)?しない",
        evidence,
    )
    if english_negation or japanese_negation:
        return None

    mapping_target = re.search(
        r"[\"'「『][^\"'」』\r\n]{2,60}[\"'」』]\s*(?:を|から|ではなく)\s*$",
        before,
    )
    if mapping_target:
        return None

    if _REPEATED_DESCRIPTION_RE.search(scoped_evidence):
        return "repeat_observation", "natural_language_repetition"

    if _DURABLE_CONFLICT_RE.search(scoped_evidence):
        return "change_request", "explicit_inventoried_conflict"

    if _DURABLE_DEFINITION_RE.search(scoped_evidence):
        return "registration_request", "explicit_durable_definition"

    english_action = re.search(
        r"\b(?:register|save|record|remember|persist)\s+"
        r"(?:(?:the\s+)?(?:quoted\s+)?(?:phrase|term|wording)\s+)?$",
        before,
        re.IGNORECASE,
    )
    japanese_action = re.search(
        r"^\s*(?:という(?:フレーズ|表記|呼称)|という語|を)?"
        r"[^、。！？\r\n]{0,70}(?:として|で)?\s*(?:登録|保存|記録)(?:して|する|してください|します)",
        after,
        re.IGNORECASE,
    )
    if english_action or japanese_action:
        return "registration_request", "explicit_quoted_registration_request"

    has_change_mapping = re.search(r"\b(?:change|replace|rename)\b|変更|置き換え|差し替え", evidence, re.IGNORECASE)
    if _DURABLE_INVENTORY_RE.search(scoped_evidence) and not has_change_mapping:
        return "registration_request", "explicit_durable_inventory"

    quoted_definition = re.search(
        r"^\s*(?:means|is\s+defined\s+as)\b|^\s*(?:とは|は)\s*[^。！？\r\n]{0,100}(?:意味|定義|指)",
        after,
        re.IGNORECASE,
    )
    if quoted_definition and _TEMPORARY_SCOPE_RE.search(evidence):
        return "descriptive_definition", "descriptive_local_definition"
    if quoted_definition:
        return "local_definition", "explicit_quoted_local_definition"
    return None


def extract_context_signals(text: str) -> list[ContextSignal]:
    source = text or ""
    masked_source = _mask_non_authoritative_text(source)
    signals: dict[str, ContextSignal] = {}
    patterns = (
        (
            re.compile(
                rf"\bchange\s+(?:the\s+)?preferred\s+(?:wording|term|form)\s+from\s+"
                rf"(?P<term>{_LATIN_TERM_LAZY})\s+to\s+"
                rf"(?P<preferred>{_LATIN_TERM_LAZY})"
                r"(?=\s+(?:in|for)\s+(?:the\s+)?(?:registered\s+)?vocabulary\b|[,.;:!?\r\n]|$)",
                re.IGNORECASE,
            ),
            "change_request",
            "explicit_change_request",
        ),
        (
            re.compile(
                rf"\bregister\s+(?P<term>{_LATIN_TERM})\s+as\s+"
                rf"(?P<preferred>{_LATIN_TERM})\s+in\s+VEIL\b",
                re.IGNORECASE,
            ),
            "registration_request",
            "explicit_registration_mapping",
        ),
        (
            re.compile(
                rf"\b(?:change|rename)\s+(?P<term>{_LATIN_TERM})\s+(?:to|as)\s+"
                rf"(?P<preferred>{_LATIN_TERM})(?=[,.;:!?\r\n]|$)",
                re.IGNORECASE,
            ),
            "change_request",
            "explicit_change_request",
        ),
        (
            re.compile(
                rf"\breplace\s+(?P<term>{_LATIN_TERM_LAZY})\s+with\s+"
                rf"(?P<preferred>{_LATIN_TERM_LAZY})"
                r"(?=\s+(?:in|for)\s+(?:the\s+)?(?:registered\s+)?vocabulary\b|[,.;:!?\r\n]|$)",
                re.IGNORECASE,
            ),
            "change_request",
            "explicit_change_request",
        ),
        (
            re.compile(
                rf"\buse\s+(?P<preferred>{_LATIN_TERM})\s+instead\s+of\s+"
                rf"(?P<term>{_LATIN_TERM})(?=[,.;:!?\r\n]|$)",
                re.IGNORECASE,
            ),
            "change_request",
            "explicit_conflict_request",
        ),
        (
            re.compile(
                rf"\buse\s+(?P<term>{_LATIN_TERM_LAZY})\s+as\s+"
                r"(?:the\s+)?preferred\s+(?:form|wording|term)(?:\s+instead)?"
                r"(?=[,.;:!?\r\n]|$)",
                re.IGNORECASE,
            ),
            "change_request",
            "explicit_conflict_request",
        ),
        (
            re.compile(
                rf"(?P<term>{_MIXED_TERM})\s*(?:を|から)\s*"
                rf"(?P<preferred>{_MIXED_TERM})\s*(?:に|へ)"
                r"(?:変更|統一|置き換え|差し替え)",
                re.IGNORECASE,
            ),
            "change_request",
            "explicit_change_request",
        ),
        (
            re.compile(
                rf"(?P<term>{_MIXED_TERM})\s*ではなく\s*"
                rf"(?P<preferred>{_MIXED_TERM})\s*(?:を)?(?:使|採用)",
                re.IGNORECASE,
            ),
            "change_request",
            "explicit_conflict_request",
        ),
        (
            re.compile(
                rf"(?P<term>{_MIXED_TERM})\s*を\s*"
                rf"(?P<preferred>{_MIXED_TERM})\s*として登録",
                re.IGNORECASE,
            ),
            "registration_request",
            "explicit_registration_mapping",
        ),
        (
            re.compile(
                rf"\b(?:please\s+)?(?:also\s+)?(?:register|remember|record|save)[ \t]{{1,2}}"
                rf"(?:(?:the[ \t]+)?(?:phrase|term|wording)[ \t]{{1,2}})?"
                rf"(?P<term>(?!(?:it|this|that|them|(?:the[ \t]+)?quoted[ \t]+wording|"
                rf"the[ \t]+(?:phrase|term|wording))\b){_LATIN_TERM_LAZY})"
                r"(?=\s+(?:as|for|in\s+VEIL)\b|[,.;:!?\r\n]|$)",
                re.IGNORECASE,
            ),
            "registration_request",
            "explicit_registration_request",
        ),
        (
            re.compile(
                rf"\b(?:use|call|refer to)\s+(?:the\s+(?:phrase|term)\s+)?"
                rf"(?P<term>{_LATIN_TERM})\s+(?:consistently|everywhere|from now on)\b",
                re.IGNORECASE,
            ),
            "consistency_request",
            "explicit_consistency_request",
        ),
        (
            re.compile(
                rf"\balways\s+(?:use|call|refer to)\s+(?:the\s+(?:phrase|term)\s+)?"
                rf"(?P<term>{_LATIN_TERM})(?=[,.;:!?\r\n]|$)",
                re.IGNORECASE,
            ),
            "consistency_request",
            "explicit_consistency_request",
        ),
        (
            re.compile(rf"\b(?:standardize on|standardise on)\s+(?P<term>{_LATIN_TERM})(?=[,.;:!?\r\n]|$)", re.IGNORECASE),
            "consistency_request",
            "explicit_consistency_request",
        ),
        (
            re.compile(rf"\bmake\s+(?P<term>{_LATIN_TERM})\s+the\s+standard\s+term\b", re.IGNORECASE),
            "consistency_request",
            "explicit_consistency_request",
        ),
        (
            re.compile(
                rf"(?:^|[.!?\r\n]\s*)"
                rf"(?:(?:in|for) this [A-Za-z][A-Za-z0-9_-]*(?:\s+[A-Za-z][A-Za-z0-9_-]*){{0,2}},?\s+|here,?\s+)?"
                rf"(?P<term>{_LATIN_TERM})\s+means\b",
                re.IGNORECASE,
            ),
            "local_definition",
            "explicit_local_definition",
        ),
        (
            re.compile(rf"\b(?P<term>{_LATIN_TERM})\s+is\s+defined\s+as\b", re.IGNORECASE),
            "local_definition",
            "explicit_local_definition",
        ),
        (
            re.compile(rf"\b(?:we\s+)?define\s+(?P<term>{_LATIN_TERM})\s+as\b", re.IGNORECASE),
            "local_definition",
            "explicit_local_definition",
        ),
        (
            re.compile(rf"\b(?:register|remember|record)\s+(?P<term>{_LATIN_TERM})\s+(?:as|in VEIL\b)", re.IGNORECASE),
            "registration_request",
            "explicit_registration_request",
        ),
        (
            re.compile(
                rf"(?:^|[.!?\r\n]\s*)(?P<term>[A-Z][a-z]{{2,}})\s+"
                r"(?=(?:will|would|has|had|is|was|reviewed|joined|said)\b)",
            ),
            "non_target",
            "proper_name_non_target",
        ),
        (
            re.compile(
                rf"(?:^|[.!?\r\n]\s*)(?P<term>{_LATIN_TERM_LAZY})\s+"
                r"(?:appears?|appeared|was\s+used|is\s+used|stayed|remained|shows?|showed)\b"
                r"[^.!?\r\n]{0,80}\b(?:both|multiple|repeated(?:ly)?|consecutive|weekly|twice)\b",
                re.IGNORECASE,
            ),
            "repeat_observation",
            "natural_language_repetition",
        ),
        (
            re.compile(
                rf"(?:^|[.!?\r\n]\s*)(?:across\s+)?"
                r"(?:two|three|four|five|multiple|\d+)\s+"
                r"(?:[A-Za-z][A-Za-z0-9_-]*\s+){0,2}"
                r"(?:notes|records|reports|messages|documents|sessions|weeks|months)\b"
                r"[^.!?\r\n]{0,100}\b(?:describe|described|call|called|label(?:led)?|name(?:d)?)\b"
                rf"[^.!?\r\n]{{0,80}}\bas\s+(?:the\s+)?(?P<term>{_LATIN_TERM_LAZY})"
                r"(?=[.!?\r\n]|$)",
                re.IGNORECASE,
            ),
            "repeat_observation",
            "natural_language_repetition",
        ),
        (
            re.compile(rf"(?P<term>{_LATIN_TERM})\s*(?:という表記)?\s*(?:を)?(?:一貫して使|必ず使|に統一(?:して|する)|と呼(?:ぶ(?:ことにする)?|んでください)|を標準表記にする|として登録する)", re.IGNORECASE),
            "consistency_request",
            "explicit_consistency_request",
        ),
        (
            re.compile(rf"(?P<term>{_LATIN_TERM})\s*(?:とは|は)\s*[^。\r\n]{{0,80}}(?:意味|定義|指す)", re.IGNORECASE),
            "local_definition",
            "explicit_local_definition",
        ),
        (
            re.compile(
                rf"{_JA_SENTENCE_PREFIX}(?P<term>{_JA_TERM})\s*(?:という表記)?\s*(?:を)?"
                r"(?:一貫して使|必ず使|に統一(?:して|する)|と呼(?:ぶ(?:ことにする)?|んでください)|を標準表記にする|として登録する)",
                re.IGNORECASE,
            ),
            "consistency_request",
            "explicit_consistency_request",
        ),
        (
            re.compile(
                rf"{_JA_SENTENCE_PREFIX}(?P<term>{_JA_TERM})\s*(?:とは|は)\s*"
                r"[^。\r\n]{0,80}(?:意味|定義|指す)",
                re.IGNORECASE,
            ),
            "local_definition",
            "explicit_local_definition",
        ),
        (
            re.compile(
                rf"(?:^|[。！？\r\n]\s*)(?:この[^。！？\r\n]{{1,24}}では、?\s*)?"
                rf"(?P<term>{_JA_TERM})\s*を\s*[^。！？\r\n]{{1,80}}"
                r"と呼(?:びます|んでいます|ぶ)",
                re.IGNORECASE,
            ),
            "descriptive_definition",
            "descriptive_local_definition",
        ),
        (
            re.compile(
                rf"(?:^|[。！？\r\n]\s*)(?:今回|この一回|一回限り|一度限り)"
                rf"[^。！？\r\n]{{0,30}}(?:に限り|だけ|のみ)[、,]?\s*"
                rf"(?P<term>{_JA_TERM})\s*(?:とは|は)\s*[^。！？\r\n]{{1,100}}"
                r"(?:を指(?:す|します)|を意味(?:する|します))",
                re.IGNORECASE,
            ),
            "descriptive_definition",
            "descriptive_local_definition",
        ),
        (
            re.compile(
                rf"(?:二|2)週続けて[^。！？\r\n]{{0,60}}を\s*"
                rf"(?P<term>{_JA_TERM})\s*と呼んで",
                re.IGNORECASE,
            ),
            "repeat_observation",
            "natural_language_repetition",
        ),
    )
    for pattern, kind, reason in patterns:
        for match in pattern.finditer(masked_source):
            _record_signal(
                signals,
                term=match.group("term"),
                kind=kind,
                reason=reason,
                position=match.start("term"),
                text=source,
                requested_preferred=match.groupdict().get("preferred"),
            )

    quoted_patterns = (
        (
            re.compile(
                rf"\b(?:please\s+)?(?:also\s+)?(?:register|remember|record|save)\s+"
                rf"(?:(?:the\s+)?(?:phrase|term|quoted\s+wording)\s+)?{_QUOTED_TERM}"
                r"(?=\s+(?:as|for|in\s+VEIL)\b|[,.;:!?\r\n]|$)",
                re.IGNORECASE,
            ),
            "registration_request",
            "explicit_quoted_registration_request",
        ),
        (
            re.compile(
                rf"\buse\s+(?:the\s+)?(?:phrase|term)\s+{_QUOTED_TERM}\s+as\b"
                r"[^.!?\r\n]{0,120}\b(?:save|register|record)\s+it\b",
                re.IGNORECASE,
            ),
            "registration_request",
            "explicit_quoted_registration_request",
        ),
        (
            re.compile(
                rf"\bregister\s+[\"'「『](?P<term>{_QUOTED_VALUE})[\"'」』]\s+as\s+"
                rf"[\"'「『](?P<preferred>{_QUOTED_VALUE})[\"'」』]\s+in\s+VEIL\b",
                re.IGNORECASE,
            ),
            "registration_request",
            "explicit_registration_mapping",
        ),
        (
            re.compile(
                rf"[\"'「『](?P<term>{_QUOTED_VALUE})[\"'」』]\s*(?:は|を)?使わず[^。！？\r\n]{{0,80}}"
                rf"[\"'「『](?P<preferred>{_QUOTED_VALUE})[\"'」』][^。！？\r\n]{{0,60}}"
                r"(?:変更|統一|優先|正式な表記)",
                re.IGNORECASE,
            ),
            "change_request",
            "explicit_conflict_request",
        ),
        (
            re.compile(
                rf"\b(?:change|rename)\s+[\"'「『](?P<term>{_QUOTED_VALUE})[\"'」』]\s+"
                rf"(?:to|as)\s+[\"'「『](?P<preferred>{_QUOTED_VALUE})[\"'」』]",
                re.IGNORECASE,
            ),
            "change_request",
            "explicit_change_request",
        ),
        (
            re.compile(
                rf"[\"'「『](?P<term>{_QUOTED_VALUE})[\"'」』]\s*(?:を|から)\s*"
                rf"[\"'「『](?P<preferred>{_QUOTED_VALUE})[\"'」』]\s*(?:に|へ)"
                r"(?:変更|統一|置き換え|差し替え)",
                re.IGNORECASE,
            ),
            "change_request",
            "explicit_change_request",
        ),
        (
            re.compile(
                rf"[\"'「『](?P<term>{_QUOTED_VALUE})[\"'」』]\s*ではなく\s*"
                rf"[\"'「『](?P<preferred>{_QUOTED_VALUE})[\"'」』]\s*(?:を)?(?:使|採用)",
                re.IGNORECASE,
            ),
            "change_request",
            "explicit_conflict_request",
        ),
        (
            re.compile(
                rf"[\"'「『](?P<term>{_QUOTED_VALUE})[\"'」』]\s*を\s*"
                rf"[\"'「『](?P<preferred>{_QUOTED_VALUE})[\"'」』]\s*として登録",
                re.IGNORECASE,
            ),
            "registration_request",
            "explicit_registration_mapping",
        ),
        (
            re.compile(
                rf"\b(?:use|call|refer to)\s+{_QUOTED_TERM}\s+"
                r"(?:consistently|everywhere|from now on)\b",
                re.IGNORECASE,
            ),
            "consistency_request",
            "explicit_quoted_consistency_request",
        ),
        (
            re.compile(
                rf"\balways\s+(?:use|call|refer to)\s+{_QUOTED_TERM}"
                r"(?=[,.;:!?\r\n]|$)",
                re.IGNORECASE,
            ),
            "consistency_request",
            "explicit_quoted_consistency_request",
        ),
        (
            re.compile(
                rf"(?:ただし|一方|同じ決定(?:文)?で)[^。！？\r\n]{{0,80}}{_QUOTED_TERM}"
                r"\s*(?:を)?(?:優先|採用)",
                re.IGNORECASE,
            ),
            "change_request",
            "explicit_conflict_request",
        ),
        (
            re.compile(
                _QUOTED_TERM
                + r"[^。！？\r\n]{0,100}(?:名称|表記|呼称)?(?:として|で)?\s*"
                r"(?:登録|保存|記録)(?:して|する|してください|します)",
                re.IGNORECASE,
            ),
            "registration_request",
            "explicit_quoted_registration_request",
        ),
        (
            re.compile(
                _QUOTED_TERM
                + r"\s*(?:という呼称)?(?:を)?(?:一貫して使|必ず使|に統一|"
                r"と呼ぶことにする|と呼んでください|として記録|に登録)"
            ),
            "consistency_request",
            "explicit_quoted_consistency_request",
        ),
        (
            re.compile(_QUOTED_TERM + r"\s*(?:とは|は)\s*[^。\r\n]{0,80}(?:意味|定義|指す)"),
            "local_definition",
            "explicit_quoted_local_definition",
        ),
    )
    for pattern, kind, reason in quoted_patterns:
        for match in pattern.finditer(source):
            _record_signal(
                signals,
                term=match.group("term"),
                kind=kind,
                reason=reason,
                position=match.start("term"),
                text=source,
                requested_preferred=match.groupdict().get("preferred"),
            )
    for match in re.finditer(_QUOTED_TERM, source):
        spec = _quoted_signal_spec(source, match)
        if spec is None:
            continue
        kind, reason = spec
        _record_signal(
            signals,
            term=match.group("term"),
            kind=kind,
            reason=reason,
            position=match.start("term"),
            text=source,
        )
    return sorted(signals.values(), key=lambda item: item.position)


def extract_repeated_observations(text: str) -> list[tuple[str, str, int]]:
    cleaned = sanitize_capture_text(text)
    tokens = re.findall(r"[A-Za-z][A-Za-z0-9_-]*", cleaned)
    counts: dict[str, tuple[str, int]] = {}
    for width in (3, 2):
        for index in range(len(tokens) - width + 1):
            words = tokens[index : index + width]
            normalized_words = [normalize_term(word) for word in words]
            if normalized_words[0] in _REPEATED_EDGE_STOPWORDS or normalized_words[-1] in _REPEATED_EDGE_STOPWORDS:
                continue
            if len(set(normalized_words)) == 1:
                continue
            term = " ".join(words)
            normalized = normalize_term(term)
            current = counts.get(normalized)
            counts[normalized] = (current[0] if current else term, (current[1] if current else 0) + 1)
    return sorted(
        ((term, normalized, count) for normalized, (term, count) in counts.items() if count >= 2),
        key=lambda item: (-len(item[1].split()), -item[2], item[1]),
    )


def extract_registered_matches(text: str, registered_terms: set[str]) -> list[tuple[str, int]]:
    normalized_text = normalize_term(re.sub(r"[^A-Za-z0-9_\-\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff]+", " ", text or ""))
    padded = f" {normalized_text} "
    matches = []
    for term in sorted(registered_terms):
        if re.search(r"[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff]", term):
            boundary = r"A-Za-z0-9_\-\u30a0-\u30ff\u3400-\u4dbf\u4e00-\u9fff"
            count = len(re.findall(rf"(?<![{boundary}]){re.escape(term)}(?![{boundary}])", normalized_text))
        else:
            count = padded.count(f" {term} ")
        if count:
            matches.append((term, count))
    return matches


def _from_signal(signal: ContextSignal, *, registered: bool, occurrences: int) -> CaptureOutcome:
    if signal.kind == "non_target":
        return CaptureOutcome(
            term=signal.term,
            normalized=signal.normalized,
            outcome=OUTCOME_EXCLUDE,
            reason=signal.reason,
            impact="low",
            confidence=0.99,
            occurrences=occurrences,
            registered=False,
            signal=signal.kind,
        )
    if signal.kind in {"repeat_observation", "descriptive_definition"}:
        return CaptureOutcome(
            term=signal.term,
            normalized=signal.normalized,
            outcome=OUTCOME_OBSERVE,
            reason=signal.reason,
            impact="low",
            confidence=0.90,
            occurrences=occurrences,
            registered=registered,
            signal=signal.kind,
        )
    if registered and signal.kind == "consistency_request":
        return CaptureOutcome(
            term=signal.term,
            normalized=signal.normalized,
            outcome=OUTCOME_EXISTING_MATCH,
            reason="explicit_request_already_registered",
            impact=signal.impact,
            confidence=1.0,
            occurrences=occurrences,
            registered=True,
            signal=signal.kind,
            requested_preferred=signal.requested_preferred,
        )
    if signal.kind in {"consistency_request", "registration_request", "change_request"} or signal.impact == "high":
        outcome = OUTCOME_EXCEPTION
        confidence = 0.99 if signal.kind != "local_definition" else 0.96
    else:
        outcome = OUTCOME_OBSERVE
        confidence = 0.85
    return CaptureOutcome(
        term=signal.term,
        normalized=signal.normalized,
        outcome=outcome,
        reason=signal.reason,
        impact=signal.impact,
        confidence=confidence,
        occurrences=occurrences,
        registered=registered,
        signal=signal.kind,
        requested_preferred=signal.requested_preferred,
    )


def _from_classified(item: ClassifiedTerm) -> CaptureOutcome:
    if item.registered:
        return CaptureOutcome(
            term=item.term,
            normalized=item.normalized,
            outcome=OUTCOME_EXISTING_MATCH,
            reason="registered_term_match",
            impact="medium",
            confidence=1.0,
            occurrences=item.occurrences,
            registered=True,
        )
    if item.label == LABEL_COINED_OR_SHORTENED:
        outcome, reason, confidence = OUTCOME_OBSERVE, "unconfirmed_local_wording", 0.82
    elif item.label == LABEL_UNKNOWN:
        outcome, reason, confidence = OUTCOME_OBSERVE, "insufficient_context", 0.70
    elif item.label in {LABEL_FILE_CONFIG_IDENTIFIER, LABEL_INDUSTRY_TERM}:
        outcome, reason, confidence = OUTCOME_EXCLUDE, item.reason, 0.99
    elif item.label == LABEL_OTHER and item.reason == "proper_noun_non_target":
        outcome, reason, confidence = OUTCOME_EXCLUDE, item.reason, 0.99
    elif item.occurrences >= 2:
        outcome, reason, confidence = OUTCOME_OBSERVE, "repeated_unconfirmed_wording", 0.80
    else:
        outcome, reason, confidence = OUTCOME_EXCLUDE, "ordinary_or_low_impact_wording", 0.95
    return CaptureOutcome(
        term=item.term,
        normalized=item.normalized,
        outcome=outcome,
        reason=reason,
        impact="low",
        confidence=confidence,
        occurrences=item.occurrences,
        registered=False,
    )


def analyze_capture_outcomes(
    text: str,
    registered_terms: Iterable[str] | None = None,
) -> CaptureAnalysis:
    registered = {normalize_term(term) for term in (registered_terms or ()) if normalize_term(term)}
    classified = extract_classified_terms(text, registered)
    classified_by_term = {item.normalized: item for item in classified}
    signals = extract_context_signals(text)
    results: list[CaptureOutcome] = []
    consumed: set[str] = set()

    for signal in signals:
        item = classified_by_term.get(signal.normalized)
        occurrences = item.occurrences if item is not None else max(1, len(re.findall(re.escape(signal.term), text, re.IGNORECASE)))
        results.append(_from_signal(signal, registered=signal.normalized in registered, occurrences=occurrences))
        consumed.add(signal.normalized)

    for term, count in extract_registered_matches(text, registered):
        if term in consumed:
            continue
        results.append(
            CaptureOutcome(
                term=term,
                normalized=term,
                outcome=OUTCOME_EXISTING_MATCH,
                reason="registered_term_match",
                impact="medium",
                confidence=1.0,
                occurrences=count,
                registered=True,
            )
        )
        consumed.add(term)

    for term, normalized, count in extract_repeated_observations(text):
        if normalized in consumed or normalized in registered:
            continue
        results.append(
            CaptureOutcome(
                term=term,
                normalized=normalized,
                outcome=OUTCOME_OBSERVE,
                reason="repeated_unconfirmed_wording",
                impact="low",
                confidence=0.80,
                occurrences=count,
                registered=False,
            )
        )
        consumed.add(normalized)

    for item in classified:
        if item.normalized not in consumed:
            results.append(_from_classified(item))

    priority = {
        OUTCOME_EXCEPTION: 0,
        OUTCOME_EXISTING_MATCH: 1,
        OUTCOME_OBSERVE: 2,
        OUTCOME_EXCLUDE: 3,
    }
    results.sort(key=lambda item: (priority[item.outcome], -item.occurrences, item.normalized))
    return CaptureAnalysis(results=tuple(results))
