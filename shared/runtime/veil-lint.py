#!/usr/bin/env python3
"""
veil-lint: Check text against VEIL vocabulary rules.

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
from typing import Any
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
    normalize_term,
    simple_singularize_token,
)
from shared.tools.veil_locale import t

CONFIG_DIR = os.path.expanduser("~/.veil")
DEFAULT_RULES_DIR = os.path.join(CONFIG_DIR, "rules")

FENCED_CODE_RE = re.compile(r"(?ms)(^|\n)(?P<fence>`{3,}|~{3,})[^\n]*\n.*?\n[ \t]*(?P=fence)[ \t]*(?=\n|$)")
INLINE_CODE_RE = re.compile(r"`[^`\n]*`")
INDENTED_CODE_RE = re.compile(r"(?m)(?:^(?: {4}|\t).*(?:\n|$))+")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=t("lint.description"))
    parser.add_argument("path", nargs="?", help=t("lint.path_help"))
    parser.add_argument("--stdin", action="store_true", help=t("lint.stdin_help"))
    parser.add_argument("--text", help=t("lint.text_help"))
    parser.add_argument("--json", action="store_true", help=t("lint.json_help"))
    parser.add_argument(
        "--rules-dir",
        default=DEFAULT_RULES_DIR,
        help=t("lint.rules_dir_help"),
    )
    parser.add_argument(
        "--db",
        help=t("lint.db_help"),
    )
    return parser.parse_args()


def load_rules(rules_dir: str) -> tuple[list[dict[str, str]], list[dict[str, Any]]]:
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
            key = normalize_term(original)
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


def load_rules_for_source(
    rules_dir: str,
    db_path: str | None,
) -> tuple[str, str, list[dict[str, str]], list[dict[str, Any]], dict[str, Any] | None]:
    if db_path:
        status, rules, payload = load_rules_for_lint_from_db(db_path)
        return "db", db_path, rules, [], payload if status == "error" else None
    rules, conflicts = load_rules(rules_dir)
    return "rules-dir", rules_dir, rules, conflicts, None


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
    masked = mask_ranges(masked, INDENTED_CODE_RE)
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


def lint_text(text: str, rules: list[dict[str, str]]) -> list[dict[str, Any]]:
    masked = mask_protected_segments(text)
    starts = line_starts(text)
    violations: list[dict[str, Any]] = []

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


def summarize_hits(results: list[dict[str, Any]]) -> tuple[int, int]:
    return len(results), sum(item["count"] for item in results)


def print_bucket(items: list[dict[str, Any]]) -> None:
    for item in items:
        lines = ", ".join(str(hit["line"]) for hit in item["hits"])
        print(f"- {item['original']} -> {item['preferred']} {t('lint.hit_count', count=item['count'], lines=lines)}")
        first_hit = item["hits"][0]["excerpt"]
        if first_hit:
            print(f"  {first_hit}")
        preview = item["hits"][0].get("suggested_line_preview") or ""
        if preview and preview != first_hit:
            print(t("lint.suggested", preview=preview))


def print_text_result(violations: list[dict[str, Any]], source_type: str, source_label: str) -> None:
    if not violations:
        print(t("lint.clean"))
        return
    rule_count, hit_count = summarize_hits(violations)
    print(f"NG: {rule_count} rule(s), {hit_count} hit(s) from {source_type}:{source_label}")
    print_bucket(violations)


def print_conflicts(conflicts: list[dict[str, Any]]) -> None:
    for conflict in conflicts:
        selected = conflict["selected"]
        ignored = ", ".join(
            f"{entry['original']} -> {entry['preferred']} ({entry['source_file']})"
            for entry in conflict["ignored"]
        )
        print(
            t(
                "lint.conflict_warning",
                normalized=conflict["normalized"],
                original=selected["original"],
                preferred=selected["preferred"],
                source_file=selected["source_file"],
                ignored=ignored,
            ),
            file=sys.stderr,
        )


def main() -> int:
    args = parse_args()
    try:
        text = read_input(args)
    except ValueError:
        print(t("lint.usage_error"), file=sys.stderr)
        return 2
    except OSError as exc:
        print(t("lint.read_error", exc=exc), file=sys.stderr)
        return 2

    source_type, source_label, rules, conflicts, source_error = load_rules_for_source(args.rules_dir, args.db)
    if source_error is not None:
        payload = {
            "status": "error",
            "reason": t(str(source_error.get("reason"))),
            "source_type": source_type,
            "source": source_label,
            "rules_dir": args.rules_dir,
            "db_path": args.db,
            "conflicts": conflicts,
            "error": source_error.get("error"),
        }
        if args.json:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            detail = f" ({source_error['error']})" if source_error.get("error") else ""
            print(t("lint.source_error", source_type=source_type, source_label=source_label, reason=payload["reason"]) + detail)
        return 2
    if conflicts:
        print_conflicts(conflicts)
    if not rules:
        payload = {
            "status": "skip",
            "reason": t("lint.no_rules_reason"),
            "source_type": source_type,
            "source": source_label,
            "rules_dir": args.rules_dir,
            "db_path": args.db,
            "conflicts": conflicts,
        }
        if args.json:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            print(t("lint.no_rules", source_type=source_type, source_label=source_label))
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
