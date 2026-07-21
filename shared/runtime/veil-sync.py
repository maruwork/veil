#!/usr/bin/env python3
"""
veil-sync: Sync VEIL vocabulary rules to AI tool configuration files.

Usage:
  python shared/runtime/veil-sync.py                             # sync all targets
  python shared/runtime/veil-sync.py --add <path>                # register sync target
  python shared/runtime/veil-sync.py --list                      # list registered targets
  python shared/runtime/veil-sync.py --remove <path>             # unregister target
  python shared/runtime/veil-sync.py --db <path>

Supported files:
  CLAUDE.md, AGENTS.md, GEMINI.md, .cursorrules,
  .github/copilot-instructions.md, .aider.conf.yml
"""
from __future__ import annotations

import argparse
import sys
import os
import json
import re
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from shared.tools.veil_rule_store import (
    DEFAULT_DB_PATH,
    get_protected_repo_dir_name,
    readback_rules,
)
from shared.tools.veil_locale import t

CONFIG_DIR = os.path.expanduser("~/.veil")

MARKERS = {
    "yaml": ("# VEIL_START", "# VEIL_END"),
    "default": ("<!-- VEIL_START -->", "<!-- VEIL_END -->"),
}

YAML_EXTS = {".yml", ".yaml", ".toml", ".ini", ".cfg"}

AI_CONFIG_NAMES = [
    "CLAUDE.md",
    "AGENTS.md",
    "GEMINI.md",
    ".cursorrules",
    ".aider.conf.yml",
]


def find_sibling_ai_configs(registered_path: str) -> list[str]:
    dir_ = os.path.dirname(registered_path)
    # .github/copilot-instructions.md is registered → step up to project root
    if os.path.basename(dir_) == ".github":
        dir_ = os.path.dirname(dir_)
    found = []
    for name in AI_CONFIG_NAMES:
        candidate = os.path.abspath(os.path.join(dir_, name))
        if os.path.exists(candidate) and candidate != registered_path:
            found.append(candidate)
    copilot = os.path.abspath(os.path.join(dir_, ".github", "copilot-instructions.md"))
    if os.path.exists(copilot) and copilot != registered_path:
        found.append(copilot)
    return found


def build_paths(config_dir: str, db_path: str | None) -> dict[str, str]:
    return {
        "config_dir": config_dir,
        "targets_file": os.path.join(config_dir, "targets.json"),
        "config_file": os.path.join(config_dir, "config.json"),
        "behavior_file": os.path.join(config_dir, "behavior.md"),
        "db_path": db_path or DEFAULT_DB_PATH,
    }


def build_parser():
    parser = argparse.ArgumentParser(description=t("sync.description"))
    parser.add_argument("--config-dir", default=CONFIG_DIR, help=t("sync.config_dir_help"))
    parser.add_argument("--db", help=t("sync.db_help"))
    parser.add_argument("--quiet", action="store_true", help=t("sync.quiet_help"))
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--add", metavar="PATH", help=t("sync.add_help"))
    group.add_argument("--list", action="store_true", help=t("sync.list_help"))
    group.add_argument("--remove", metavar="PATH", help=t("sync.remove_help"))
    parser.add_argument("--purge", action="store_true", help=t("sync.purge_help"))
    return parser


def get_markers(path):
    ext = os.path.splitext(path)[1].lower()
    return MARKERS["yaml"] if ext in YAML_EXTS else MARKERS["default"]


def _commentize_structured_block(text: str) -> str:
    lines = text.splitlines()
    if not lines:
        return "#"
    commented: list[str] = []
    for line in lines:
        commented.append(f"# {line}" if line.strip() else "#")
    return "\n".join(commented)


def render_sync_block(path: str, combined: str) -> str:
    marker_start, marker_end = get_markers(path)
    ext = os.path.splitext(path)[1].lower()
    body = _commentize_structured_block(combined) if ext in YAML_EXTS else combined
    return f"{marker_start}\n{body}\n{marker_end}"


def load_targets(paths):
    if not os.path.exists(paths["targets_file"]):
        return []
    try:
        with open(paths["targets_file"], encoding="utf-8-sig") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError) as exc:
        print(t("sync.targets_read_error", exc=exc), file=sys.stderr)
        return []
    if not isinstance(data, list) or not all(isinstance(item, str) for item in data):
        print(t("sync.targets_format_error"), file=sys.stderr)
        return []
    return data


def save_targets(paths, targets):
    os.makedirs(paths["config_dir"], exist_ok=True)
    with open(paths["targets_file"], "w", encoding="utf-8") as f:
        json.dump(targets, f, ensure_ascii=False, indent=2)


def load_behavior(paths):
    if not os.path.exists(paths["behavior_file"]):
        return ""
    try:
        with open(paths["behavior_file"], encoding="utf-8") as f:
            return f.read().strip()
    except OSError:
        return ""


def prepare_base_rules(paths, quiet=False):
    payload = readback_rules(paths["db_path"])
    if payload["status"] == "skip":
        return payload["status"], "", None
    if payload["status"] != "ok":
        return payload["status"], "", payload

    active_rows = [
        row for row in payload["rows"]
        if row.get("status") == "active"
    ]
    if not active_rows:
        return "ok", "", None

    lines: list[str] = []
    for row in sorted(active_rows, key=lambda item: (str(item["term_normalized"]), str(item["term_original"]).lower())):
        preferred = str(row["preferred"]).strip()
        if not preferred:
            continue
        lines.append(f"- {row['term_original']} -> {preferred}")
    return "ok", "\n".join(lines), None


def do_sync(paths, base="", quiet=False, targets=None):
    if targets is None:
        targets = load_targets(paths)
    combined = ""
    if base:
        combined = t("sync.rules_section_header") + base
    behavior = load_behavior(paths)
    if behavior:
        sep = "\n\n" if combined else ""
        combined = combined + sep + behavior
    if not targets or not combined:
        return
    for path in targets:
        protected_root = get_protected_repo_dir_name(path)
        if protected_root is not None:
            if not quiet:
                print(t("sync.protected_target_skip", path=path, root=protected_root))
            continue
        if not os.path.exists(path):
            if not quiet:
                print(t("sync.skip", path=path))
            continue
        marker_start, marker_end = get_markers(path)
        block = render_sync_block(path, combined)
        try:
            with open(path, encoding="utf-8") as f:
                content = f.read()
        except OSError as e:
            if not quiet:
                print(t("sync.error", path=path, reason=e))
            continue
        pattern = re.escape(marker_start) + r".*?" + re.escape(marker_end)
        if re.search(pattern, content, flags=re.DOTALL):
            new_content = re.sub(pattern, block, content, flags=re.DOTALL)
        else:
            new_content = content.rstrip("\n") + "\n\n" + block + "\n"
        if new_content == content:
            if not quiet:
                print(t("sync.no_change", path=path))
            continue
        try:
            dir_ = os.path.dirname(path) or '.'
            with tempfile.NamedTemporaryFile('w', encoding='utf-8', dir=dir_, delete=False, suffix='.tmp') as tmp:
                tmp.write(new_content)
                tmp_path = tmp.name
            shutil.move(tmp_path, path)
        except OSError as e:
            if not quiet:
                print(t("sync.write_error", path=path, reason=e))
            continue
        if not quiet:
            print(t("sync.updated", path=path))


def cmd_sync(paths, quiet=False):
    targets = load_targets(paths)
    if not targets:
        if not quiet:
            print(t("sync.no_targets"))
        return 0
    _, base, source_error = prepare_base_rules(paths, quiet=quiet)
    if source_error is not None:
        if not quiet:
            detail = f" ({source_error['error']})" if source_error.get("error") else ""
            print(t("sync.source_error", reason=t(str(source_error.get("reason")))) + detail)
        return 1
    behavior = load_behavior(paths)
    if not base and not behavior:
        if not quiet:
            print(t("sync.no_rules"))
        return 0
    if not quiet:
        print(t("sync.sync_start", count=len(targets)))
    do_sync(paths, base, quiet=quiet, targets=targets)
    if not quiet:
        print(t("sync.sync_done"))
    return 0


def save_config(paths):
    os.makedirs(paths["config_dir"], exist_ok=True)
    cfg = {}
    if os.path.exists(paths["config_file"]):
        try:
            with open(paths["config_file"], encoding="utf-8") as f:
                cfg = json.load(f)
        except Exception:
            pass
    cfg["sync_script"] = os.path.abspath(__file__)
    cfg["veil_root"] = str(Path(__file__).resolve().parents[2])
    with open(paths["config_file"], "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)


def cmd_add(paths, path, quiet=False):
    path = os.path.abspath(path)
    protected_root = get_protected_repo_dir_name(path)
    if protected_root is not None:
        print(t("sync.protected_target_path", path=path, root=protected_root))
        return 1
    if not os.path.exists(path):
        print(t("sync.file_not_found", path=path))
        return 1
    targets = load_targets(paths)
    changed = False
    notices: list[tuple[str, str]] = []
    if path in targets:
        notices.append(("already_registered", path))
    else:
        targets.append(path)
        changed = True
        notices.append(("registered", path))

    for sibling in find_sibling_ai_configs(path):
        if sibling not in targets:
            targets.append(sibling)
            changed = True
            notices.append(("auto_registered", sibling))

    _, base, source_error = prepare_base_rules(paths, quiet=quiet)
    if source_error is not None:
        detail = f" ({source_error['error']})" if source_error.get("error") else ""
        print(t("sync.source_error", reason=t(str(source_error.get("reason")))) + detail)
        return 1

    for key, notice_path in notices:
        print(t(f"sync.{key}", path=notice_path))

    if changed:
        save_targets(paths, targets)
        save_config(paths)

    do_sync(paths, base, quiet=quiet)
    return 0


def cmd_list(paths):
    targets = load_targets(paths)
    if not targets:
        print(t("sync.no_targets_list"))
        return 0
    print(t("sync.targets_header"))
    for target in targets:
        status = "[OK]" if os.path.exists(target) else t("sync.target_miss")
        print(f"  {status} {target}")
    return 0


def _remove_veil_block(path: str) -> bool:
    marker_start, marker_end = get_markers(path)
    try:
        with open(path, encoding="utf-8") as f:
            content = f.read()
        pattern = r"\n*" + re.escape(marker_start) + r".*?" + re.escape(marker_end) + r"\n?"
        new_content = re.sub(pattern, "", content, flags=re.DOTALL)
        if new_content == content:
            return False
        new_content = new_content.rstrip("\n") + "\n"
        fd, tmp = tempfile.mkstemp(dir=os.path.dirname(path) or ".")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as fh:
                fh.write(new_content)
            shutil.move(tmp, path)
        except Exception:
            os.unlink(tmp)
            raise
        return True
    except OSError:
        return False


def cmd_remove(paths, path, purge: bool = False):
    path = os.path.abspath(path)
    targets = load_targets(paths)
    if path not in targets:
        print(t("sync.not_registered", path=path))
        return 1
    targets.remove(path)
    save_targets(paths, targets)
    if purge and os.path.exists(path):
        removed = _remove_veil_block(path)
        if removed:
            print(t("sync.block_removed", path=path))
    print(t("sync.unregistered", path=path))
    return 0


if __name__ == "__main__":
    parser = build_parser()
    args = parser.parse_args()
    paths = build_paths(args.config_dir, args.db)
    if args.add:
        sys.exit(cmd_add(paths, args.add, quiet=args.quiet))
    elif args.list:
        sys.exit(cmd_list(paths))
    elif args.remove:
        sys.exit(cmd_remove(paths, args.remove, purge=args.purge))
    else:
        sys.exit(cmd_sync(paths, quiet=args.quiet))
