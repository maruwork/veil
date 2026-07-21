from __future__ import annotations

from dataclasses import asdict, dataclass
import re
from typing import Any

try:
    from shared.tools.veil_capture_taxonomy import (
        ALL_LABELS,
        ADOPTABLE_OTHER_MULTIWORD_TERMS,
        GENERIC_SINGLE_WORDS,
        IDENTIFIER_TOKEN_RE,
        KNOWN_COINED_TERMS,
        KNOWN_FILE_CONFIG_TERMS,
        KNOWN_INDUSTRY_ACRONYMS,
        KNOWN_INDUSTRY_TERMS,
        KNOWN_OTHER_MULTIWORD_TERMS,
        KNOWN_REPO_DIR_TERMS,
        LABEL_COINED_OR_SHORTENED,
        LABEL_FILE_CONFIG_IDENTIFIER,
        LABEL_INDUSTRY_TERM,
        LABEL_OTHER,
        LABEL_UNKNOWN,
        PREVIEWABLE_GENERIC_SINGLE_TERMS,
        PROPER_NOUN_TERMS,
        SHORTENED_TERMS,
        WORD_TOKEN_RE,
    )
except ModuleNotFoundError:
    from veil_capture_taxonomy import (  # type: ignore[no-redef]
        ALL_LABELS,
        ADOPTABLE_OTHER_MULTIWORD_TERMS,
        GENERIC_SINGLE_WORDS,
        IDENTIFIER_TOKEN_RE,
        KNOWN_COINED_TERMS,
        KNOWN_FILE_CONFIG_TERMS,
        KNOWN_INDUSTRY_ACRONYMS,
        KNOWN_INDUSTRY_TERMS,
        KNOWN_OTHER_MULTIWORD_TERMS,
        KNOWN_REPO_DIR_TERMS,
        LABEL_COINED_OR_SHORTENED,
        LABEL_FILE_CONFIG_IDENTIFIER,
        LABEL_INDUSTRY_TERM,
        LABEL_OTHER,
        LABEL_UNKNOWN,
        PREVIEWABLE_GENERIC_SINGLE_TERMS,
        PROPER_NOUN_TERMS,
        SHORTENED_TERMS,
        WORD_TOKEN_RE,
    )
from shared.tools.veil_rule_store import normalize_term


@dataclass(frozen=True)
class ClassifiedTerm:
    term: str
    normalized: str
    label: str
    reason: str
    occurrences: int = 1
    registered: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _split_phrase_tokens(term: str) -> list[str]:
    return [token for token in normalize_term(term).split(" ") if token]


def sanitize_capture_text(text: str) -> str:
    return re.sub(
        r"\s+",
        " ",
        re.sub(
            r"\(line\s+\d+\)",
            " ",
            re.sub(
            r"\b[a-z0-9_]+=([^\s]+)",
            " ",
            re.sub(
                r"`[^`]*`",
                " ",
                re.sub(
                    r"\[([^\]]+)\]\([^)]+\)",
                    r"\1",
                    re.sub(r"```[\s\S]*?```", " ", text or ""),
                ),
            ),
            flags=re.IGNORECASE,
            ),
        ),
    ).strip()


def _identifier_reason(term: str) -> str | None:
    stripped = term.strip()
    if not stripped:
        return None
    has_space = bool(re.search(r"\s", stripped))
    if any(char in stripped for char in ("/", "\\", "*")):
        return "path_or_glob_pattern"
    if "." in stripped and len(stripped) > 2:
        return "filename_or_dotted_identifier"
    if "_" in stripped:
        return "underscore_identifier"
    if not has_space and re.fullmatch(r"[0-9a-fA-F]{7,40}", stripped):
        return "hex_identifier"
    if not has_space and stripped.isupper() and len(stripped) >= 2:
        return "uppercase_identifier"
    if not has_space and re.search(r"[a-z][A-Z]|[A-Z][a-z].*[A-Z]", stripped):
        return "camel_or_mixed_case_identifier"
    return None


def classify_term(term: str, registered_terms: set[str] | None = None) -> ClassifiedTerm:
    raw = re.sub(r"\s+", " ", term.strip())
    normalized = normalize_term(raw)
    registered = bool(registered_terms and normalized in registered_terms)
    tokens = _split_phrase_tokens(raw)

    if not normalized:
        return ClassifiedTerm(
            term=raw,
            normalized=normalized,
            label=LABEL_UNKNOWN,
            reason="empty_after_normalization",
            registered=registered,
        )

    if normalized in PROPER_NOUN_TERMS:
        return ClassifiedTerm(
            term=raw,
            normalized=normalized,
            label=LABEL_OTHER,
            reason="proper_noun_non_target",
            registered=registered,
        )

    if normalized in KNOWN_INDUSTRY_ACRONYMS and raw.isupper():
        return ClassifiedTerm(
            term=raw,
            normalized=normalized,
            label=LABEL_INDUSTRY_TERM,
            reason="known_industry_acronym",
            registered=registered,
        )

    if normalized in KNOWN_REPO_DIR_TERMS:
        return ClassifiedTerm(
            term=raw,
            normalized=normalized,
            label=LABEL_FILE_CONFIG_IDENTIFIER,
            reason="repo_directory_identifier",
            registered=registered,
        )

    if normalized in KNOWN_FILE_CONFIG_TERMS:
        return ClassifiedTerm(
            term=raw,
            normalized=normalized,
            label=LABEL_FILE_CONFIG_IDENTIFIER,
            reason="config_term",
            registered=registered,
        )

    if normalized in KNOWN_INDUSTRY_TERMS:
        return ClassifiedTerm(
            term=raw,
            normalized=normalized,
            label=LABEL_INDUSTRY_TERM,
            reason="known_industry_term",
            registered=registered,
        )

    if normalized in SHORTENED_TERMS:
        return ClassifiedTerm(
            term=raw,
            normalized=normalized,
            label=LABEL_COINED_OR_SHORTENED,
            reason="common_shortened_form",
            registered=registered,
        )

    if len(tokens) <= 1:
        if normalized in GENERIC_SINGLE_WORDS:
            return ClassifiedTerm(
                term=raw,
                normalized=normalized,
                label=LABEL_OTHER,
                reason="generic_single_word",
                registered=registered,
            )

    identifier_reason = _identifier_reason(raw)
    if identifier_reason is not None:
        return ClassifiedTerm(
            term=raw,
            normalized=normalized,
            label=LABEL_FILE_CONFIG_IDENTIFIER,
            reason=identifier_reason,
            registered=registered,
        )

    if len(tokens) <= 1:
        if len(normalized) <= 4:
            return ClassifiedTerm(
                term=raw,
                normalized=normalized,
                label=LABEL_UNKNOWN,
                reason="too_short_without_clear_signal",
                registered=registered,
            )
        return ClassifiedTerm(
            term=raw,
            normalized=normalized,
            label=LABEL_UNKNOWN,
                reason="single_word_without_clear_signal",
                registered=registered,
            )

    if normalized in KNOWN_COINED_TERMS:
        return ClassifiedTerm(
            term=raw,
            normalized=normalized,
            label=LABEL_COINED_OR_SHORTENED,
            reason="known_coined_phrase",
            registered=registered,
        )

    return ClassifiedTerm(
        term=raw,
        normalized=normalized,
        label=LABEL_OTHER,
        reason="ordinary_multiword_phrase",
        registered=registered,
    )


def is_adoptable_classified_term(item: ClassifiedTerm) -> bool:
    token_count = len(_split_phrase_tokens(item.term))
    if item.registered or item.occurrences < 2:
        return False
    if item.label in {LABEL_UNKNOWN, LABEL_FILE_CONFIG_IDENTIFIER}:
        return False
    if item.label == LABEL_COINED_OR_SHORTENED:
        return token_count > 1
    if item.label == LABEL_INDUSTRY_TERM:
        return False
    if item.label == LABEL_OTHER:
        return token_count > 1 and item.normalized in ADOPTABLE_OTHER_MULTIWORD_TERMS
    return False


def is_previewable_classified_term(item: ClassifiedTerm) -> bool:
    token_count = len(_split_phrase_tokens(item.term))
    if item.registered:
        return False
    if item.label == LABEL_INDUSTRY_TERM:
        return False
    if item.label == LABEL_UNKNOWN:
        return False
    if item.label == LABEL_FILE_CONFIG_IDENTIFIER:
        return token_count > 1 and item.normalized in KNOWN_FILE_CONFIG_TERMS
    if item.label == LABEL_COINED_OR_SHORTENED:
        return True
    if item.label == LABEL_OTHER:
        if token_count > 1:
            return item.normalized in KNOWN_OTHER_MULTIWORD_TERMS
        return item.normalized in PREVIEWABLE_GENERIC_SINGLE_TERMS
    return False


def _contains_japanese_script(text: str) -> bool:
    return bool(re.search(r"[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff]", text))


def is_investigable_classified_term(item: ClassifiedTerm, source_text: str) -> bool:
    token_count = len(_split_phrase_tokens(item.term))
    if item.registered:
        return False
    if item.label == LABEL_INDUSTRY_TERM:
        return False
    if item.reason == "proper_noun_non_target":
        return False
    if token_count > 1:
        return True
    if item.label == LABEL_OTHER:
        return item.normalized in PREVIEWABLE_GENERIC_SINGLE_TERMS
    if item.label == LABEL_UNKNOWN:
        return _contains_japanese_script(source_text) and bool(re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]*", item.term))
    return True


def extract_classified_terms(text: str, registered_terms: set[str] | None = None) -> list[ClassifiedTerm]:
    registered = registered_terms or set()
    text = sanitize_capture_text(text)
    if not text:
        return []
    items: dict[str, tuple[int, int, ClassifiedTerm]] = {}

    def record(term: str, position: int) -> None:
        classified = classify_term(term, registered)
        if not classified.normalized:
            return
        word_count = len(_split_phrase_tokens(classified.term))
        existing = items.get(classified.normalized)
        if existing is None:
            items[classified.normalized] = (1, position, classified)
            return
        count, first_position, current = existing
        replacement = current
        if word_count > len(_split_phrase_tokens(current.term)):
            replacement = classified
        items[classified.normalized] = (count + 1, min(position, first_position), replacement)

    def should_record_phrase(raw_tokens: list[str]) -> bool:
        if len(raw_tokens) <= 1:
            return True
        normalized_tokens = [normalize_term(token) for token in raw_tokens]
        if len(set(normalized_tokens)) == 1:
            return False
        normalized_phrase = normalize_term(" ".join(raw_tokens))
        phrase_label = classify_term(" ".join(raw_tokens), registered).label
        if phrase_label in {LABEL_INDUSTRY_TERM, LABEL_COINED_OR_SHORTENED}:
            return True
        if phrase_label == LABEL_FILE_CONFIG_IDENTIFIER and normalized_phrase in KNOWN_FILE_CONFIG_TERMS:
            return True
        if phrase_label == LABEL_OTHER and normalized_phrase in KNOWN_OTHER_MULTIWORD_TERMS:
            return True
        labels = [classify_term(token, registered).label for token in raw_tokens]
        if LABEL_FILE_CONFIG_IDENTIFIER in labels:
            return False
        if any(token in SHORTENED_TERMS for token in normalized_tokens[1:]):
            return False
        if "-" in raw_tokens[1]:
            return False
        return False

    masked = text
    for match in IDENTIFIER_TOKEN_RE.finditer(text):
        record(match.group(0), match.start())
        start, end = match.span()
        masked = masked[:start] + (" " * (end - start)) + masked[end:]

    for line in masked.splitlines():
        word_matches = list(WORD_TOKEN_RE.finditer(line))
        tokens = [{"text": match.group(0), "start": match.start()} for match in word_matches]
        for window_size in (3, 2):
            for idx in range(len(tokens) - window_size + 1):
                window = tokens[idx : idx + window_size]
                raw_tokens = [token["text"] for token in window]
                if should_record_phrase(raw_tokens):
                    record(" ".join(raw_tokens), window[0]["start"])
        for token in tokens:
            raw = token["text"]
            if len(raw) == 1:
                continue
            if len(raw) < 4 and not raw.isupper():
                continue
            record(raw, token["start"])

    provisional: list[ClassifiedTerm] = []
    for count, _, classified in sorted(items.values(), key=lambda item: (item[1], -len(item[2].term), item[2].term.lower())):
        provisional.append(
            ClassifiedTerm(
                term=classified.term,
                normalized=classified.normalized,
                label=classified.label,
                reason=classified.reason,
                occurrences=count,
                registered=classified.registered,
            )
        )

    multiword_candidates = [
        item
        for item in provisional
        if len(_split_phrase_tokens(item.term)) > 1
        and (
            item.label in {LABEL_COINED_OR_SHORTENED, LABEL_INDUSTRY_TERM}
            or (item.label == LABEL_OTHER and item.normalized in KNOWN_OTHER_MULTIWORD_TERMS)
        )
    ]
    covered_single_tokens = {
        token
        for item in multiword_candidates
        for token in _split_phrase_tokens(item.term)
    }
    longer_multiword_prefixes = {
        item.normalized
        for item in multiword_candidates
        if any(other.normalized.startswith(item.normalized + " ") for other in multiword_candidates if other.normalized != item.normalized)
    }

    results: list[ClassifiedTerm] = []
    for item in provisional:
        token_count = len(_split_phrase_tokens(item.term))
        if (
            token_count == 1
            and item.normalized in covered_single_tokens
            and item.label in {LABEL_OTHER, LABEL_UNKNOWN}
            and item.normalized not in PROPER_NOUN_TERMS
        ):
            continue
        if item.label in {LABEL_COINED_OR_SHORTENED, LABEL_INDUSTRY_TERM} and item.normalized in longer_multiword_prefixes:
            continue
        results.append(item)
    return results


def extract_classified_term_map(text: str, registered_terms: set[str] | None = None) -> dict[str, ClassifiedTerm]:
    return {item.normalized: item for item in extract_classified_terms(text, registered_terms)}


def extract_adoptable_terms(
    text: str,
    registered_terms: set[str] | None = None,
    *,
    limit: int = 5,
) -> list[ClassifiedTerm]:
    def label_priority(label: str) -> int:
        if label == LABEL_INDUSTRY_TERM:
            return 4
        if label == LABEL_COINED_OR_SHORTENED:
            return 3
        if label == LABEL_FILE_CONFIG_IDENTIFIER:
            return 2
        if label == LABEL_OTHER:
            return 1
        return 0

    results = [item for item in extract_classified_terms(text, registered_terms) if is_adoptable_classified_term(item)]
    results.sort(key=lambda item: (-label_priority(item.label), -item.occurrences, -len(item.term), item.term.lower()))
    return results[:limit]


def extract_investigation_terms(
    text: str,
    registered_terms: set[str] | None = None,
    *,
    limit: int = 8,
) -> list[ClassifiedTerm]:
    def label_priority(label: str) -> int:
        if label == LABEL_FILE_CONFIG_IDENTIFIER:
            return 5
        if label == LABEL_COINED_OR_SHORTENED:
            return 4
        if label == LABEL_UNKNOWN:
            return 3
        if label == LABEL_OTHER:
            return 2
        if label == LABEL_INDUSTRY_TERM:
            return 1
        return 0

    results = [item for item in extract_classified_terms(text, registered_terms) if is_investigable_classified_term(item, text)]
    covered_single_tokens = {
        token
        for item in results
        if len(_split_phrase_tokens(item.term)) > 1
        for token in _split_phrase_tokens(item.term)
    }
    results = [
        item
        for item in results
        if not (
            len(_split_phrase_tokens(item.term)) == 1
            and item.normalized in covered_single_tokens
        )
    ]
    results.sort(
        key=lambda item: (
            -label_priority(item.label),
            -item.occurrences,
            -len(_split_phrase_tokens(item.term)),
            -len(item.term),
            item.term.lower(),
        )
    )
    return results[:limit]


def extract_preview_terms(
    text: str,
    registered_terms: set[str] | None = None,
    *,
    limit: int = 5,
) -> list[ClassifiedTerm]:
    def label_priority(label: str) -> int:
        if label == LABEL_INDUSTRY_TERM:
            return 4
        if label == LABEL_COINED_OR_SHORTENED:
            return 3
        if label == LABEL_FILE_CONFIG_IDENTIFIER:
            return 2
        if label == LABEL_OTHER:
            return 1
        return 0

    results = [item for item in extract_classified_terms(text, registered_terms) if is_previewable_classified_term(item)]
    results.sort(key=lambda item: (-label_priority(item.label), -item.occurrences, -len(item.term), item.term.lower()))
    return results[:limit]
