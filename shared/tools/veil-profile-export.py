#!/usr/bin/env python3
"""
veil-profile-export: Non-destructively export VEIL current profile.

Usage:
  python shared/tools/veil-profile-export.py --profile-name technical-writing-default
  python shared/tools/veil-profile-export.py --domain finance --base-profile technical-writing-default
  python shared/tools/veil-profile-export.py --base-manifest workspace/profile-exports/technical-writing-default/manifest.json --profile-name medical-guardrail --domain medical
  python shared/tools/veil-profile-export.py --rules-dir <path> --output-dir <path>
  python shared/tools/veil-profile-export.py --json
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

try:
    from shared.tools.veil_locale import t
except ModuleNotFoundError:
    from veil_locale import t  # type: ignore[no-redef]

CONFIG_DIR = os.path.expanduser("~/.veil")
DEFAULT_RULES_DIR = os.path.join(CONFIG_DIR, "rules")

# These constants match section headings in rules files (## 必須, ## 推奨, ## 観察).
# They are part of the file format specification and must not be localized.
LEVEL_REQUIRED = "必須"
LEVEL_RECOMMENDED = "推奨"
LEVEL_OBSERVE = "観察"
RULE_LINE_RE = re.compile(r"^\s*-\s*(?P<original>.+?)\s*(?:→|->)\s*(?P<preferred>.+?)\s*$")
LEVEL_HEADING_RE = re.compile(r"^\s{0,3}#{1,6}\s*(?P<level>必須|推奨|観察)\s*$")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=t("export.description"))
    parser.add_argument(
        "--rules-dir",
        default=DEFAULT_RULES_DIR,
        help=t("export.rules_dir_help"),
    )
    parser.add_argument(
        "--base-manifest",
        default=None,
        help=t("export.base_manifest_help"),
    )
    parser.add_argument(
        "--profile-name",
        default="technical-writing-default",
        help=t("export.profile_name_help"),
    )
    parser.add_argument(
        "--domain",
        default="technical-writing",
        help=t("export.domain_help"),
    )
    parser.add_argument(
        "--intended-use",
        default="AI-assisted technical writing terminology guardrail",
        help=t("export.intended_use_help"),
    )
    parser.add_argument(
        "--base-profile",
        default="none",
        help=t("export.base_profile_help"),
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        help=t("export.output_dir_help"),
    )
    parser.add_argument("--json", action="store_true", help=t("export.json_help"))
    return parser.parse_args()


def empty_counts() -> dict[str, int]:
    return {
        "required_count": 0,
        "recommended_count": 0,
        "observe_count": 0,
        "legacy_flat_count": 0,
        "total_rules": 0,
    }


def summarize_rules_dir(rules_dir: str) -> dict[str, object]:
    file_reports: list[dict[str, object]] = []
    summary = empty_counts() | {"files": 0, "legacy_files": 0}

    for fname in sorted(os.listdir(rules_dir)):
        if not fname.endswith(".md"):
            continue
        path = os.path.join(rules_dir, fname)
        try:
            with open(path, encoding="utf-8") as f:
                lines = f.readlines()
        except OSError:
            continue

        counts = empty_counts()
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
                continue
            if current_level == LEVEL_REQUIRED:
                counts["required_count"] += 1
            elif current_level == LEVEL_RECOMMENDED:
                counts["recommended_count"] += 1
            elif current_level == LEVEL_OBSERVE:
                counts["observe_count"] += 1

        if counts["total_rules"] == 0:
            continue

        summary["files"] += 1
        summary["required_count"] += counts["required_count"]
        summary["recommended_count"] += counts["recommended_count"]
        summary["observe_count"] += counts["observe_count"]
        summary["legacy_flat_count"] += counts["legacy_flat_count"]
        summary["total_rules"] += counts["total_rules"]
        if counts["legacy_flat_count"] > 0:
            summary["legacy_files"] += 1
        file_reports.append({"file": fname, **counts})

    return {"summary": summary, "files": file_reports}


def default_output_dir(profile_name: str) -> str:
    return os.path.join(os.getcwd(), "workspace", "profile-exports", profile_name)


def load_base_manifest(path: str) -> dict[str, object]:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def export_profile(
    rules_dir: str,
    output_dir: str,
    profile_name: str,
    domain: str,
    intended_use: str,
    base_profile: str,
) -> dict[str, object]:
    if not os.path.isdir(rules_dir):
        return {
            "status": "error",
            "reason": t("export.rules_dir_not_found"),
            "rules_dir": rules_dir,
            "output_dir": output_dir,
            "profile_name": profile_name,
            "domain": domain,
            "intended_use": intended_use,
            "base_profile": base_profile,
        }

    os.makedirs(output_dir, exist_ok=True)
    copied_files: list[str] = []
    for fname in sorted(os.listdir(rules_dir)):
        if not fname.endswith(".md"):
            continue
        src = os.path.join(rules_dir, fname)
        dst = os.path.join(output_dir, fname)
        with open(src, encoding="utf-8") as f:
            text = f.read()
        with open(dst, "w", encoding="utf-8", newline="\n") as f:
            f.write(text)
        copied_files.append(fname)

    summary_payload = summarize_rules_dir(rules_dir)
    manifest = {
        "profile_name": profile_name,
        "domain": domain,
        "intended_use": intended_use,
        "base_profile": base_profile,
        "source_rules_dir": rules_dir,
        "export_dir": output_dir,
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "summary": summary_payload["summary"],
        "files": summary_payload["files"],
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
        "rules_dir": rules_dir,
        "output_dir": output_dir,
        "copied_files": copied_files,
        "manifest_path": manifest_path,
        "summary": summary_payload["summary"],
    }


def print_text(payload: dict[str, object]) -> None:
    if payload["status"] != "ok":
        print(f"ERROR: {t(str(payload['reason']))} ({payload['rules_dir']})")
        return
    summary = payload["summary"]
    print(
        "EXPORTED:"
        f" profile={payload['profile_name']},"
        f" domain={payload['domain']},"
        f" files={summary['files']},"
        f" total={summary['total_rules']},"
        f" required={summary['required_count']},"
        f" recommended={summary['recommended_count']},"
        f" observe={summary['observe_count']},"
        f" output={payload['output_dir']}"
    )
    print(f"- manifest: {payload['manifest_path']}")


def main() -> int:
    args = parse_args()
    rules_dir = args.rules_dir
    intended_use = args.intended_use
    base_profile = args.base_profile
    if args.base_manifest:
        manifest = load_base_manifest(args.base_manifest)
        rules_dir = os.path.dirname(os.path.abspath(args.base_manifest))
        if base_profile == "none":
            base_profile = str(manifest.get("profile_name", "none"))
        if intended_use == "AI-assisted technical writing terminology guardrail":
            intended_use = str(manifest.get("intended_use", intended_use))
    output_dir = args.output_dir or default_output_dir(args.profile_name)
    payload = export_profile(
        rules_dir,
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
