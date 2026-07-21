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
import hashlib
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from shared.tools.veil_capture_taxonomy import capture_taxonomy_payload
from shared.tools.veil_delivery_freshness import read_manifest, verify_manifest
from shared.tools.veil_html_assets import _HTML_TEMPLATE, _HTML_UI_BY_LANG
from shared.tools.veil_rule_store import DB_CLI_PATH, readback_rules
from shared.tools.veil_locale import t

CONFIG_DIR = os.path.expanduser("~/.veil")
DEFAULT_DB_PATH = os.path.join(CONFIG_DIR, "veil.db")
DEFAULT_HTML_PATH = os.path.join(CONFIG_DIR, "veil.html")
TARGETS_FILE = os.path.join(CONFIG_DIR, "targets.json")
SKILL_CLAUDE = os.path.expanduser("~/.claude/commands/veil-capture.md")
SKILL_CODEX = os.path.expanduser("~/.agents/skills/veil-capture/SKILL.md")
SKILL_CLAUDE_SOURCE = ROOT / "skills" / "claude-code" / "veil-capture.md"
SKILL_CODEX_SOURCE = ROOT / "skills" / "codex" / "veil-capture" / "SKILL.md"


VEIL_VERSION = "1.0.4"


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


def _last_updated(path: str) -> str | None:
    if not os.path.exists(path):
        return None
    try:
        mtime = os.path.getmtime(path)
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


def _skill_state(installed: str, source: Path) -> str:
    if not os.path.exists(installed):
        return "MISSING"
    try:
        if not source.is_file():
            return "ERROR"
        return "OK" if hashlib.sha256(Path(installed).read_bytes()).digest() == hashlib.sha256(source.read_bytes()).digest() else "STALE"
    except OSError:
        return "ERROR"


def _html_state(db_path: str) -> str:
    if not os.path.exists(DEFAULT_HTML_PATH):
        return "MISSING"
    try:
        content = Path(DEFAULT_HTML_PATH).read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return "ERROR"
    manifest, error = read_manifest(content)
    if error:
        return "STALE" if error == "missing" else "ERROR"
    assert manifest is not None
    result = readback_rules(db_path)
    if result["status"] != "ok":
        return "ERROR"
    lang_match = re.search(r'<html lang="([^"]+)"', content)
    default_lang = lang_match.group(1) if lang_match else "en"
    # The language is a rendering setting, not canonical data. Its stored value
    # is protected by content_sha256 while the other settings are recomputed.
    settings = {
        "db_cli_path": DB_CLI_PATH,
        "db_path": Path(db_path).as_posix(),
        "html_path": Path(DEFAULT_HTML_PATH).as_posix(),
        "default_lang": default_lang,
    }
    return verify_manifest(
        content,
        template=_HTML_TEMPLATE,
        ui_by_lang=_HTML_UI_BY_LANG,
        capture_taxonomy=capture_taxonomy_payload(),
        rows=result["rows"],
        settings=settings,
    )


def collect_status(db_path: str) -> dict:
    db_exists = os.path.exists(db_path)
    rule_count: int | None = None
    db_error: dict | None = None
    if db_exists:
        result = readback_rules(db_path)
        if result["status"] == "ok":
            rule_count = result["summary"]["total"]
        elif result["status"] == "error":
            db_error = {"reason": result["reason"], "error": result.get("error")}

    html_exists = os.path.exists(DEFAULT_HTML_PATH)
    html_updated = _last_updated(DEFAULT_HTML_PATH) if html_exists else None

    targets = _load_targets()
    target_statuses: list[dict] = []
    if targets is not None:
        for path in targets:
            target_statuses.append({"path": path, "ok": os.path.exists(path)})

    return {
        "db_path": db_path,
        "db_exists": db_exists,
        "rule_count": rule_count,
        "db_error": db_error,
        "html_path": DEFAULT_HTML_PATH,
        "html_exists": html_exists,
        "html_last_updated": html_updated,
        "targets_configured": targets is not None,
        "targets": target_statuses,
    }


def collect_setup(db_path: str) -> dict:
    items: list[dict] = []

    if os.path.exists(db_path):
        result = readback_rules(db_path)
        if result["status"] == "error":
            detail = f" ({result.get('error')})" if result.get("error") else ""
            items.append({"label": t("status.canonical_unreadable", path=_display_path(db_path), reason=t(str(result["reason"]))) + detail, "level": "ERROR"})
        else:
            items.append({"label": _display_path(db_path), "level": "OK"})
    else:
        items.append({"label": _display_path(db_path), "level": "ERROR"})

    html_state = _html_state(db_path)
    items.append({"label": _display_path(DEFAULT_HTML_PATH), "level": html_state})

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

    claude_state = _skill_state(SKILL_CLAUDE, SKILL_CLAUDE_SOURCE)
    codex_state = _skill_state(SKILL_CODEX, SKILL_CODEX_SOURCE)
    items.append({"label": f"skill: {_display_path(SKILL_CLAUDE)}", "level": claude_state})
    items.append({"label": f"skill: {_display_path(SKILL_CODEX)}", "level": codex_state})

    has_error = any(item["level"] in {"ERROR", "STALE", "MISSING"} for item in items)
    return {"items": items, "has_error": has_error}


def print_status(payload: dict) -> None:
    if payload["db_exists"] and not payload["db_error"]:
        print(t("status.canonical_found", path=_display_path(payload["db_path"])))
        print(t("status.canonical_rule_count", count=payload["rule_count"]))
    elif payload["db_exists"]:
        detail = payload["db_error"].get("error") if payload["db_error"] else None
        suffix = f" ({detail})" if detail else ""
        print(t("status.canonical_unreadable", path=_display_path(payload["db_path"]), reason=t(str(payload["db_error"]["reason"]))) + suffix)
    else:
        print(t("status.canonical_not_found", path=_display_path(payload["db_path"])))

    if payload["html_exists"]:
        updated = payload["html_last_updated"] or "unknown"
        print(t("status.html_found", path=_display_path(payload["html_path"]), updated=updated))
    else:
        print(t("status.html_not_found", path=_display_path(payload["html_path"])))

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
