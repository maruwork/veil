#!/usr/bin/env python3
"""
veil-lint: VEIL 語彙ルールに照らして利用者向け文章を検査する。

Usage:
  python shared/runtime/veil-lint.py <file>
  python shared/runtime/veil-lint.py --stdin
  python shared/runtime/veil-lint.py --text "..."
  python shared/runtime/veil-lint.py --json

Default authority:
  ~/.veil/rules/*.md
"""

from __future__ import annotations

import argparse
import bisect
import json
import os
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from shared.tools.veil_rule_store import (
    RULE_LINE_RE,
    first_preferred,
    load_rules_for_lint_from_db,
    simple_singularize_token,
)

CONFIG_DIR = os.path.expanduser("~/.veil")
DEFAULT_RULES_DIR = os.path.join(CONFIG_DIR, "rules")

FENCED_CODE_RE = re.compile(r"```.*?```", re.DOTALL)
INLINE_CODE_RE = re.compile(r"`[^`\n]*`")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="VEIL 語彙ルールに照らして文章を検査する。")
    parser.add_argument("path", nargs="?", help="検査対象のテキストファイル。")
    parser.add_argument("--stdin", action="store_true", help="標準入力から文章を読む。")
    parser.add_argument("--text", help="指定した文字列を直接検査する。")
    parser.add_argument("--json", action="store_true", help="JSON 形式で出力する。")
    parser.add_argument(
        "--rules-dir",
        default=DEFAULT_RULES_DIR,
        help="検査に使う rules directory を上書きする。既定: ~/.veil/rules",
    )
    parser.add_argument(
        "--db",
        help="SQLite source を使う時の DB path。指定時は rules-dir よりこちらを優先する。",
    )
    return parser.parse_args()


def canonical_original(term: str) -> str:
    return re.sub(r"[\s\-_]+", " ", term.strip().lower())


def load_rules(rules_dir: str) -> tuple[list[dict[str, str]], list[dict[str, object]]]:
    if not os.path.isdir(rules_dir):
        return [], []

    by_original: dict[str, dict[str, str]] = {}
    conflicts_by_key: dict[str, list[dict[str, str]]] = defaultdict(list)
    for fname in sorted(os.listdir(rules_dir)):
        if not fname.endswith(".md"):
            continue
        path = os.path.join(rules_dir, fname)
        try:
            with open(path, encoding="utf-8") as f:
                lines = f.readlines()
        except OSError:
            continue

        for line in lines:
            match = RULE_LINE_RE.match(line)
            if not match:
                continue
            original = match.group("original").strip()
            preferred = first_preferred(match.group("preferred"))
            if not original or not preferred:
                continue
            key = canonical_original(original)
            entry = {
                "original": original,
                "preferred": preferred,
                "source_file": fname,
            }
            if key not in by_original:
                by_original[key] = entry
            elif (
                by_original[key]["original"] != original
                or by_original[key]["preferred"] != preferred
            ):
                conflicts_by_key[key].append(entry)

    conflicts = []
    for key, entries in conflicts_by_key.items():
        conflicts.append(
            {
                "normalized": key,
                "selected": by_original[key],
                "ignored": entries,
            }
        )

    rules = [
        {
            "original": entry["original"],
            "preferred": entry["preferred"],
        }
        for entry in by_original.values()
    ]
    return rules, conflicts


def load_rules_for_source(rules_dir: str, db_path: str | None) -> tuple[str, str, list[dict[str, str]], list[dict[str, object]]]:
    if db_path:
        rules = load_rules_for_lint_from_db(db_path)
        return "db", db_path, rules, []
    rules, conflicts = load_rules(rules_dir)
    return "rules-dir", rules_dir, rules, conflicts


def build_original_pattern(original: str) -> re.Pattern[str]:
    tokens = [part for part in re.split(r"[\s\-_]+", original.strip()) if part]
    if not tokens:
        return re.compile(r"$^")
    normalized_tokens = [simple_singularize_token(token.lower()) for token in tokens]
    core = r"[\s\-_]+".join(plural_aware_token_pattern(token) for token in normalized_tokens)

    start_boundary = r"(?<![A-Za-z0-9])" if original[:1].isalnum() else ""
    end_boundary = r"(?![A-Za-z0-9])" if original[-1:].isalnum() else ""
    return re.compile(start_boundary + core + end_boundary, re.IGNORECASE)


def plural_aware_token_pattern(token: str) -> str:
    forms = [token]
    if re.search(r"[^aeiou]y$", token, re.IGNORECASE):
        forms.append(token[:-1] + "ies")
    elif token.lower().endswith("is") and len(token) > 2:
        forms.append(token[:-2] + "es")
    elif re.search(r"(ch|sh|x|z|s)$", token, re.IGNORECASE):
        forms.append(token + "es")
    else:
        forms.append(token + "s")
    escaped = sorted({re.escape(form) for form in forms}, key=len, reverse=True)
    return "(?:" + "|".join(escaped) + ")"


def mask_ranges(text: str, pattern: re.Pattern[str]) -> str:
    chars = list(text)
    for match in pattern.finditer(text):
        for idx in range(match.start(), match.end()):
            if chars[idx] != "\n":
                chars[idx] = " "
    return "".join(chars)


def mask_protected_segments(text: str) -> str:
    masked = mask_ranges(text, FENCED_CODE_RE)
    masked = mask_ranges(masked, INLINE_CODE_RE)
    return masked


def line_starts(text: str) -> list[int]:
    starts = [0]
    for idx, char in enumerate(text):
        if char == "\n":
            starts.append(idx + 1)
    return starts


def line_number(starts: list[int], pos: int) -> int:
    return bisect.bisect_right(starts, pos)


def line_text(text: str, line_no: int) -> str:
    lines = text.splitlines()
    if 1 <= line_no <= len(lines):
        return lines[line_no - 1].strip()
    return ""


def build_line_preview(excerpt: str, match_text: str, preferred: str) -> str:
    if not excerpt:
        return ""
    return excerpt.replace(match_text, preferred, 1)


def lint_text(text: str, rules: list[dict[str, str]]) -> list[dict[str, object]]:
    masked = mask_protected_segments(text)
    starts = line_starts(text)
    violations: list[dict[str, object]] = []

    for rule in rules:
        pattern = build_original_pattern(rule["original"])
        hits = []
        for match in pattern.finditer(masked):
            line_no = line_number(starts, match.start())
            matched_text = text[match.start():match.end()]
            excerpt = line_text(text, line_no)
            hits.append(
                {
                    "line": line_no,
                    "column": match.start() - starts[line_no - 1] + 1,
                    "match": matched_text,
                    "excerpt": excerpt,
                    "suggested_replacement": rule["preferred"],
                    "suggested_line_preview": build_line_preview(excerpt, matched_text, rule["preferred"]),
                }
            )
        if hits:
            violations.append(
                {
                    "original": rule["original"],
                    "preferred": rule["preferred"],
                    "count": len(hits),
                    "hits": hits,
                }
            )

    violations.sort(key=lambda item: item["hits"][0]["line"])
    return violations


def read_input(args: argparse.Namespace) -> str:
    if args.text is not None:
        return args.text
    if args.stdin or (args.path in (None, "-") and not sys.stdin.isatty()):
        return sys.stdin.read()
    if args.path:
        with open(args.path, encoding="utf-8") as f:
            return f.read()
    raise ValueError("No input text provided.")


def summarize_hits(results: list[dict[str, object]]) -> tuple[int, int]:
    return len(results), sum(item["count"] for item in results)


def print_bucket(items: list[dict[str, object]]) -> None:
    for item in items:
        lines = ", ".join(str(hit["line"]) for hit in item["hits"])
        print(f"- {item['original']} -> {item['preferred']} ({item['count']} 件, 行 {lines})")
        first_hit = item["hits"][0]["excerpt"]
        if first_hit:
            print(f"  {first_hit}")
        preview = item["hits"][0].get("suggested_line_preview") or ""
        if preview and preview != first_hit:
            print(f"  置換例: {preview}")


def print_text_result(violations: list[dict[str, object]], source_type: str, source_label: str) -> None:
    if not violations:
        print("CLEAN: 登録済み原語は文章中に見つかりませんでした。")
        return
    rule_count, hit_count = summarize_hits(violations)
    print(f"NG: {rule_count} rule(s), {hit_count} hit(s) from {source_type}:{source_label}")
    print_bucket(violations)


def print_conflicts(conflicts: list[dict[str, object]]) -> None:
    for conflict in conflicts:
        selected = conflict["selected"]
        ignored = ", ".join(
            f"{entry['original']} -> {entry['preferred']} ({entry['source_file']})"
            for entry in conflict["ignored"]
        )
        print(
            "警告: 正規化済みキー競合 "
            f"[{conflict['normalized']}] 採用 "
            f"{selected['original']} -> {selected['preferred']} ({selected['source_file']}), "
            f"ignored {ignored}",
            file=sys.stderr,
        )


def main() -> int:
    args = parse_args()
    try:
        text = read_input(args)
    except ValueError:
        print("使い方エラー: <file>、--stdin、--text のいずれかを指定してください。", file=sys.stderr)
        return 2
    except OSError as exc:
        print(f"読み込みエラー: {exc}", file=sys.stderr)
        return 2

    source_type, source_label, rules, conflicts = load_rules_for_source(args.rules_dir, args.db)
    if conflicts:
        print_conflicts(conflicts)
    if not rules:
        payload = {
            "status": "skip",
            "reason": "VEIL ルールが見つかりません。",
            "source_type": source_type,
            "source": source_label,
            "rules_dir": args.rules_dir,
            "db_path": args.db,
            "conflicts": conflicts,
        }
        if args.json:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            print(f"SKIP: {source_type}:{source_label} に VEIL ルールがありません")
        return 0

    violations = lint_text(text, rules)
    status = "violation" if violations else "clean"
    if args.json:
        payload = {
            "status": status,
            "source_type": source_type,
            "source": source_label,
            "rules_dir": args.rules_dir,
            "db_path": args.db,
            "conflicts": conflicts,
            "violations": violations,
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print_text_result(violations, source_type, source_label)

    return 1 if violations else 0


if __name__ == "__main__":
    sys.exit(main())
