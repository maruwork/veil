#!/usr/bin/env python3
"""
veil-sync: VEIL語彙を各AIツールの設定ファイルに同期する

使い方:
  python veil-sync.py                  # 全ターゲットを同期
  python veil-sync.py --add <path>     # 同期先ファイルを登録
  python veil-sync.py --list           # 登録済み一覧
  python veil-sync.py --remove <path>  # 登録を解除

対応ファイル例:
  CLAUDE.md, AGENTS.md, GEMINI.md, .cursorrules,
  .github/copilot-instructions.md, .aider.conf.yml
"""

import sys
import os
import json
import re
import shutil
import tempfile
import urllib.request

VEIL_URL = "http://127.0.0.1:8080/vocab/prompt"
CONFIG_DIR = os.path.expanduser("~/.veil")
TARGETS_FILE = os.path.join(CONFIG_DIR, "targets.json")
BASE_RULES_DIR = os.path.join(CONFIG_DIR, "rules")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")

# ファイル種別ごとのマーカー
MARKERS = {
    "yaml": ("# VEIL_START", "# VEIL_END"),
    "default": ("<!-- VEIL_START -->", "<!-- VEIL_END -->"),
}

YAML_EXTS = {".yml", ".yaml", ".toml", ".ini", ".cfg"}


def get_markers(path):
    ext = os.path.splitext(path)[1].lower()
    return MARKERS["yaml"] if ext in YAML_EXTS else MARKERS["default"]


def load_targets():
    if not os.path.exists(TARGETS_FILE):
        return []
    with open(TARGETS_FILE, encoding="utf-8") as f:
        return json.load(f)


def save_targets(targets):
    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(TARGETS_FILE, "w", encoding="utf-8") as f:
        json.dump(targets, f, ensure_ascii=False, indent=2)


def fetch_vocab():
    try:
        with urllib.request.urlopen(VEIL_URL, timeout=3) as resp:
            return resp.read().decode("utf-8").strip()
    except Exception:
        return None




def load_base_rules():
    if not os.path.isdir(BASE_RULES_DIR):
        return ""
    parts = []
    for fname in sorted(os.listdir(BASE_RULES_DIR)):
        if not fname.endswith(".md"):
            continue
        try:
            with open(os.path.join(BASE_RULES_DIR, fname), encoding="utf-8") as f:
                content = f.read().strip()
            if content:
                parts.append(content)
        except OSError:
            pass
    return "\n".join(parts)


def do_sync(vocab_text, base="", quiet=False):
    targets = load_targets()
    combined = vocab_text or ""
    if base:
        sep = "\n\n" if combined else ""
        combined = combined + sep + "表記統一ルール：\n" + base
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


def cmd_sync():
    targets = load_targets()
    if not targets:
        print("同期先が未登録です。先に登録してください:\n  python veil-sync.py --add <path>")
        return
    vocab = fetch_vocab()
    if vocab is None:
        print("警告: VEILサーバーに接続できません。base rules のみで同期します。\n      (app.py が起動中なら語彙DBも反映されます)")
        vocab = ""
    base = load_base_rules()
    if not vocab and not base:
        print("同期するルールがありません。app.py を起動するか ~/.veil/rules/ にルールを追加してください。")
        return
    print(f"\n{len(targets)}件を同期:\n")
    do_sync(vocab, base)
    print("\n完了")


def save_config():
    os.makedirs(CONFIG_DIR, exist_ok=True)
    cfg = {}
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, encoding="utf-8") as f:
                cfg = json.load(f)
        except Exception:
            pass
    cfg["sync_script"] = os.path.abspath(__file__)
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)


def cmd_add(path):
    path = os.path.abspath(path)
    targets = load_targets()
    if path in targets:
        print(f"既に登録済み: {path}")
        return
    targets.append(path)
    save_targets(targets)
    save_config()
    print(f"登録: {path}")

    # 登録と同時に即時同期
    vocab = fetch_vocab()
    if vocab is None:
        print("警告: VEILサーバーに接続できません。base rules のみで同期します。")
        vocab = ""
    base = load_base_rules()
    do_sync(vocab, base)


def cmd_list():
    targets = load_targets()
    if not targets:
        print("登録された同期先はありません。")
        return
    print("登録済み同期先:")
    for t in targets:
        status = "✓" if os.path.exists(t) else "✗ (見つからない)"
        print(f"  [{status}] {t}")


def cmd_remove(path):
    path = os.path.abspath(path)
    targets = load_targets()
    if path not in targets:
        print(f"未登録: {path}")
        return
    targets.remove(path)
    save_targets(targets)
    print(f"解除: {path}")


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        cmd_sync()
    elif args[0] == "--stdin":
        # app.py からの自動呼び出し用: vocab テキストを stdin から受け取って同期
        vocab = sys.stdin.read().strip()
        do_sync(vocab, load_base_rules(), quiet=True)
    elif args[0] == "--add" and len(args) >= 2:
        cmd_add(args[1])
    elif args[0] == "--list":
        cmd_list()
    elif args[0] == "--remove" and len(args) >= 2:
        cmd_remove(args[1])
    else:
        print(__doc__)
