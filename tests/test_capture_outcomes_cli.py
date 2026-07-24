from __future__ import annotations

import json
from pathlib import Path

from .helpers import classify_cmd, db_cmd


def test_outcomes_cli_requires_no_question_for_background_observation() -> None:
    result = classify_cmd(
        "--text",
        "root clutter root clutter should be reviewed later.",
        "--outcomes",
        "--db",
        "does-not-exist.db",
        "--json",
    )
    payload = json.loads(result.stdout)

    assert payload["contract_version"] == "1"
    assert payload["analysis_mode"] == "raw-text-diagnostic"
    assert payload["diagnostic_only"] is True
    assert payload["write_allowed"] is False
    assert payload["summary"]["user_action_required"] is False
    assert payload["summary"]["question_count"] == 0
    assert payload["summary"]["counts"]["observe"] >= 1


def test_outcomes_cli_batches_high_impact_exceptions() -> None:
    result = classify_cmd(
        "--text",
        "Use decision boundary consistently. Always use release boundary.",
        "--outcomes",
        "--db",
        "does-not-exist.db",
        "--json",
    )
    payload = json.loads(result.stdout)

    assert payload["summary"]["user_action_required"] is True
    assert payload["summary"]["question_count"] == 1
    assert {item["normalized"] for item in payload["exceptions"]} == {
        "decision boundary",
        "release boundary",
    }


def test_outcomes_cli_resolves_registered_term_without_question(tmp_db: str) -> None:
    db_cmd("upsert-rule", "--db", tmp_db, "--term", "current state", "--preferred", "current state")
    result = classify_cmd(
        "--text",
        "Use current state consistently in every handoff.",
        "--outcomes",
        "--db",
        tmp_db,
        "--json",
    )
    payload = json.loads(result.stdout)

    assert payload["summary"]["user_action_required"] is False
    assert payload["summary"]["counts"]["existing-match"] == 1


def test_outcomes_cli_plain_output_hides_candidate_table() -> None:
    result = classify_cmd(
        "--text",
        "root clutter root clutter should be reviewed later.",
        "--outcomes",
        "--db",
        "does-not-exist.db",
    )

    assert result.stdout.startswith("NO-ACTION ")
    assert "Candidate" not in result.stdout


def test_outcomes_cli_preserves_quoted_explicit_intent() -> None:
    result = classify_cmd(
        "--text",
        'Use "decision boundary" consistently.',
        "--outcomes",
        "--db",
        "does-not-exist.db",
        "--json",
    )
    payload = json.loads(result.stdout)

    assert [item["normalized"] for item in payload["exceptions"]] == ["decision boundary"]
    assert payload["summary"]["question_count"] == 1


def test_outcomes_cli_registered_change_is_exception(tmp_db: str) -> None:
    db_cmd("upsert-rule", "--db", tmp_db, "--term", "current state", "--preferred", "present state")
    result = classify_cmd(
        "--text",
        "Change current state to present condition.",
        "--outcomes",
        "--db",
        tmp_db,
        "--json",
    )
    payload = json.loads(result.stdout)

    assert [item["normalized"] for item in payload["exceptions"]] == ["current state"]
    assert payload["exceptions"][0]["requested_preferred"] == "present condition"


def test_outcomes_cli_registered_mapping_is_exception(tmp_db: str) -> None:
    db_cmd("upsert-rule", "--db", tmp_db, "--term", "current state", "--preferred", "present state")
    result = classify_cmd(
        "--text",
        "Register current state as present state in VEIL.",
        "--outcomes",
        "--db",
        tmp_db,
        "--json",
    )
    payload = json.loads(result.stdout)

    assert [item["normalized"] for item in payload["exceptions"]] == ["current state"]
    assert payload["exceptions"][0]["requested_preferred"] == "present state"


def _write_semantic_payload(path: Path, payload: dict[str, object]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


def _semantic_rename_payload(source: str) -> dict[str, object]:
    return {
        "contract_version": "2",
        "frames": [
            {
                "frame_id": "f1",
                "term": "current state",
                "intent": "rename",
                "persistence": "durable",
                "polarity": "affirmed",
                "scope": "project",
                "from_term": "current state",
                "preferred": "present state",
                "conflict_group": None,
                "impact": "medium",
                "term_evidence": {"text": source, "occurrence": 1},
                "intent_evidence": [{"text": source, "occurrence": 1}],
                "confidence": "high",
            }
        ],
        "critic": {
            "status": "confirmed",
            "confirmed_frame_ids": ["f1"],
            "rejected_frame_ids": [],
            "unresolved_frame_ids": [],
            "missing_frames": [],
        },
    }


def test_semantic_frames_cli_applies_contract_v2_without_writing(tmp_path: Path, tmp_db: str) -> None:
    source = "Rename current state to present state for future reports."
    frames_path = tmp_path / "frames.json"
    _write_semantic_payload(frames_path, _semantic_rename_payload(source))
    db_cmd("upsert-rule", "--db", tmp_db, "--term", "current state", "--preferred", "current state")
    db_path = Path(tmp_db)
    before_bytes = db_path.read_bytes()
    before_mtime = db_path.stat().st_mtime_ns

    result = classify_cmd(
        "--text",
        source,
        "--outcomes",
        "--semantic-frames",
        str(frames_path),
        "--db",
        tmp_db,
        "--json",
    )
    payload = json.loads(result.stdout)

    assert payload["contract_version"] == "2"
    assert payload["analysis_mode"] == "semantic-frames"
    assert payload["diagnostic_only"] is False
    assert payload["write_allowed"] is False
    assert payload["status"] == "ok"
    assert payload["summary"]["question_count"] == 1
    assert payload["exceptions"][0]["requested_preferred"] == "present state"
    assert db_path.read_bytes() == before_bytes
    assert db_path.stat().st_mtime_ns == before_mtime


def test_semantic_frames_cli_does_not_run_legacy_lexical_parser(tmp_path: Path) -> None:
    source = "The person's authentication factor, and its age, were logged."
    frames_path = tmp_path / "frames.json"
    _write_semantic_payload(
        frames_path,
        {
            "contract_version": "2",
            "frames": [],
            "critic": {
                "status": "confirmed",
                "confirmed_frame_ids": [],
                "rejected_frame_ids": [],
                "unresolved_frame_ids": [],
                "missing_frames": [],
            },
        },
    )

    result = classify_cmd(
        "--text",
        source,
        "--outcomes",
        "--semantic-frames",
        str(frames_path),
        "--db",
        "does-not-exist.db",
        "--json",
    )
    payload = json.loads(result.stdout)

    assert payload["results"] == []
    assert payload["summary"]["question_count"] == 0


def test_semantic_frames_cli_fails_closed_on_invalid_evidence(tmp_path: Path) -> None:
    source = "Use origin seal for every project handoff."
    frames_path = tmp_path / "frames.json"
    payload = _semantic_rename_payload("Rename current state to present state.")
    _write_semantic_payload(frames_path, payload)

    result = classify_cmd(
        "--text",
        source,
        "--outcomes",
        "--semantic-frames",
        str(frames_path),
        "--db",
        "does-not-exist.db",
        "--json",
        check=False,
    )
    error = json.loads(result.stdout)

    assert result.returncode == 2
    assert error["status"] == "error"
    assert error["write_allowed"] is False
    assert error["summary"]["question_count"] == 0
    assert error["exceptions"] == []
    assert any("does not exist in the exact input text" in item for item in error["errors"])


def test_semantic_frames_option_requires_outcomes(tmp_path: Path) -> None:
    frames_path = tmp_path / "frames.json"
    _write_semantic_payload(frames_path, {})

    result = classify_cmd(
        "--text",
        "ordinary text",
        "--semantic-frames",
        str(frames_path),
        check=False,
    )

    assert result.returncode == 2
    assert "requires --outcomes" in result.stderr
