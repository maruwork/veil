#!/usr/bin/env python3
"""
veil-audit-db: helper DB の既存語彙を非破壊で監査する。

Usage:
  python veil-audit-db.py
  python veil-audit-db.py --db-path /path/to/vocab.db
  python veil-audit-db.py --status drop-candidate
  python veil-audit-db.py --json
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sqlite3
import sys
from pathlib import Path

import app
from veil_audit_core import VALID_STATUSES, audit_rows, filter_results, summarize_results


def load_normalize_helper():
    script_path = Path(__file__).with_name("veil-normalize.py")
    spec = importlib.util.spec_from_file_location("veil_normalize_helper", script_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("veil-normalize.py を読み込めません。")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


NORMALIZE_HELPER = load_normalize_helper()
CURRENT_SEED_SET = {row[0] for row in app.SEEDS}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="既存 vocab.db を非破壊で監査する。")
    parser.add_argument(
        "--db-path",
        default=app.DB_PATH,
        help="監査対象の vocab.db path。既定: repo 直下 vocab.db",
    )
    parser.add_argument(
        "--status",
        action="append",
        choices=VALID_STATUSES,
        help="指定した status だけを返す。複数回指定可。",
    )
    parser.add_argument("--json", action="store_true", help="JSON 形式で出力する。")
    return parser.parse_args()


def fetch_rows(db_path: str) -> list[dict[str, object]]:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute(
        "SELECT id, original, p1, p2, p3, cat, use_count FROM vocab ORDER BY use_count DESC, id ASC"
    )
    rows = [
        {
            "id": row[0],
            "original": row[1],
            "p1": row[2],
            "p2": row[3],
            "p3": row[4],
            "cat": row[5],
            "use_count": row[6],
        }
        for row in cur.fetchall()
    ]
    conn.close()
    return rows

def print_text_result(db_path: str, results: list[dict[str, object]], statuses: list[str] | None) -> None:
    print(f"監査対象: {db_path}")
    if statuses:
        print("status 絞り込み: " + ", ".join(statuses))
    if not results:
        print("語彙はありません。")
        return

    summary = summarize_results(results)
    print(
        "集計: "
        + ", ".join(f"{key}={summary[key]}" for key in ("keep", "review", "drop-candidate") if key in summary)
    )

    for item in results:
        reasons = " / ".join(item["reasons"])
        print(f"- [{item['status']}] {item['original']}")
        print(
            f"  cat={item['cat']} use_count={item['use_count']} "
            f"p1={'あり' if item['p1'] else 'なし'}"
        )
        print(f"  判別補助: {item['classification_hint']} ({item['classification_reason']})")
        print(f"  理由: {reasons}")
        print(f"  次アクション: {item['suggested_action']}")
        if item["review_focus"]:
            print("  見直し焦点: " + " / ".join(item["review_focus"]))


def main() -> int:
    args = parse_args()
    db_path = args.db_path
    if not os.path.exists(db_path):
        payload = {
            "status": "skip",
            "reason": "vocab.db が見つかりません。",
            "db_path": db_path,
        }
        if args.json:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            print(f"SKIP: {db_path} に vocab.db がありません")
        return 0

    rows = fetch_rows(db_path)
    results = filter_results(
        audit_rows(rows, CURRENT_SEED_SET, NORMALIZE_HELPER.classify_candidate_hint),
        args.status,
    )
    if args.json:
        payload = {
            "status": "ok",
            "db_path": db_path,
            "filters": {"statuses": args.status or []},
            "seed_count": len(CURRENT_SEED_SET),
            "row_count": len(results),
            "results": results,
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print_text_result(db_path, results, args.status)
    return 0


if __name__ == "__main__":
    sys.exit(main())
