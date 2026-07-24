from __future__ import annotations

import json

from shared.tools.veil_human_ux_acceptance import evaluate_records, prepare_fixture


def _records(manifest_path, *, helped: bool = False, misconception: bool = False, confusion: list[str] | None = None):
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    import hashlib

    return {
        "contract_version": "1",
        "fixture_manifest_sha256": hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
        "source_revision": manifest["source_revision"],
        "participants": [
            {
                "participant_id": f"P{index:02d}",
                "target_user": True,
                "is_page_author": False,
                "tasks": {
                    task: {
                        "completed": True,
                        "moderator_navigation_help": helped and index == 1 and task == "find_preferred",
                    }
                    for task in ("find_preferred", "request_change", "review_conversation")
                },
                "beliefs": {
                    "no_match_proves_no_review_needed": misconception and index == 1,
                    "copy_saved_a_rule": False,
                    "knows_when_not_to_open_html": True,
                },
                "confusion_codes": confusion or [],
            }
            for index in range(1, 6)
        ],
    }


def test_prepare_fixture_is_disposable_and_binds_the_template(tmp_path) -> None:
    fixture_dir = tmp_path / "fixture"
    manifest = prepare_fixture(fixture_dir)

    assert (fixture_dir / "veil-human-ux.html").is_file()
    assert (fixture_dir / "fixture-manifest.json").is_file()
    assert manifest["fixture_rules"] == [{"term": "current state", "preferred": "present state"}]
    assert not (fixture_dir / "fixture.db").exists()


def test_five_independent_records_pass_only_the_human_ux_gate(tmp_path) -> None:
    fixture_dir = tmp_path / "fixture"
    prepare_fixture(fixture_dir)
    manifest_path = fixture_dir / "fixture-manifest.json"
    records_path = tmp_path / "records.json"
    records_path.write_text(json.dumps(_records(manifest_path)), encoding="utf-8")

    report = evaluate_records(manifest_path, records_path)

    assert report["status"] == "human-ux-passed"
    assert report["release_status"] == "not-ready"
    assert report["task_success_without_navigation_help"] == {
        "find_preferred": 5,
        "request_change": 5,
        "review_conversation": 5,
    }


def test_navigation_help_and_misconception_fail_closed(tmp_path) -> None:
    fixture_dir = tmp_path / "fixture"
    prepare_fixture(fixture_dir)
    manifest_path = fixture_dir / "fixture-manifest.json"
    records_path = tmp_path / "records.json"
    records_path.write_text(
        json.dumps(_records(manifest_path, helped=True, misconception=True)),
        encoding="utf-8",
    )

    report = evaluate_records(manifest_path, records_path)

    assert report["status"] == "requires-revision"
    assert {issue["code"] for issue in report["issues"]} >= {
        "human_ux.moderator_navigation_help",
        "human_ux.misconception",
    }


def test_any_observed_confusion_requires_a_fresh_source_run(tmp_path) -> None:
    fixture_dir = tmp_path / "fixture"
    prepare_fixture(fixture_dir)
    manifest_path = fixture_dir / "fixture-manifest.json"
    records_path = tmp_path / "records.json"
    records_path.write_text(
        json.dumps(_records(manifest_path, confusion=["copy_persistence"])),
        encoding="utf-8",
    )

    report = evaluate_records(manifest_path, records_path)

    assert report["status"] == "requires-revision"
    assert any(issue["code"] == "human_ux.unresolved_design_confusion" for issue in report["issues"])
