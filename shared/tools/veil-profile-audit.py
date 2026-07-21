#!/usr/bin/env python3
"""
veil-profile-audit: Non-destructively audit VEIL profile data.

Usage:
  python shared/tools/veil-profile-audit.py
  python shared/tools/veil-profile-audit.py --db <path>
  python shared/tools/veil-profile-audit.py --seed-file <path>
  python shared/tools/veil-profile-audit.py --json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

try:
    from shared.tools.veil_rule_store import (
        DEFAULT_BUNDLED_PROFILE_SEED_PATH,
        DEFAULT_DB_PATH,
        add_profile_level_count,
        empty_profile_level_counts,
        load_rules_from_seed_file,
        readback_rules,
    )
    from shared.tools.veil_locale import t
except ModuleNotFoundError:
    from veil_rule_store import (  # type: ignore[no-redef]
        DEFAULT_BUNDLED_PROFILE_SEED_PATH,
        DEFAULT_DB_PATH,
        add_profile_level_count,
        empty_profile_level_counts,
        load_rules_from_seed_file,
        readback_rules,
    )
    from veil_locale import t  # type: ignore[no-redef]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=t("audit.description"))
    parser.add_argument("--db", default=DEFAULT_DB_PATH, help=t("audit.db_help"))
    parser.add_argument("--seed-file", help=t("audit.seed_file_help"))
    parser.add_argument("--json", action="store_true", help=t("audit.json_help"))
    return parser.parse_args()


def _empty_counts() -> dict[str, int]:
    return empty_profile_level_counts()


def _summarize_rows(rows: list[dict[str, Any]], source_type: str, source_label: str) -> dict[str, Any]:
    counts = _empty_counts()
    active_rows = [row for row in rows if row.get("status") == "active"]
    for row in active_rows:
        add_profile_level_count(counts, str(row.get("profile_level")), legacy_flat=bool(row.get("legacy_flat")))

    file_reports: list[dict[str, Any]] = []
    if counts["total_rules"] > 0:
        file_reports.append({"file": source_label, **counts})

    return {
        "status": "ok",
        "source_type": source_type,
        "summary": {"files": len(file_reports), **counts},
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

    result = _summarize_rows(payload["rows"], "db", db_path)
    result["db_path"] = db_path
    return result


def audit_seed_file(seed_file: str) -> dict[str, Any]:
    payload = load_rules_from_seed_file(seed_file)
    if payload["status"] != "ok":
        return {
            "status": payload["status"],
            "reason": payload["reason"],
            "source_type": "seed-file",
            "seed_file": seed_file,
            "summary": {"files": 0, **_empty_counts()},
            "files": [],
            "error": payload.get("error"),
        }

    result = _summarize_rows(payload["selected_rules"], "seed-file", seed_file)
    result["seed_file"] = seed_file
    return result


def print_text_report(payload: dict[str, Any]) -> None:
    if payload["status"] == "skip":
        target = payload.get("db_path") or payload.get("seed_file")
        print(t("audit.no_source", target=target))
        return
    if payload["status"] == "error":
        target = payload.get("db_path") or payload.get("seed_file")
        detail = f" ({payload['error']})" if payload.get("error") else ""
        print(f"ERROR: {t(str(payload['reason']))} ({target}){detail}")
        return

    summary = payload["summary"]
    source = payload.get("db_path") or payload.get("seed_file")
    print(
        "PROFILE:"
        f" source={payload.get('source_type')}, path={source},"
        f" files={summary['files']}, total={summary['total_rules']}"
    )
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
    seed_file = args.seed_file or None
    payload = audit_seed_file(seed_file) if seed_file else audit_db(args.db)
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print_text_report(payload)
    return 1 if payload["status"] == "error" else 0


if __name__ == "__main__":
    sys.exit(main())
