#!/usr/bin/env python3
"""Prepare and judge the five-person VEIL HTML UX acceptance without PII."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from shared.tools.veil_html_assets import get_html_ui_for_lang
from shared.tools.veil_rule_store import export_html_from_db, init_db, upsert_rules_atomic


CONTRACT_VERSION = "1"
PARTICIPANT_COUNT = 5
TASK_IDS = ("find_preferred", "request_change", "review_conversation")
CONFUSION_CODES = {
    "rulebook_discovery",
    "change_request_route",
    "review_recovery_route",
    "copy_persistence",
    "negative_scope",
    "keyboard_operation",
    "other_design_confusion",
}
FIXTURE_RULES = [
    {
        "term": "current state",
        "preferred": "present state",
        "preferred_alt_2": "current status",
        "status": "active",
        "source_context": "human-ux-fixture",
    }
]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def source_revision(*, require_clean: bool) -> str:
    completed = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    revision = completed.stdout.strip()
    if completed.returncode != 0 or len(revision) != 40:
        raise RuntimeError("human_ux.git_head_unavailable")
    if require_clean:
        clean = subprocess.run(
            ["git", "diff", "--quiet", "HEAD", "--"],
            cwd=ROOT,
            check=False,
        )
        if clean.returncode != 0:
            raise RuntimeError("human_ux.tracked_source_dirty")
    return revision


def prepare_fixture(output_dir: Path, *, require_clean: bool = False) -> dict[str, Any]:
    """Create one static, disposable page for five independent sessions."""

    if output_dir.exists():
        raise RuntimeError("human_ux.fixture_output_exists")
    revision = source_revision(require_clean=require_clean)
    output_dir.mkdir(parents=True)
    try:
        with tempfile.TemporaryDirectory(prefix="veil-human-ux-") as temporary:
            temporary_dir = Path(temporary)
            db_path = temporary_dir / "fixture.db"
            html_path = output_dir / "veil-human-ux.html"
            init_db(str(db_path))
            seeded = upsert_rules_atomic(str(db_path), FIXTURE_RULES)
            if seeded.get("status") != "ok":
                raise RuntimeError(f"human_ux.fixture_seed_failed:{seeded}")
            exported = export_html_from_db(
                str(db_path),
                str(html_path),
                ui=get_html_ui_for_lang("en"),
            )
            if exported.get("status") != "ok":
                raise RuntimeError(f"human_ux.fixture_export_failed:{exported}")

        manifest = {
            "contract_version": CONTRACT_VERSION,
            "fixture_id": output_dir.name,
            "source_revision": revision,
            "created_at": utc_now(),
            "html": {
                "filename": html_path.name,
                "sha256": sha256_bytes(html_path.read_bytes()),
            },
            "fixture_rules": [
                {"term": item["term"], "preferred": item["preferred"]}
                for item in FIXTURE_RULES
            ],
            "participant_count_required": PARTICIPANT_COUNT,
            "pii_policy": "Do not record names, contact details, transcripts, or free-text notes.",
        }
        manifest_path = output_dir / "fixture-manifest.json"
        manifest_bytes = (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
        manifest_path.write_bytes(manifest_bytes)
        records_template = {
            "contract_version": CONTRACT_VERSION,
            "fixture_manifest_sha256": sha256_bytes(manifest_bytes),
            "source_revision": revision,
            "participants": [],
        }
        (output_dir / "records-template.json").write_text(
            json.dumps(records_template, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        return manifest
    except Exception:
        # A partial fixture cannot be a valid acceptance input.
        for child in output_dir.iterdir():
            child.unlink()
        output_dir.rmdir()
        raise


def _issue(issues: list[dict[str, str]], code: str, detail: str) -> None:
    issues.append({"code": code, "detail": detail})


def evaluate_records(fixture_manifest: Path, records_path: Path) -> dict[str, Any]:
    """Fail closed unless five anonymous, independent sessions meet every gate."""

    issues: list[dict[str, str]] = []
    try:
        fixture = load_json(fixture_manifest)
        records = load_json(records_path)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        return {
            "contract_version": CONTRACT_VERSION,
            "status": "evidence-incomplete",
            "release_status": "not-ready",
            "issues": [{"code": "human_ux.unreadable_input", "detail": str(exc)}],
        }

    fixture_sha = sha256_bytes(fixture_manifest.read_bytes())
    if not isinstance(fixture, dict) or fixture.get("contract_version") != CONTRACT_VERSION:
        _issue(issues, "human_ux.fixture_contract", "fixture contract_version is invalid")
    if not isinstance(records, dict) or records.get("contract_version") != CONTRACT_VERSION:
        _issue(issues, "human_ux.records_contract", "records contract_version is invalid")
        participants: Any = []
    else:
        participants = records.get("participants")
    if not isinstance(records, dict) or records.get("fixture_manifest_sha256") != fixture_sha:
        _issue(issues, "human_ux.fixture_mismatch", "records are not bound to this fixture manifest")
    if isinstance(fixture, dict) and isinstance(records, dict) and records.get("source_revision") != fixture.get("source_revision"):
        _issue(issues, "human_ux.source_revision_mismatch", "records and fixture source revisions differ")
    if not isinstance(participants, list) or len(participants) != PARTICIPANT_COUNT:
        _issue(issues, "human_ux.participant_count", f"exactly {PARTICIPANT_COUNT} participants are required")
        participants = []

    seen_ids: set[str] = set()
    task_success = {task_id: 0 for task_id in TASK_IDS}
    belief_violations = {"no_match_proves_no_review_needed": 0, "copy_saved_a_rule": 0}
    negative_scope_success = 0
    confusion_count = 0

    for index, participant in enumerate(participants, start=1):
        prefix = f"participant[{index}]"
        if not isinstance(participant, dict):
            _issue(issues, "human_ux.participant_shape", f"{prefix} is not an object")
            continue
        unexpected_fields = set(participant) - {
            "participant_id",
            "target_user",
            "is_page_author",
            "tasks",
            "beliefs",
            "confusion_codes",
        }
        if unexpected_fields:
            _issue(
                issues,
                "human_ux.participant_extra_field",
                f"{prefix}:{','.join(sorted(unexpected_fields))}",
            )
        participant_id = participant.get("participant_id")
        if not isinstance(participant_id, str) or not participant_id or len(participant_id) > 32:
            _issue(issues, "human_ux.participant_id", f"{prefix} has an invalid anonymous ID")
            continue
        if participant_id in seen_ids:
            _issue(issues, "human_ux.duplicate_participant", participant_id)
        seen_ids.add(participant_id)
        if participant.get("target_user") is not True or participant.get("is_page_author") is not False:
            _issue(issues, "human_ux.participant_eligibility", participant_id)

        tasks = participant.get("tasks")
        if not isinstance(tasks, dict):
            _issue(issues, "human_ux.tasks_shape", participant_id)
            tasks = {}
        for task_id in TASK_IDS:
            task = tasks.get(task_id)
            if not isinstance(task, dict):
                _issue(issues, "human_ux.task_missing", f"{participant_id}:{task_id}")
                continue
            if set(task) - {"completed", "moderator_navigation_help"}:
                _issue(issues, "human_ux.task_extra_field", f"{participant_id}:{task_id}")
            completed = task.get("completed") is True
            navigation_help = task.get("moderator_navigation_help") is True
            if completed and not navigation_help:
                task_success[task_id] += 1
            elif navigation_help:
                _issue(issues, "human_ux.moderator_navigation_help", f"{participant_id}:{task_id}")

        beliefs = participant.get("beliefs")
        if not isinstance(beliefs, dict):
            _issue(issues, "human_ux.beliefs_shape", participant_id)
            beliefs = {}
        if set(beliefs) - {
            "no_match_proves_no_review_needed",
            "copy_saved_a_rule",
            "knows_when_not_to_open_html",
        }:
            _issue(issues, "human_ux.belief_extra_field", participant_id)
        if beliefs.get("no_match_proves_no_review_needed") is True:
            belief_violations["no_match_proves_no_review_needed"] += 1
        if beliefs.get("copy_saved_a_rule") is True:
            belief_violations["copy_saved_a_rule"] += 1
        if beliefs.get("knows_when_not_to_open_html") is True:
            negative_scope_success += 1

        codes = participant.get("confusion_codes", [])
        if not isinstance(codes, list) or not all(isinstance(code, str) for code in codes):
            _issue(issues, "human_ux.confusion_shape", participant_id)
            continue
        unexpected = sorted(set(codes) - CONFUSION_CODES)
        if unexpected:
            _issue(issues, "human_ux.confusion_code", f"{participant_id}:{','.join(unexpected)}")
        confusion_count += len(set(codes))

    for task_id, count in task_success.items():
        if count < 4:
            _issue(issues, "human_ux.task_threshold", f"{task_id}={count}/5")
    for belief, count in belief_violations.items():
        if count:
            _issue(issues, "human_ux.misconception", f"{belief}={count}")
    if negative_scope_success < 4:
        _issue(issues, "human_ux.negative_scope_threshold", f"{negative_scope_success}/5")
    if confusion_count:
        _issue(
            issues,
            "human_ux.unresolved_design_confusion",
            "a new source revision and a fresh five-person run are required",
        )

    evidence_codes = {
        "human_ux.unreadable_input",
        "human_ux.fixture_contract",
        "human_ux.records_contract",
        "human_ux.fixture_mismatch",
        "human_ux.source_revision_mismatch",
        "human_ux.participant_count",
        "human_ux.participant_shape",
        "human_ux.participant_id",
        "human_ux.duplicate_participant",
        "human_ux.tasks_shape",
        "human_ux.task_missing",
        "human_ux.beliefs_shape",
        "human_ux.confusion_shape",
    }
    status = "human-ux-passed"
    if any(issue["code"] in evidence_codes for issue in issues):
        status = "evidence-incomplete"
    elif issues:
        status = "requires-revision"
    return {
        "contract_version": CONTRACT_VERSION,
        "status": status,
        "release_status": "not-ready",
        "fixture_manifest_sha256": fixture_sha,
        "source_revision": fixture.get("source_revision") if isinstance(fixture, dict) else None,
        "participant_count": len(participants),
        "task_success_without_navigation_help": task_success,
        "misconception_counts": belief_violations,
        "knows_when_not_to_open_html": negative_scope_success,
        "observed_confusion_count": confusion_count,
        "issues": issues,
        "limitations": [
            "This verdict qualifies only the five-person HTML UX gate.",
            "It never upgrades the product release status by itself.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subcommands = parser.add_subparsers(dest="command", required=True)
    prepare = subcommands.add_parser("prepare", help="Create a one-run disposable human UX fixture.")
    prepare.add_argument("--output-dir", type=Path, required=True)
    evaluate = subcommands.add_parser("evaluate", help="Evaluate five anonymous participant records.")
    evaluate.add_argument("--fixture-manifest", type=Path, required=True)
    evaluate.add_argument("--records", type=Path, required=True)
    evaluate.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    if args.command == "prepare":
        print(
            json.dumps(
                prepare_fixture(args.output_dir, require_clean=True),
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0
    report = evaluate_records(args.fixture_manifest, args.records)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["status"] == "human-ux-passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
