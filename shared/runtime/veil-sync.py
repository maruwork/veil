#!/usr/bin/env python3
"""
veil-sync: VEIL語彙を各AIツールの設定ファイルに同期する

使い方:
  python shared/runtime/veil-sync.py                             # 全ターゲットを同期
  python shared/runtime/veil-sync.py --add <path>                # 同期先ファイルを登録
  python shared/runtime/veil-sync.py --list                      # 登録済み一覧
  python shared/runtime/veil-sync.py --remove <path>             # 登録を解除
  python shared/runtime/veil-sync.py --db <path> --rules-dir <path>

対応ファイル例:
  CLAUDE.md, AGENTS.md, GEMINI.md, .cursorrules,
  .github/copilot-instructions.md, .aider.conf.yml
"""

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

from shared.tools.veil_rule_store import DEFAULT_DB_PATH, DEFAULT_RULES_DIR, export_markdown_mirror_from_db

CONFIG_DIR = os.path.expanduser("~/.veil")

# ファイル種別ごとのマーカー
MARKERS = {
    "yaml": ("# VEIL_START", "# VEIL_END"),
    "default": ("<!-- VEIL_START -->", "<!-- VEIL_END -->"),
}

YAML_EXTS = {".yml", ".yaml", ".toml", ".ini", ".cfg"}


def build_paths(config_dir: str, db_path: str | None, rules_dir: str | None) -> dict[str, str]:
    return {
        "config_dir": config_dir,
        "targets_file": os.path.join(config_dir, "targets.json"),
        "config_file": os.path.join(config_dir, "config.json"),
        "behavior_file": os.path.join(config_dir, "behavior.md"),
        "db_path": db_path or DEFAULT_DB_PATH,
        "rules_dir": rules_dir or DEFAULT_RULES_DIR,
    }


def build_parser():
    parser = argparse.ArgumentParser(description="VEIL語彙を各AIツールの設定ファイルに同期する。")
    parser.add_argument("--config-dir", default=CONFIG_DIR, help="VEIL config directory。既定: ~/.veil")
    parser.add_argument("--db", help="SQLite canonical DB path。既定: ~/.veil/veil.db")
    parser.add_argument("--rules-dir", help="markdown ミラーディレクトリ。既定: ~/.veil/rules")
    parser.add_argument("--quiet", action="store_true", help="sync 時の通常出力を抑制する。")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--add", metavar="PATH", help="同期先ファイルを登録する。")
    group.add_argument("--list", action="store_true", help="登録済み一覧を表示する。")
    group.add_argument("--remove", metavar="PATH", help="同期先ファイルの登録を解除する。")
    return parser


def get_markers(path):
    ext = os.path.splitext(path)[1].lower()
    return MARKERS["yaml"] if ext in YAML_EXTS else MARKERS["default"]


def load_targets(paths):
    if not os.path.exists(paths["targets_file"]):
        return []
    try:
        with open(paths["targets_file"], encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"警告: targets.json を読めませんでした: {exc}", file=sys.stderr)
        return []
    if not isinstance(data, list) or not all(isinstance(item, str) for item in data):
        print("警告: targets.json の形式が不正です。文字列パス配列を期待します。", file=sys.stderr)
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


def load_base_rules(rules_dir):
    if not os.path.isdir(rules_dir):
        return ""
    parts = []
    for fname in sorted(os.listdir(rules_dir)):
        if not fname.endswith(".md"):
            continue
        try:
            with open(os.path.join(rules_dir, fname), encoding="utf-8") as f:
                content = f.read().strip()
            if content:
                parts.append(content)
        except OSError:
            pass
    return "\n".join(parts)


def refresh_markdown_mirror(paths, quiet=False):
    if os.path.exists(paths["db_path"]):
        payload = export_markdown_mirror_from_db(paths["db_path"], paths["rules_dir"])
        if payload["status"] != "ok":
            if not quiet:
                reason = payload.get("reason") or "ミラー export に失敗しました。"
                print(f"  エラー: markdown ミラーを更新できません: {reason}")
            return payload
        if not quiet:
            print(
                f"  ミラー更新: {paths['rules_dir']} "
                f"(written={len(payload['written_files'])}, removed={len(payload['removed_files'])})"
            )
        return payload
    return {
        "status": "skip",
        "reason": "db file が見つからないため rules-dir fallback を使う",
        "db_path": paths["db_path"],
        "rules_dir": paths["rules_dir"],
    }


def prepare_base_rules(paths, quiet=False):
    payload = refresh_markdown_mirror(paths, quiet=quiet)
    if payload["status"] not in {"ok", "skip"}:
        return ""
    return load_base_rules(paths["rules_dir"])


def do_sync(paths, base="", quiet=False):
    targets = load_targets(paths)
    combined = ""
    if base:
        sep = "\n\n" if combined else ""
        combined = combined + sep + "表記統一ルール：\n" + base
    behavior = load_behavior(paths)
    if behavior:
        sep = "\n\n" if combined else ""
        combined = combined + sep + behavior
    if not targets or not combined:
        return
    for path in targets:
        if not os.path.exists(path):
            if not quiet:
                print(f"  スキップ: {path} (ファイルが見つかりません)")
            continue
        marker_start, marker_end = get_markers(path)
        block = f"{marker_start}\n{combined}\n{marker_end}"
        try:
            with open(path, encoding="utf-8") as f:
                content = f.read()
        except OSError as e:
            if not quiet:
                print(f"  エラー: {path} ({e})")
            continue
        pattern = re.escape(marker_start) + r".*?" + re.escape(marker_end)
        if re.search(pattern, content, flags=re.DOTALL):
            new_content = re.sub(pattern, block, content, flags=re.DOTALL)
        else:
            new_content = content.rstrip("\n") + "\n\n" + block + "\n"
        if new_content == content:
            if not quiet:
                print(f"  変更なし: {path}")
            continue
        try:
            dir_ = os.path.dirname(path) or '.'
            with tempfile.NamedTemporaryFile('w', encoding='utf-8', dir=dir_, delete=False, suffix='.tmp') as tmp:
                tmp.write(new_content)
                tmp_path = tmp.name
            shutil.move(tmp_path, path)
        except OSError as e:
            if not quiet:
                print(f"  書き込みエラー: {path} ({e})")
            continue
        if not quiet:
            print(f"  更新: {path}")


def cmd_sync(paths, quiet=False):
    targets = load_targets(paths)
    if not targets:
        print("同期先が未登録です。先に登録してください:\n  python shared/runtime/veil-sync.py --add <path>")
        return
    base = prepare_base_rules(paths, quiet=quiet)
    behavior = load_behavior(paths)
    if not base and not behavior:
        print("同期するルールがありません。SQLite canonical または markdown ミラーを確認してください。")
        return
    print(f"\n{len(targets)}件を同期:\n")
    do_sync(paths, base, quiet=quiet)
    print("\n完了")


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
    cfg["canonical_db"] = paths["db_path"]
    cfg["rules_mirror_dir"] = paths["rules_dir"]
    with open(paths["config_file"], "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)


def cmd_add(paths, path, quiet=False):
    path = os.path.abspath(path)
    if not os.path.exists(path):
        print(f"エラー: ファイルが存在しません: {path}")
        return
    targets = load_targets(paths)
    if path in targets:
        print(f"既に登録済み: {path}")
        return
    targets.append(path)
    save_targets(paths, targets)
    save_config(paths)
    print(f"登録: {path}")

    # 登録と同時に即時同期
    base = prepare_base_rules(paths, quiet=quiet)
    do_sync(paths, base, quiet=quiet)


def cmd_list(paths):
    targets = load_targets(paths)
    if not targets:
        print("登録された同期先はありません。")
        return
    print("登録済み同期先:")
    for t in targets:
        status = "✓" if os.path.exists(t) else "✗ (見つからない)"
        print(f"  [{status}] {t}")


def cmd_remove(paths, path):
    path = os.path.abspath(path)
    targets = load_targets(paths)
    if path not in targets:
        print(f"未登録: {path}")
        return
    targets.remove(path)
    save_targets(paths, targets)
    print(f"解除: {path}")


if __name__ == "__main__":
    parser = build_parser()
    args = parser.parse_args()
    paths = build_paths(args.config_dir, args.db, args.rules_dir)
    if args.add:
        cmd_add(paths, args.add, quiet=args.quiet)
    elif args.list:
        cmd_list(paths)
    elif args.remove:
        cmd_remove(paths, args.remove)
    else:
        cmd_sync(paths, quiet=args.quiet)
