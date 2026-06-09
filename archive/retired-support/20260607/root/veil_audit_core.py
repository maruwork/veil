#!/usr/bin/env python3
"""Shared helper for helper DB audit."""

from __future__ import annotations

from collections.abc import Callable

HINT_TO_CAT = {
    "識別子候補": 2,
    "固有名候補": 5,
    "説明語候補": 1,
    "境界が曖昧な候補": 7,
}
VALID_STATUSES = ("keep", "review", "drop-candidate")


def audit_status(
    row: dict[str, object],
    current_seed_set: set[str],
    classify_candidate_hint: Callable[[str], tuple[str, str]],
) -> tuple[str, list[str], str, str]:
    original = str(row["original"])
    p1 = str(row["p1"] or "")
    cat = int(row["cat"] or 0)
    use_count = int(row["use_count"] or 0)
    classification_hint, classification_reason = classify_candidate_hint(original)

    reasons: list[str] = []
    expected_cat = HINT_TO_CAT.get(classification_hint)
    cat_mismatch = expected_cat is not None and cat not in (expected_cat, 6)

    if original in current_seed_set:
        reasons.append("現行 seed 集合に含まれる")
        return "keep", reasons, classification_hint, classification_reason

    if use_count >= 3:
        reasons.append("use_count が高い")
        return "keep", reasons, classification_hint, classification_reason

    if use_count == 0 and not p1 and classification_hint in {"識別子候補", "境界が曖昧な候補"}:
        reasons.append("未使用")
        reasons.append("候補1なし")
        reasons.append(f"{classification_hint} と判定")
        return "drop-candidate", reasons, classification_hint, classification_reason

    if use_count == 0 and classification_hint == "識別子候補":
        reasons.append("未使用")
        reasons.append("識別子寄り")
        return "drop-candidate", reasons, classification_hint, classification_reason

    if not p1:
        reasons.append("候補1なし")
    if use_count <= 1:
        reasons.append("use_count が低い")
    if classification_hint == "境界が曖昧な候補":
        reasons.append("境界が曖昧")
    if cat_mismatch:
        reasons.append("cat と判別補助がずれる")
    if cat == 6:
        reasons.append("project 固有は手動で見直す")

    if not reasons:
        reasons.append("現行 seed には無いが即除外条件にも当たらない")
    return "review", reasons, classification_hint, classification_reason


def build_action_guidance(
    row: dict[str, object],
    status: str,
    classification_hint: str,
    cat_mismatch: bool,
) -> tuple[str, list[str]]:
    if status == "keep":
        return "そのまま維持", []

    if status == "drop-candidate":
        return "helper DB からの削除を検討する", [
            "UI で不要なら削除",
        ]

    focus: list[str] = []
    if not str(row["p1"] or ""):
        focus.append("候補1なし")
    if cat_mismatch:
        focus.append("cat と判別補助がずれる")
    if classification_hint == "境界が曖昧な候補":
        focus.append("境界が曖昧")
    if classification_hint == "識別子候補":
        focus.append("識別子寄り")
    if int(row["cat"] or 0) == 6:
        focus.append("project 固有語なので手動判断")
    original = str(row["original"])
    if (
        classification_hint not in {"固有名候補", "識別子候補"}
        and " " not in original
        and "-" not in original
        and "_" not in original
        and "=" not in original
    ):
        focus.append("単語単体で意味が広い")
    if not focus:
        focus.append("候補1・カテゴリ・用途を見直す")
    return "候補1・カテゴリ・用途を見直す", focus


def audit_rows(
    rows: list[dict[str, object]],
    current_seed_set: set[str],
    classify_candidate_hint: Callable[[str], tuple[str, str]],
) -> list[dict[str, object]]:
    results = []
    for row in rows:
        status, reasons, classification_hint, classification_reason = audit_status(
            row,
            current_seed_set,
            classify_candidate_hint,
        )
        expected_cat = HINT_TO_CAT.get(classification_hint)
        cat_mismatch = expected_cat is not None and int(row["cat"] or 0) not in (expected_cat, 6)
        suggested_action, review_focus = build_action_guidance(
            row,
            status,
            classification_hint,
            cat_mismatch,
        )
        results.append(
            {
                **row,
                "status": status,
                "reasons": reasons,
                "classification_hint": classification_hint,
                "classification_reason": classification_reason,
                "suggested_action": suggested_action,
                "review_focus": review_focus,
                "is_current_seed": row["original"] in current_seed_set,
            }
        )
    return results


def filter_results(results: list[dict[str, object]], statuses: list[str] | None) -> list[dict[str, object]]:
    if not statuses:
        return results
    allowed = set(statuses)
    return [item for item in results if item["status"] in allowed]


def summarize_results(results: list[dict[str, object]]) -> dict[str, int]:
    summary = {status: 0 for status in VALID_STATUSES}
    for item in results:
        summary[item["status"]] = summary.get(item["status"], 0) + 1
    return summary
