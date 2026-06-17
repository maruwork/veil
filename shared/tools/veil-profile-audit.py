#!/usr/bin/env python3
"""
veil-profile-audit: Non-destructively audit VEIL rules directory rule count.

Usage:
  python shared/tools/veil-profile-audit.py
  python shared/tools/veil-profile-audit.py --rules-dir <path>
  python shared/tools/veil-profile-audit.py --db <path>
  python shared/tools/veil-profile-audit.py --json
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

try:
    from shared.tools.veil_rule_store import (
        add_profile_level_count,
        empty_profile_level_counts,
        load_rules_from_markdown_dir,
        readback_rules,
    )
    from shared.tools.veil_locale import t
except ModuleNotFoundError:
    from veil_rule_store import (  # type: ignore[no-redef]
        add_profile_level_count,
        empty_profile_level_counts,
        load_rules_from_markdown_dir,
        readback_rules,
    )
    from veil_locale import t  # type: ignore[no-redef]

CONFIG_DIR = os.path.expanduser("~/.veil")
DEFAULT_RULES_DIR = os.path.join(CONFIG_DIR, "rules")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=t("audit.description"))
    parser.add_argument(
        "--rules-dir",
        default=DEFAULT_RULES_DIR,
        help=t("audit.rules_dir_help"),
    )
    parser.add_argument(
        "--db",
        help=t("audit.db_help"),
    )
    parser.add_argument("--json", action="store_true", help=t("audit.json_help"))
    return parser.parse_args()


def _empty_counts() -> dict[str, int]:
    return empty_profile_level_counts()


def audit_rules_dir(rules_dir: str) -> dict[str, Any]:
    if not os.path.isdir(rules_dir):
        return {
            "status": "skip",
            "reason": "audit.rules_dir_not_found",
            "rules_dir": rules_dir,
            "summary": {
                "files": 0,
                "total_rules": 0,
                "required_count": 0,
                "recommended_count": 0,
                "observe_count": 0,
                "legacy_flat_count": 0,
            },
            "files": [],
        }

    parsed = load_rules_from_markdown_dir(rules_dir)
    if parsed["status"] != "ok":
        return {
            "status": parsed["status"],
            "reason": parsed["reason"],
            "source_type": "rules-dir",
            "rules_dir": rules_dir,
            "summary": {"files": 0, **_empty_counts()},
            "files": [],
        }

    file_reports: list[dict[str, Any]] = []
    totals = _empty_counts()
    files_by_name: dict[str, dict[str, Any]] = {}
    for row in parsed["rules"]:
        fname = str(row["source_file"])
        counts = files_by_name.setdefault(fname, {"file": fname, **_empty_counts()})
        add_profile_level_count(
            counts,
            str(row.get("profile_level")),
            legacy_flat=bool(row.get("legacy_flat")),
        )
        add_profile_level_count(
            totals,
            str(row.get("profile_level")),
            legacy_flat=bool(row.get("legacy_flat")),
        )

    for fname in sorted(files_by_name):
        file_reports.append(files_by_name[fname])

    return {
        "status": "ok",
        "source_type": "rules-dir",
        "rules_dir": rules_dir,
        "summary": {"files": len(file_reports), **totals},
        "files": file_reports,
    }


def audit_db(db_path: str) -> dict[str, Any]:
    payload = readback_rules(db_path)
    if payload["status"] != "ok":
        return {
            "status": payload["status"],
            "reason": payload["reason"],
            "source_type": "db",
            "db_path": db_path,
            "summary": {"files": 0, **_empty_counts()},
            "files": [],
            "error": payload.get("error"),
        }

    counts = _empty_counts()
    for row in payload["rows"]:
        if row.get("status") != "active":
            continue
        add_profile_level_count(counts, str(row.get("profile_level")))

    file_reports: list[dict[str, Any]] = []
    if counts["total_rules"] > 0:
        file_reports.append({"file": db_path, **counts})

    return {
        "status": "ok",
        "source_type": "db",
        "db_path": db_path,
        "summary": {"files": len(file_reports), **counts},
        "files": file_reports,
    }


def print_text_report(payload: dict[str, Any]) -> None:
    if payload["status"] == "skip":
        target = payload.get("db_path") or payload.get("rules_dir")
        print(t("audit.no_source", target=target))
        return
    if payload["status"] == "error":
        target = payload.get("db_path") or payload.get("rules_dir")
        detail = f" ({payload['error']})" if payload.get("error") else ""
        print(f"ERROR: {t(str(payload['reason']))} ({target}){detail}")
        return

    summary = payload["summary"]
    source = payload.get("db_path") or payload.get("rules_dir")
    print(
        "PROFILE:"
        f" source={payload.get('source_type')}, path={source},"
        f" files={summary['files']}, total={summary['total_rules']}"
    )
    if payload.get("source_type") == "rules-dir":
        print(
            f"  required={summary.get('required_count', 0)},"
            f" recommended={summary.get('recommended_count', 0)},"
            f" observe={summary.get('observe_count', 0)},"
            f" legacy_flat={summary.get('legacy_flat_count', 0)}"
        )
    for item in payload["files"]:
        print(f"- {item['file']}: total={item['total_rules']}")


def main() -> int:
    args = parse_args()
    payload = audit_db(args.db) if args.db else audit_rules_dir(args.rules_dir)
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print_text_report(payload)
    return 1 if payload["status"] == "error" else 0


if __name__ == "__main__":
    sys.exit(main())
