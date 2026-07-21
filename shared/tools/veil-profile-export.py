#!/usr/bin/env python3
"""
veil-profile-export: Non-destructively export VEIL current profile.

Usage:
  python shared/tools/veil-profile-export.py --profile-name technical-writing-default
  python shared/tools/veil-profile-export.py --db ~/.veil/veil.db
  python shared/tools/veil-profile-export.py --seed-file shared/default-profile/technical-writing-default.json
  python shared/tools/veil-profile-export.py --base-manifest ~/.veil/profile-exports/technical-writing-default/manifest.json --profile-name medical-guardrail --domain medical
  python shared/tools/veil-profile-export.py --json
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

try:
    from shared.tools.veil_rule_store import (
        DEFAULT_DB_PATH,
        add_profile_level_count,
        empty_profile_level_counts,
        load_rules_from_seed_file,
        readback_rules,
    )
    from shared.tools.veil_locale import t
except ModuleNotFoundError:
    from veil_rule_store import (  # type: ignore[no-redef]
        DEFAULT_DB_PATH,
        add_profile_level_count,
        empty_profile_level_counts,
        load_rules_from_seed_file,
        readback_rules,
    )
    from veil_locale import t  # type: ignore[no-redef]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=t("export.description"))
    parser.add_argument("--db", default=DEFAULT_DB_PATH, help=t("export.db_help"))
    parser.add_argument("--seed-file", default=None, help=t("export.seed_file_help"))
    parser.add_argument("--base-manifest", default=None, help=t("export.base_manifest_help"))
    parser.add_argument("--profile-name", default="technical-writing-default", help=t("export.profile_name_help"))
    parser.add_argument("--domain", default="technical-writing", help=t("export.domain_help"))
    parser.add_argument(
        "--intended-use",
        default="AI-assisted technical writing terminology guardrail",
        help=t("export.intended_use_help"),
    )
    parser.add_argument("--base-profile", default="none", help=t("export.base_profile_help"))
    parser.add_argument("--output-dir", default=None, help=t("export.output_dir_help"))
    parser.add_argument("--json", action="store_true", help=t("export.json_help"))
    return parser.parse_args()


def default_output_dir(profile_name: str) -> str:
    return os.path.join(os.path.expanduser("~/.veil"), "profile-exports", profile_name)


def load_base_manifest(path: str) -> dict[str, Any]:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def summarize_rows(rows: list[dict[str, Any]]) -> dict[str, int]:
    summary = empty_profile_level_counts()
    for row in rows:
        if row.get("status") != "active":
            continue
        add_profile_level_count(summary, str(row.get("profile_level")), legacy_flat=bool(row.get("legacy_flat")))
    summary["files"] = 1 if summary["total_rules"] > 0 else 0
    return summary


def serialize_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    active_rows = [row for row in rows if row.get("status") == "active"]
    active_rows.sort(key=lambda row: (str(row["term_normalized"]), str(row["term_original"]).lower()))
    serialized: list[dict[str, Any]] = []
    for row in active_rows:
        serialized.append(
            {
                "term_original": row["term_original"],
                "preferred": row["preferred"],
                "preferred_alt_2": row.get("preferred_alt_2"),
                "preferred_alt_3": row.get("preferred_alt_3"),
                "status": row.get("status", "active"),
                "profile_level": row.get("profile_level"),
                "category_hint": row.get("category_hint"),
                "note": row.get("note"),
                "source_context": row.get("source_context"),
            }
        )
    return serialized


def load_source_rows(db_path: str, seed_file: str | None) -> tuple[str, str, list[dict[str, Any]], dict[str, Any] | None]:
    if seed_file:
        payload = load_rules_from_seed_file(seed_file)
        if payload["status"] != "ok":
            return "seed-file", seed_file, [], payload
        return "seed-file", seed_file, payload["selected_rules"], None

    payload = readback_rules(db_path)
    if payload["status"] != "ok":
        return "db", db_path, [], payload
    return "db", db_path, payload["rows"], None


def export_profile(
    source_type: str,
    source_label: str,
    rows: list[dict[str, Any]],
    output_dir: str,
    profile_name: str,
    domain: str,
    intended_use: str,
    base_profile: str,
) -> dict[str, Any]:
    os.makedirs(output_dir, exist_ok=True)
    serialized = serialize_rows(rows)
    summary = summarize_rows(rows)

    rules_payload = {
        "profile_name": profile_name,
        "domain": domain,
        "intended_use": intended_use,
        "base_profile": base_profile,
        "rules": serialized,
    }
    rules_path = os.path.join(output_dir, "rules.json")
    with open(rules_path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(rules_payload, f, ensure_ascii=False, indent=2)
        f.write("\n")

    manifest = {
        "profile_name": profile_name,
        "domain": domain,
        "intended_use": intended_use,
        "base_profile": base_profile,
        "source_type": source_type,
        "source": source_label,
        "rules_file": rules_path,
        "export_dir": output_dir,
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "summary": summary,
        "files": [{"file": "rules.json", **summary}] if summary["total_rules"] > 0 else [],
    }
    manifest_path = os.path.join(output_dir, "manifest.json")
    with open(manifest_path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
        f.write("\n")

    return {
        "status": "ok",
        "profile_name": profile_name,
        "domain": domain,
        "intended_use": intended_use,
        "base_profile": base_profile,
        "source_type": source_type,
        "source": source_label,
        "output_dir": output_dir,
        "rules_file": rules_path,
        "manifest_path": manifest_path,
        "summary": summary,
    }


def print_text(payload: dict[str, Any]) -> None:
    if payload["status"] != "ok":
        source = payload.get("source") or payload.get("db_path") or payload.get("seed_file")
        detail = f" ({payload['error']})" if payload.get("error") else ""
        print(f"ERROR: {t(str(payload['reason']))} ({source}){detail}")
        return
    summary = payload["summary"]
    print(
        "EXPORTED:"
        f" profile={payload['profile_name']},"
        f" domain={payload['domain']},"
        f" total={summary['total_rules']},"
        f" required={summary['required_count']},"
        f" recommended={summary['recommended_count']},"
        f" observe={summary['observe_count']},"
        f" output={payload['output_dir']}"
    )
    print(f"- manifest: {payload['manifest_path']}")
    print(f"- rules: {payload['rules_file']}")


def main() -> int:
    args = parse_args()
    seed_file = args.seed_file
    intended_use = args.intended_use
    base_profile = args.base_profile

    if args.base_manifest:
        if not os.path.exists(args.base_manifest):
            print(f"Error: manifest file not found: {args.base_manifest}", file=sys.stderr)
            return 1
        manifest = load_base_manifest(args.base_manifest)
        if seed_file is None:
            seed_file = os.path.join(os.path.dirname(os.path.abspath(args.base_manifest)), "rules.json")
        if base_profile == "none":
            base_profile = str(manifest.get("profile_name", "none"))
        if intended_use == "AI-assisted technical writing terminology guardrail":
            intended_use = str(manifest.get("intended_use", intended_use))

    source_type, source_label, rows, source_error = load_source_rows(args.db, seed_file)
    if source_error is not None:
        payload = {
            "status": source_error["status"],
            "reason": source_error["reason"],
            "source_type": source_type,
            "source": source_label,
            "db_path": args.db,
            "seed_file": seed_file,
            "error": source_error.get("error"),
        }
    else:
        output_dir = args.output_dir or default_output_dir(args.profile_name)
        payload = export_profile(
            source_type,
            source_label,
            rows,
            output_dir,
            args.profile_name,
            args.domain,
            intended_use,
            base_profile,
        )

    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print_text(payload)
    return 0 if payload["status"] == "ok" else 1


if __name__ == "__main__":
    sys.exit(main())
