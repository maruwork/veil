"""Validate and merge the v8 independently reviewed corpus before freeze.

This tool reads only the selected anonymized source and G5 review artifacts.
It does not read the canonical DB, freeze inputs, generate frames, or evaluate
outcomes.  A merged corpus is written only after two separately authored
reviews agree on source linkage, exact evidence, frame, and matrix outcome.
"""

from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import json
from pathlib import Path
import re
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
VERDICT_FIELDS = {
    "case_id", "session_id", "context", "term", "registered_terms", "review_frame",
    "expected_outcome", "reviewer", "verdict", "reason",
}
FRAME_FIELDS = {
    "term", "intent", "persistence", "polarity", "scope", "impact", "term_evidence",
    "intent_evidence", "confidence",
}
OUTCOMES = {"exclude", "observe", "existing-match", "exception"}
SCOPE_ID = "20260722-real-conversation-ux-v8"


def valid_reviewer_id(value: Any, role: str) -> bool:
    return isinstance(value, str) and re.fullmatch(rf"reviewer-{role}-v8(?:-r[1-9][0-9]*)?", value) is not None


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
    intent_evidence = frame["intent_evidence"]
    if not isinstance(intent_evidence, list) or not intent_evidence or any(
        not occurrence_exists(context, item) for item in intent_evidence
    ):
        raise ValueError("review_frame intent evidence is not exact")
    return frame


def derive_outcome(frame: dict[str, Any], *, registered: bool) -> str:
    """Implement the ordered rows of the reviewed-label contract."""
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


def validate_snapshot(snapshot: dict[str, Any]) -> set[str]:
    if set(snapshot) != SNAPSHOT_FIELDS or snapshot["contract_version"] != "2":
        raise ValueError("canonical snapshot field contract is invalid")
    if not isinstance(snapshot["read_at"], str) or not snapshot["read_at"]:
        raise ValueError("canonical snapshot read_at is invalid")
    if snapshot["source"] != "read-only canonical DB readback":
        raise ValueError("canonical snapshot source is invalid")
    values = snapshot["normalized_active_terms"]
    if not isinstance(values, list) or any(not isinstance(value, str) or not value for value in values):
        raise ValueError("canonical snapshot terms are invalid")
    active = [normalize_term(value) for value in values]
    if any(not value for value in active) or len(active) != len(set(active)) or active != values:
        raise ValueError("canonical snapshot terms must be normalized and unique")
    return set(active)


def validate_reviewed_corpus(
    *, source_path: Path, snapshot_path: Path, reviewer_a_path: Path, reviewer_b_path: Path
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    sources = read_jsonl(source_path)
    if len(sources) != 1 or set(sources[0]) != SOURCE_FIELDS:
        raise ValueError("source must contain exactly one exact-shape row")
    source = sources[0]
    if not all(isinstance(source[name], str) and source[name] for name in SOURCE_FIELDS):
        raise ValueError("source row is invalid")
    active = validate_snapshot(read_json(snapshot_path))
    reviewer_a, reviewer_b = read_jsonl(reviewer_a_path), read_jsonl(reviewer_b_path)
    if not reviewer_a or len(reviewer_a) != len(reviewer_b):
        raise ValueError("Reviewer A and Reviewer B row counts differ")

    b_by_term: dict[tuple[str, str], dict[str, Any]] = {}
    for row in reviewer_b:
        if set(row) != VERDICT_FIELDS or not isinstance(row.get("case_id"), str) or not row["case_id"]:
            raise ValueError("Reviewer B verdict row is invalid")
        session_id, term = row.get("session_id"), row.get("term")
        if not isinstance(session_id, str) or not session_id or not isinstance(term, str) or not term:
            raise ValueError("Reviewer B source or primary term is invalid")
        key = (session_id, normalize_term(term))
        if not key[1] or key in b_by_term:
            raise ValueError("Reviewer B primary term is empty or duplicate")
        b_by_term[key] = row

    merged: list[dict[str, Any]] = []
    seen_terms: set[str] = set()
    for row in reviewer_a:
        if set(row) != CORPUS_FIELDS or row.get("contract_version") != "2":
            raise ValueError("Reviewer A corpus row field contract is invalid")
        if not isinstance(row.get("case_id"), str) or not row["case_id"]:
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
        registered_terms = row.get("registered_terms")
        expected_registered = [normalized] if normalized in active else []
        if registered_terms != expected_registered:
            raise ValueError("Reviewer A registered terms do not match the snapshot")
        frame = validate_frame(row.get("review_frame"), context=row["context"], term=term)
        expected = derive_outcome(frame, registered=bool(registered_terms))
        if row.get("expected_outcome") != expected or expected not in OUTCOMES:
            raise ValueError("Reviewer A outcome does not follow the matrix")
        if row.get("impact") != frame["impact"] or not isinstance(row.get("reason"), str) or not row["reason"].strip():
            raise ValueError("Reviewer A impact or rationale is invalid")
        if row.get("source_class") != "anonymized-real-conversation":
            raise ValueError("Reviewer A source class is invalid")
        reviewer = row.get("reviewer")
        if not isinstance(reviewer, dict) or not valid_reviewer_id(reviewer.get("id"), "a") or not isinstance(reviewer.get("reviewed_at"), str):
            raise ValueError("Reviewer A identity is invalid")
        if row.get("second_review") != "pending":
            raise ValueError("Reviewer A artifact must remain pre-B pending")
        if row.get("provenance") != {"kind": "anonymized-real-conversation", "scope_id": SCOPE_ID, "contains_real_conversation": True}:
            raise ValueError("Reviewer A provenance is invalid")

        b = b_by_term.pop((row["session_id"], normalized), None)
        if b is None:
            if any(session == row["session_id"] for session, _ in b_by_term):
                raise ValueError("Reviewer B primary target differs from Reviewer A")
            raise ValueError("Reviewer A case has no Reviewer B verdict")
        if b.get("session_id") != source["session_id"] or b.get("context") != source["source_text"] or b.get("term") != term:
            raise ValueError("Reviewer B source linkage or primary target differs from Reviewer A")
        if b.get("registered_terms") != expected_registered:
            raise ValueError("Reviewer B registered terms do not match the snapshot")
        b_frame = validate_frame(b.get("review_frame"), context=b["context"], term=b["term"])
        b_expected = derive_outcome(b_frame, registered=bool(b["registered_terms"]))
        if b.get("expected_outcome") != b_expected:
            raise ValueError("Reviewer B outcome does not follow the matrix")
        for name in ("session_id", "context", "term", "registered_terms", "expected_outcome"):
            if b.get(name) != row.get(name):
                raise ValueError("Reviewer B does not agree with Reviewer A evidence or outcome")
        if b.get("verdict") != "agree" or not isinstance(b.get("reason"), str) or not b["reason"].strip():
            raise ValueError("Reviewer B verdict is not an agreement with rationale")
        b_reviewer = b.get("reviewer")
        if not isinstance(b_reviewer, dict) or not valid_reviewer_id(b_reviewer.get("id"), "b") or not isinstance(b_reviewer.get("reviewed_at"), str):
            raise ValueError("Reviewer B identity is invalid")
        if b_reviewer["id"] == reviewer["id"]:
            raise ValueError("Reviewer identities must be distinct")
        merged.append({**row, "second_review": {"required": True, "reviewer_id": b_reviewer["id"], "verdict": "agree", "reason": b["reason"], "reviewed_at": b_reviewer["reviewed_at"]}})
    if b_by_term:
        raise ValueError("Reviewer B contains an unknown case")
    report = {
        "status": "passed",
        "validated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "case_count": len(merged), "session_count": 1,
        "outcome_counts": dict(sorted(Counter(row["expected_outcome"] for row in merged).items())),
        "impact_counts": dict(sorted(Counter(row["impact"] for row in merged).items())),
        "second_review_counts": {"agree": len(merged)},
        "reviewer_ids": sorted({row["reviewer"]["id"] for row in merged} | {row["second_review"]["reviewer_id"] for row in merged}),
    }
    return merged, report


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate and merge v8 two-reviewer corpus artifacts.")
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
    merged, report = validate_reviewed_corpus(source_path=args.source.resolve(), snapshot_path=args.snapshot.resolve(), reviewer_a_path=args.reviewer_a.resolve(), reviewer_b_path=args.reviewer_b.resolve())
    output.mkdir(parents=True, exist_ok=True)
    corpus_path.write_text("".join(json.dumps(row, ensure_ascii=True, sort_keys=True) + "\n" for row in merged), encoding="utf-8")
    report_path.write_text(json.dumps(report, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=True, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
