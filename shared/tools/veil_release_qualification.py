#!/usr/bin/env python3
"""Fail-closed operational release qualification for VEIL's declared scope."""

from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
CONTRACT_VERSION = "1"
REQUIRED_HOSTED_CHECKS = {
    "Analyze (actions)",
    "Analyze (python)",
    "CodeQL",
    "design-methodology",
    "smoke (3.8)",
    "smoke (3.11)",
    "smoke (3.12)",
    "windows",
}


def load_json(path: Path) -> Any:
    # PowerShell's UTF-8 output can carry a BOM. Delivery evidence is produced
    # on Windows, so accept either UTF-8 representation while retaining strict
    # JSON parsing for every other input error.
    return json.loads(path.read_text(encoding="utf-8-sig"))


def current_revision() -> str:
    completed = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        capture_output=True,
        check=False,
        text=True,
        encoding="utf-8",
    )
    revision = completed.stdout.strip()
    if completed.returncode != 0 or len(revision) != 40:
        raise RuntimeError("release.git_head_unavailable")
    return revision


def issue(items: list[dict[str, str]], code: str, detail: str) -> None:
    items.append({"code": code, "detail": detail})


def qualify(
    *,
    browser_record: dict[str, Any],
    integration_record: dict[str, Any],
    delivery_record: dict[str, Any],
    hosted_checks: list[dict[str, Any]],
    revision: str,
) -> dict[str, Any]:
    """Return ready only for the declared operational, non-semantic scope."""

    issues: list[dict[str, str]] = []
    expected_records = {
        "browser": browser_record,
        "integration": integration_record,
        "delivery": delivery_record,
    }
    for name, record in expected_records.items():
        if not isinstance(record, dict):
            issue(issues, "release.record_shape", name)
            continue
        if record.get("git_head", record.get("commit_sha")) != revision:
            issue(issues, "release.source_revision_mismatch", name)
        if record.get("controlled_sources_dirty") is True:
            issue(issues, "release.dirty_source", name)

    fingerprints = {
        record.get("source_fingerprint_sha256")
        for record in expected_records.values()
        if isinstance(record, dict)
    }
    if len(fingerprints) != 1 or None in fingerprints:
        issue(issues, "release.source_fingerprint_mismatch", "all three records must share one fingerprint")

    if browser_record.get("status") != "ok":
        issue(issues, "release.browser_status", str(browser_record.get("status")))
    if browser_record.get("functional_startup") != "ok" or browser_record.get("keyboard_startup") != "ok":
        issue(issues, "release.browser_startup", "functional and keyboard startup must both be ok")
    if browser_record.get("result", {}).get("ok") is not True or browser_record.get("keyboard_result", {}).get("ok") is not True:
        issue(issues, "release.browser_journey", "functional and keyboard journeys must both pass")

    required_integration = {
        "status": "ok",
        "temp_only": True,
        "applied_atomic": True,
        "before_freshness": "OK",
        "stale_before_regeneration": "STALE",
        "final_freshness": "OK",
        "changed_visible": True,
        "retired_hidden": True,
    }
    for field, expected in required_integration.items():
        if integration_record.get(field) != expected:
            issue(issues, "release.integration_contract", f"{field}={integration_record.get(field)!r}")

    if delivery_record.get("status") != "ok":
        issue(issues, "release.delivery_status", str(delivery_record.get("status")))
    delivery_items = delivery_record.get("veil_status", {}).get("items", [])
    if not delivery_items or any(item.get("level") != "OK" for item in delivery_items if isinstance(item, dict)):
        issue(issues, "release.delivery_freshness", "every required delivery member must be OK")

    if not hosted_checks:
        issue(issues, "release.hosted_checks_missing", "no hosted checks supplied")
    seen_checks: set[str] = set()
    for check in hosted_checks:
        if not isinstance(check, dict):
            issue(issues, "release.hosted_check_failed", "invalid check entry")
            continue
        name = check.get("name")
        if not isinstance(name, str):
            issue(issues, "release.hosted_check_failed", "unnamed check")
            continue
        seen_checks.add(name)
        if check.get("bucket") != "pass":
            issue(issues, "release.hosted_check_failed", name)
    missing_checks = sorted(REQUIRED_HOSTED_CHECKS - seen_checks)
    if missing_checks:
        issue(issues, "release.hosted_checks_incomplete", ",".join(missing_checks))

    return {
        "contract_version": CONTRACT_VERSION,
        "source_revision": revision,
        "verdict": "release-ready" if not issues else "evidence-incomplete",
        "scope": {
            "operational_delivery": True,
            "static_rulebook_recovery": True,
            "general_semantic_accuracy": False,
            "human_usability_research": False,
        },
        "issues": issues,
        "limitations": [
            "This qualifies VEIL's declared operational delivery scope.",
            "It does not claim general semantic accuracy beyond separately recorded bounded evidence.",
            "Human UX research is optional post-release observation, not a release input.",
        ],
        "created_at": datetime.now(timezone.utc).isoformat(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--browser-record", type=Path, required=True)
    parser.add_argument("--integration-record", type=Path, required=True)
    parser.add_argument("--delivery-record", type=Path, required=True)
    parser.add_argument("--hosted-checks", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise SystemExit("release.output_already_exists")
    try:
        hosted = load_json(args.hosted_checks)
        if not isinstance(hosted, list):
            raise ValueError("hosted checks must be a JSON list")
        report = qualify(
            browser_record=load_json(args.browser_record),
            integration_record=load_json(args.integration_record),
            delivery_record=load_json(args.delivery_record),
            hosted_checks=hosted,
            revision=current_revision(),
        )
    except (OSError, UnicodeError, ValueError, json.JSONDecodeError, RuntimeError) as exc:
        report = {
            "contract_version": CONTRACT_VERSION,
            "source_revision": None,
            "verdict": "evidence-incomplete",
            "scope": {"operational_delivery": False},
            "issues": [{"code": "release.unreadable_input", "detail": str(exc)}],
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["verdict"] == "release-ready" else 1


if __name__ == "__main__":
    raise SystemExit(main())
