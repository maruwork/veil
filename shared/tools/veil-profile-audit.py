#!/usr/bin/env python3
"""
veil-profile-audit: VEIL rules directory の rule 数を棚卸しする。

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

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

try:
    from shared.tools.veil_rule_store import RULE_LINE_RE, readback_rules
except ModuleNotFoundError:
    from veil_rule_store import RULE_LINE_RE, readback_rules

CONFIG_DIR = os.path.expanduser("~/.veil")
DEFAULT_RULES_DIR = os.path.join(CONFIG_DIR, "rules")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="VEIL rules profile を non-destructive に棚卸しする。")
    parser.add_argument(
        "--rules-dir",
        default=DEFAULT_RULES_DIR,
        help="棚卸し対象の rules directory。既定: ~/.veil/rules",
    )
    parser.add_argument(
        "--db",
        help="SQLite source を使う時の DB path。指定時は rules-dir よりこちらを優先する。",
    )
    parser.add_argument("--json", action="store_true", help="JSON 形式で出力する。")
    return parser.parse_args()


def audit_rules_dir(rules_dir: str) -> dict[str, object]:
    if not os.path.isdir(rules_dir):
        return {
            "status": "skip",
            "reason": "rules directory が見つかりません。",
            "rules_dir": rules_dir,
            "summary": {"files": 0, "total_rules": 0},
            "files": [],
        }

    file_reports: list[dict[str, object]] = []
    total_rules = 0
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

        count = sum(1 for line in lines if RULE_LINE_RE.match(line))
        if count == 0:
            continue

        files_seen += 1
        total_rules += count
        file_reports.append({"file": fname, "total_rules": count})

    return {
        "status": "ok",
        "source_type": "rules-dir",
        "rules_dir": rules_dir,
        "summary": {"files": files_seen, "total_rules": total_rules},
        "files": file_reports,
    }


def audit_db(db_path: str) -> dict[str, object]:
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


def print_text_report(payload: dict[str, object]) -> None:
    if payload["status"] == "skip":
        target = payload.get("db_path") or payload.get("rules_dir")
        print(f"SKIP: {target} に利用可能な source がありません")
        return

    summary = payload["summary"]
    source = payload.get("db_path") or payload.get("rules_dir")
    print(
        "PROFILE:"
        f" source={payload.get('source_type')}, path={source},"
        f" files={summary['files']}, total={summary['total_rules']}"
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
