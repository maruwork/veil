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
import re
import sys
from pathlib import Path
from typing import Any

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

try:
    from shared.tools.veil_rule_store import RULE_LINE_RE, readback_rules
    from shared.tools.veil_locale import t
except ModuleNotFoundError:
    from veil_rule_store import RULE_LINE_RE, readback_rules  # type: ignore[no-redef]
    from veil_locale import t  # type: ignore[no-redef]

CONFIG_DIR = os.path.expanduser("~/.veil")
DEFAULT_RULES_DIR = os.path.join(CONFIG_DIR, "rules")

LEVEL_HEADING_RE = re.compile(r"^\s{0,3}#{1,6}\s*(?P<level>必須|推奨|観察)\s*$")
LEVEL_REQUIRED = "必須"
LEVEL_RECOMMENDED = "推奨"
LEVEL_OBSERVE = "観察"


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
    return {
        "total_rules": 0,
        "required_count": 0,
        "recommended_count": 0,
        "observe_count": 0,
        "legacy_flat_count": 0,
    }


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

    file_reports: list[dict[str, Any]] = []
    totals = _empty_counts()
    files_seen = 0

    for fname in sorted(os.listdir(rules_dir)):
        if not fname.endswith(".md"):
            continue
        path = os.path.join(rules_dir, fname)
        try:
            with open(path, encoding="utf-8") as f:
                lines = f.readlines()
        except OSError:
            continue

        counts = _empty_counts()
        seen_heading = False
        current_level = LEVEL_REQUIRED

        for line in lines:
            heading = LEVEL_HEADING_RE.match(line)
            if heading:
                seen_heading = True
                current_level = heading.group("level")
                continue
            if not RULE_LINE_RE.match(line):
                continue
            counts["total_rules"] += 1
            if not seen_heading:
                counts["legacy_flat_count"] += 1
                counts["required_count"] += 1
            elif current_level == LEVEL_REQUIRED:
                counts["required_count"] += 1
            elif current_level == LEVEL_RECOMMENDED:
                counts["recommended_count"] += 1
            elif current_level == LEVEL_OBSERVE:
                counts["observe_count"] += 1

        if counts["total_rules"] == 0:
            continue

        files_seen += 1
        for key in totals:
            totals[key] += counts[key]
        file_reports.append({"file": fname, **counts})

    return {
        "status": "ok",
        "source_type": "rules-dir",
        "rules_dir": rules_dir,
        "summary": {"files": files_seen, **totals},
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
            "summary": {"files": 0, "total_rules": 0},
            "files": [],
        }

    total = payload["summary"]["total"]
    return {
        "status": "ok",
        "source_type": "db",
        "db_path": db_path,
        "summary": {"files": 1 if total else 0, "total_rules": total},
        "files": [{"file": db_path, "total_rules": total}],
    }


def print_text_report(payload: dict[str, Any]) -> None:
    if payload["status"] == "skip":
        target = payload.get("db_path") or payload.get("rules_dir")
        print(t("audit.no_source", target=target))
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
    return 0


if __name__ == "__main__":
    sys.exit(main())
