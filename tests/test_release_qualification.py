from __future__ import annotations

from shared.tools.veil_release_qualification import qualify


REVISION = "a" * 40


def valid_records():
    browser = {
        "git_head": REVISION,
        "controlled_sources_dirty": False,
        "status": "ok",
        "functional_startup": "ok",
        "keyboard_startup": "ok",
        "result": {"ok": True},
        "keyboard_result": {"ok": True},
    }
    integration = {
        "git_head": REVISION,
        "controlled_sources_dirty": False,
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
        hosted_checks=[{"name": "windows", "bucket": "pass"}],
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
    }
