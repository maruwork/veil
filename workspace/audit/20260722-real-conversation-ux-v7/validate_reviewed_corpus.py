"""Validate and merge the v7 independently reviewed corpus before freeze.

This tool never reads the canonical DB, freezes artifacts, generates frames,
or evaluates outcomes.  It accepts only the frozen G4 source and G5 review
artifacts, and produces a corpus only after an independently authored
Reviewer-B verdict agrees with Reviewer A's matrix-derived result.
"""

from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from shared.tools.veil_rule_store import normalize_term


SOURCE_FIELDS = {"session_id", "source_text"}
SNAPSHOT_FIELDS = {"contract_version", "read_at", "source", "normalized_active_terms"}
CORPUS_FIELDS = {
    "contract_version", "case_id", "session_id", "context", "term", "registered_terms",
    "expected_outcome", "impact", "reason", "source_class", "reviewer", "second_review",
    "provenance", "review_frame",
}
VERDICT_FIELDS = {"case_id", "session_id", "context", "term", "registered_terms", "review_frame", "expected_outcome", "reviewer", "verdict", "reason"}
FRAME_FIELDS = {"term", "intent", "persistence", "polarity", "scope", "impact", "term_evidence", "intent_evidence", "confidence"}
OUTCOMES = {"exclude", "observe", "existing-match", "exception"}


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path.name} must be a JSON object")
    return value


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            raise ValueError(f"{path.name}:{number}: blank line")
        value = json.loads(line)
        if not isinstance(value, dict):
            raise ValueError(f"{path.name}:{number}: row must be an object")
        rows.append(value)
    return rows


def occurrence_exists(context: str, evidence: Any) -> bool:
    if not isinstance(evidence, dict) or set(evidence) != {"text", "occurrence"}:
        return False
    text, occurrence = evidence["text"], evidence["occurrence"]
    if not isinstance(text, str) or not text or not isinstance(occurrence, int) or occurrence < 1:
        return False
    position = -1
    for _ in range(occurrence):
        position = context.find(text, position + 1)
        if position < 0:
            return False
    return True


def validate_frame(frame: Any, *, context: str, term: str) -> dict[str, Any]:
    if not isinstance(frame, dict) or set(frame) != FRAME_FIELDS:
        raise ValueError("review_frame field set is invalid")
    if frame["term"] != term:
        raise ValueError("review_frame term differs from corpus term")
    if frame["intent"] not in {"mention", "adopt", "rename", "define", "conflict"}:
        raise ValueError("review_frame intent is invalid")
    if frame["persistence"] not in {"none", "temporary", "durable", "unclear"}:
        raise ValueError("review_frame persistence is invalid")
    if frame["polarity"] not in {"affirmed", "negated", "reported"}:
        raise ValueError("review_frame polarity is invalid")
    if frame["scope"] not in {"one-off", "session", "project", "global", "unclear"}:
        raise ValueError("review_frame scope is invalid")
    if frame["impact"] not in {"low", "medium", "high"} or frame["confidence"] not in {"low", "medium", "high"}:
        raise ValueError("review_frame impact or confidence is invalid")
    if not occurrence_exists(context, frame["term_evidence"]):
        raise ValueError("review_frame term evidence is not exact")
    intents = frame["intent_evidence"]
    if not isinstance(intents, list) or not intents or any(not occurrence_exists(context, item) for item in intents):
        raise ValueError("review_frame intent evidence is not exact")
    return frame


def derive_outcome(frame: dict[str, Any], *, registered: bool) -> str:
    if frame["polarity"] in {"negated", "reported"} or frame["persistence"] == "none":
        return "exclude"
    if registered and frame["intent"] in {"mention", "adopt"}:
        return "existing-match"
    if frame["persistence"] == "temporary" or frame["scope"] == "one-off":
        return "observe"
    if frame["intent"] in {"adopt", "rename", "conflict"}:
        return "exception"
    if frame["intent"] == "define" and (frame["persistence"] == "durable" or frame["impact"] == "high"):
        return "exception"
    if frame["intent"] == "define":
        return "observe"
    if frame["intent"] == "mention" and frame["persistence"] == "unclear" and frame["confidence"] != "high":
        return "observe"
    return "exclude"


def validate_reviewed_corpus(
    *, source_path: Path, snapshot_path: Path, reviewer_a_path: Path, reviewer_b_path: Path
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    sources = read_jsonl(source_path)
    if len(sources) != 1 or set(sources[0]) != SOURCE_FIELDS:
        raise ValueError("source must contain exactly one exact-shape row")
    source = sources[0]
    if not isinstance(source["session_id"], str) or not source["session_id"] or not isinstance(source["source_text"], str) or not source["source_text"]:
        raise ValueError("source row is invalid")
    snapshot = read_json(snapshot_path)
    if set(snapshot) != SNAPSHOT_FIELDS or snapshot["contract_version"] != "2" or not isinstance(snapshot["normalized_active_terms"], list):
        raise ValueError("canonical snapshot is invalid")
    active = {normalize_term(value) for value in snapshot["normalized_active_terms"] if isinstance(value, str) and normalize_term(value)}
    reviewer_a = read_jsonl(reviewer_a_path)
    reviewer_b = read_jsonl(reviewer_b_path)
    if not reviewer_a or len(reviewer_a) != len(reviewer_b):
        raise ValueError("Reviewer A and Reviewer B row counts differ")
    b_by_term: dict[tuple[str, str], dict[str, Any]] = {}
    for row in reviewer_b:
        if set(row) != VERDICT_FIELDS or not isinstance(row.get("case_id"), str) or not row["case_id"]:
            raise ValueError("Reviewer B verdict row is invalid or duplicate")
        session_id, term = row.get("session_id"), row.get("term")
        if not isinstance(session_id, str) or not isinstance(term, str) or not term:
            raise ValueError("Reviewer B source or primary term is invalid")
        key = (session_id, normalize_term(term))
        if key in b_by_term:
            raise ValueError("Reviewer B primary term is duplicate")
        b_by_term[key] = row
    merged: list[dict[str, Any]] = []
    seen_terms: set[str] = set()
    for row in reviewer_a:
        if set(row) != CORPUS_FIELDS or row.get("contract_version") != "2":
            raise ValueError("Reviewer A corpus row field contract is invalid")
        case_id = row.get("case_id")
        if not isinstance(case_id, str) or not case_id:
            raise ValueError("Reviewer A case ID is invalid")
        if row.get("session_id") != source["session_id"] or row.get("context") != source["source_text"]:
            raise ValueError("Reviewer A source linkage is invalid")
        term = row.get("term")
        if not isinstance(term, str) or not term or term not in row["context"]:
            raise ValueError("Reviewer A primary term is invalid")
        normalized = normalize_term(term)
        if len(normalized) < 3 or normalized in seen_terms:
            raise ValueError("Reviewer A term is empty or duplicate")
        seen_terms.add(normalized)
        registered = row.get("registered_terms")
        if not isinstance(registered, list) or any(not isinstance(item, str) or normalize_term(item) not in active for item in registered):
            raise ValueError("Reviewer A registered terms are invalid")
        frame = validate_frame(row.get("review_frame"), context=row["context"], term=term)
        expected = derive_outcome(frame, registered=normalized in {normalize_term(item) for item in registered})
        if row.get("expected_outcome") != expected or expected not in OUTCOMES:
            raise ValueError("Reviewer A outcome does not follow the matrix")
        reviewer = row.get("reviewer")
        if not isinstance(reviewer, dict) or reviewer.get("id") != "reviewer-a-v7" or not isinstance(reviewer.get("reviewed_at"), str):
            raise ValueError("Reviewer A identity is invalid")
        if row.get("second_review") != "pending":
            raise ValueError("Reviewer A artifact must remain pre-B pending")
        if row.get("provenance") != {"kind": "anonymized-real-conversation", "scope_id": "20260722-real-conversation-ux-v7", "contains_real_conversation": True}:
            raise ValueError("Reviewer A provenance is invalid")
        b_key = (row["session_id"], normalized)
        b = b_by_term.pop(b_key, None)
        if b is None:
            if any(session == row["session_id"] for session, _term in b_by_term):
                raise ValueError("Reviewer B primary target differs from Reviewer A")
            raise ValueError("Reviewer A case has no Reviewer B verdict")
        b_frame = validate_frame(b.get("review_frame"), context=row["context"], term=term)
        if any(b.get(key) != row.get(key) for key in ("session_id", "context", "term", "registered_terms", "expected_outcome")) or b_frame != frame:
            raise ValueError("Reviewer B does not agree with Reviewer A evidence or outcome")
        if b.get("verdict") != "agree" or not isinstance(b.get("reason"), str) or not b["reason"].strip():
            raise ValueError("Reviewer B verdict is not an agreement with rationale")
        b_reviewer = b.get("reviewer")
        if not isinstance(b_reviewer, dict) or b_reviewer.get("id") != "reviewer-b-v7" or not isinstance(b_reviewer.get("reviewed_at"), str):
            raise ValueError("Reviewer B identity is invalid")
        if b_reviewer["id"] == reviewer["id"]:
            raise ValueError("Reviewer identities must be distinct")
        merged.append({**row, "second_review": {"required": True, "reviewer_id": b_reviewer["id"], "verdict": "agree", "reason": b["reason"], "reviewed_at": b_reviewer["reviewed_at"]}})
    if b_by_term:
        raise ValueError("Reviewer B contains an unknown case")
    report = {
        "status": "passed",
        "validated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "case_count": len(merged),
        "session_count": 1,
        "outcome_counts": dict(sorted(Counter(row["expected_outcome"] for row in merged).items())),
        "impact_counts": dict(sorted(Counter(row["impact"] for row in merged).items())),
        "second_review_counts": {"agree": len(merged)},
        "reviewer_ids": ["reviewer-a-v7", "reviewer-b-v7"],
    }
    return merged, report


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate and merge v7 two-reviewer corpus artifacts.")
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--snapshot", type=Path, required=True)
    parser.add_argument("--reviewer-a", type=Path, required=True)
    parser.add_argument("--reviewer-b", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    output = args.output_dir.resolve()
    corpus_path, report_path = output / "corpus.jsonl", output / "review-report.json"
    if corpus_path.exists() or report_path.exists():
        raise ValueError("reviewed corpus or report already exists")
    merged, report = validate_reviewed_corpus(
        source_path=args.source.resolve(), snapshot_path=args.snapshot.resolve(),
        reviewer_a_path=args.reviewer_a.resolve(), reviewer_b_path=args.reviewer_b.resolve(),
    )
    output.mkdir(parents=True, exist_ok=True)
    corpus_path.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in merged), encoding="utf-8")
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
