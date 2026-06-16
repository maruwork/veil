#!/usr/bin/env python3
"""
veil-status: Show VEIL status and setup diagnostics.

Usage:
  python shared/runtime/veil-status.py
  python shared/runtime/veil-status.py --check
  python shared/runtime/veil-status.py --db ~/.veil/veil.db
  python shared/runtime/veil-status.py --json
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from shared.tools.veil_rule_store import readback_rules
from shared.tools.veil_locale import t

CONFIG_DIR = os.path.expanduser("~/.veil")
DEFAULT_DB_PATH = os.path.join(CONFIG_DIR, "veil.db")
DEFAULT_RULES_DIR = os.path.join(CONFIG_DIR, "rules")
TARGETS_FILE = os.path.join(CONFIG_DIR, "targets.json")
SKILL_CLAUDE = os.path.expanduser("~/.claude/commands/veil-capture.md")
SKILL_CODEX = os.path.expanduser("~/.agents/skills/veil-capture/SKILL.md")


VEIL_VERSION = "1.0.1"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=t("status.description"))
    parser.add_argument("--version", action="version", version=f"veil {VEIL_VERSION}")
    parser.add_argument("--check", action="store_true", help=t("status.check_help"))
    parser.add_argument("--db", default=DEFAULT_DB_PATH, help=t("status.db_help"))
    parser.add_argument("--json", dest="json_output", action="store_true", help=t("status.json_help"))
    return parser.parse_args()


def _display_path(path: str) -> str:
    home = os.path.expanduser("~").replace("\\", "/")
    normalized = path.replace("\\", "/")
    if normalized.startswith(home):
        return "~" + normalized[len(home):]
    return path


def _mirror_last_updated(rules_dir: str) -> str | None:
    if not os.path.isdir(rules_dir):
        return None
    try:
        mtimes = [os.path.getmtime(os.path.join(rules_dir, f)) for f in os.listdir(rules_dir) if f.endswith(".md")]
        if not mtimes:
            mtime = os.path.getmtime(rules_dir)
        else:
            mtime = max(mtimes)
        return datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M")
    except OSError:
        return None


def _load_targets() -> list[str] | None:
    if not os.path.exists(TARGETS_FILE):
        return None
    try:
        with open(TARGETS_FILE, encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list) and all(isinstance(item, str) for item in data):
            return data
    except (OSError, json.JSONDecodeError):
        pass
    return None


def collect_status(db_path: str) -> dict:
    db_exists = os.path.exists(db_path)
    rule_count: int | None = None
    if db_exists:
        result = readback_rules(db_path)
        rule_count = result["summary"]["total"]

    mirror_exists = os.path.isdir(DEFAULT_RULES_DIR)
    mirror_updated = _mirror_last_updated(DEFAULT_RULES_DIR) if mirror_exists else None

    targets = _load_targets()
    target_statuses: list[dict] = []
    if targets is not None:
        for path in targets:
            target_statuses.append({"path": path, "ok": os.path.exists(path)})

    return {
        "db_path": db_path,
        "db_exists": db_exists,
        "rule_count": rule_count,
        "rules_dir": DEFAULT_RULES_DIR,
        "mirror_exists": mirror_exists,
        "mirror_last_updated": mirror_updated,
        "targets_configured": targets is not None,
        "targets": target_statuses,
    }


def collect_setup(db_path: str) -> dict:
    items: list[dict] = []

    if os.path.exists(db_path):
        items.append({"label": _display_path(db_path), "level": "OK"})
    else:
        items.append({"label": _display_path(db_path), "level": "ERROR"})

    if os.path.isdir(DEFAULT_RULES_DIR):
        items.append({"label": _display_path(DEFAULT_RULES_DIR) + "/", "level": "OK"})
    else:
        items.append({"label": _display_path(DEFAULT_RULES_DIR) + "/", "level": "ERROR"})

    if os.path.exists(TARGETS_FILE):
        items.append({"label": _display_path(TARGETS_FILE), "level": "OK"})
    else:
        items.append({"label": _display_path(TARGETS_FILE), "level": "WARN"})

    targets = _load_targets()
    if targets is not None:
        for path in targets:
            if os.path.exists(path):
                items.append({"label": t("status.sync_target_ok", path=path), "level": "OK"})
            else:
                items.append({"label": t("status.sync_target_miss", path=path), "level": "WARN"})

    if os.path.exists(SKILL_CLAUDE):
        items.append({"label": f"skill: {_display_path(SKILL_CLAUDE)}", "level": "OK"})
    else:
        items.append({"label": f"skill not installed: {_display_path(SKILL_CLAUDE)}", "level": "WARN"})

    if os.path.exists(SKILL_CODEX):
        items.append({"label": f"skill: {_display_path(SKILL_CODEX)}", "level": "OK"})
    else:
        items.append({"label": f"skill not installed: {_display_path(SKILL_CODEX)}", "level": "WARN"})

    has_error = any(item["level"] == "ERROR" for item in items)
    return {"items": items, "has_error": has_error}


def print_status(payload: dict) -> None:
    if payload["db_exists"]:
        print(t("status.canonical_found", path=_display_path(payload["db_path"])))
        print(t("status.canonical_rule_count", count=payload["rule_count"]))
    else:
        print(t("status.canonical_not_found", path=_display_path(payload["db_path"])))

    if payload["mirror_exists"]:
        updated = payload["mirror_last_updated"] or "unknown"
        print(t("status.mirror_found", path=_display_path(payload["rules_dir"]), updated=updated))
    else:
        print(t("status.mirror_not_found", path=_display_path(payload["rules_dir"])))

    if not payload["targets_configured"]:
        print(t("status.targets_not_configured"))
    else:
        targets = payload["targets"]
        print(t("status.targets_registered", count=len(targets)))
        for target in targets:
            tag = "[OK]  " if target["ok"] else "[MISS]"
            print(f"  {tag} {target['path']}")


def print_setup(payload: dict) -> None:
    for item in payload["items"]:
        level = item["level"]
        label = item["label"]
        tag = f"[{level}]"
        print(f"{tag:<7} {label}")


def main() -> int:
    args = parse_args()

    if args.check:
        payload = collect_setup(args.db)
        if args.json_output:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            print_setup(payload)
        return 1 if payload["has_error"] else 0

    payload = collect_status(args.db)
    if args.json_output:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print_status(payload)
    return 0


if __name__ == "__main__":
    sys.exit(main())
