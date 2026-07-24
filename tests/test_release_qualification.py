from __future__ import annotations

import json

from shared.tools.veil_release_qualification import load_json, qualify


REVISION = "a" * 40
HOSTED_CHECKS = [
    {"name": name, "bucket": "pass"}
    for name in (
        "Analyze (actions)",
        "Analyze (python)",
        "CodeQL",
        "design-methodology",
        "smoke (3.8)",
        "smoke (3.11)",
        "smoke (3.12)",
        "windows",
    )
]


def valid_records():
    browser = {
        "git_head": REVISION,
        "controlled_sources_dirty": False,
        "source_fingerprint_sha256": "f" * 64,
        "status": "ok",
        "functional_startup": "ok",
        "keyboard_startup": "ok",
        "result": {"ok": True},
        "keyboard_result": {"ok": True},
    }
    integration = {
        "git_head": REVISION,
        "controlled_sources_dirty": False,
        "source_fingerprint_sha256": "f" * 64,
        "status": "ok",
        "temp_only": True,
        "applied_atomic": True,
        "before_freshness": "OK",
        "stale_before_regeneration": "STALE",
        "final_freshness": "OK",
        "changed_visible": True,
        "retired_hidden": True,
    }
    delivery = {
        "commit_sha": REVISION,
        "source_fingerprint_sha256": "f" * 64,
        "status": "ok",
        "veil_status": {"items": [{"level": "OK"}, {"level": "OK"}]},
    }
    return browser, integration, delivery


def test_operational_release_qualification_passes_without_human_participants() -> None:
    browser, integration, delivery = valid_records()
    report = qualify(
        browser_record=browser,
        integration_record=integration,
        delivery_record=delivery,
        hosted_checks=HOSTED_CHECKS,
        revision=REVISION,
    )

    assert report["verdict"] == "release-ready"
    assert report["scope"]["human_usability_research"] is False
    assert report["scope"]["general_semantic_accuracy"] is False


def test_source_mismatch_or_failed_hosted_check_fails_closed() -> None:
    browser, integration, delivery = valid_records()
    browser["git_head"] = "b" * 40
    report = qualify(
        browser_record=browser,
        integration_record=integration,
        delivery_record=delivery,
        hosted_checks=[{"name": "windows", "bucket": "fail"}],
        revision=REVISION,
    )

    assert report["verdict"] == "evidence-incomplete"
    assert {issue["code"] for issue in report["issues"]} >= {
        "release.source_revision_mismatch",
        "release.hosted_check_failed",
        "release.hosted_checks_incomplete",
    }


def test_mixed_source_fingerprints_fail_closed() -> None:
    browser, integration, delivery = valid_records()
    integration["source_fingerprint_sha256"] = "e" * 64

    report = qualify(
        browser_record=browser,
        integration_record=integration,
        delivery_record=delivery,
        hosted_checks=HOSTED_CHECKS,
        revision=REVISION,
    )

    assert report["verdict"] == "evidence-incomplete"
    assert any(issue["code"] == "release.source_fingerprint_mismatch" for issue in report["issues"])


def test_load_json_accepts_windows_utf8_bom_delivery_evidence(tmp_path) -> None:
    path = tmp_path / "delivery.json"
    path.write_bytes(b"\xef\xbb\xbf" + json.dumps({"status": "ok"}).encode("utf-8"))

    assert load_json(path) == {"status": "ok"}
