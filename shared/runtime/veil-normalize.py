#!/usr/bin/env python3
"""
veil-normalize: Normalize candidate terms and show integration candidates against VEIL rules.

Usage:
  python shared/runtime/veil-normalize.py <file>
  python shared/runtime/veil-normalize.py --stdin
  python shared/runtime/veil-normalize.py --text "..."
  python shared/runtime/veil-normalize.py --json
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from shared.tools.veil_rule_store import (
    LEADING_BULLET_RE,
    RULE_LINE_RE,
    first_preferred,
    load_rule_index_from_db,
    normalize_term,
)
from shared.tools.veil_locale import t

CONFIG_DIR = os.path.expanduser("~/.veil")
DEFAULT_RULES_DIR = os.path.join(CONFIG_DIR, "rules")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=t("normalize.description"))
    parser.add_argument("path", nargs="?", help=t("normalize.path_help"))
    parser.add_argument("--stdin", action="store_true", help=t("normalize.stdin_help"))
    parser.add_argument("--text", help=t("normalize.text_help"))
    parser.add_argument("--json", action="store_true", help=t("normalize.json_help"))
    parser.add_argument(
        "--rules-dir",
        default=DEFAULT_RULES_DIR,
        help=t("normalize.rules_dir_help"),
    )
    parser.add_argument(
        "--db",
        help=t("normalize.db_help"),
    )
    return parser.parse_args()


def target_file_for(term: str) -> str:
    cleaned = LEADING_BULLET_RE.sub("", term.strip()).lower()
    if not cleaned:
        return "special.md"
    first = cleaned[0]
    return f"{first}.md" if "a" <= first <= "z" else "special.md"


def read_input(args: argparse.Namespace) -> str:
    if args.text is not None:
        return args.text
    if args.stdin or (args.path in (None, "-") and not sys.stdin.isatty()):
        return sys.stdin.read()
    if args.path:
        with open(args.path, encoding="utf-8") as f:
            return f.read()
    raise ValueError("No input candidate terms provided.")


def parse_candidate_lines(text: str) -> list[str]:
    candidates: list[str] = []
    for raw in text.splitlines():
        term = LEADING_BULLET_RE.sub("", raw.strip())
        if not term:
            continue
        candidates.append(term)
    return candidates


def load_rule_index(rules_dir: str) -> tuple[dict[str, dict[str, str]], list[dict[str, object]]]:
    if not os.path.isdir(rules_dir):
        return {}, []
    index: dict[str, dict[str, str]] = {}
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
            key = normalize_term(original)
            if not key:
                continue
            entry = {
                "original": original,
                "preferred": preferred,
                "source_file": fname,
            }
            if key not in index:
                index[key] = entry
            elif (
                index[key]["original"] != original
                or index[key]["preferred"] != preferred
            ):
                conflicts_by_key[key].append(entry)
    conflicts = []
    for key, entries in conflicts_by_key.items():
        conflicts.append(
            {
                "normalized": key,
                "selected": index[key],
                "ignored": entries,
            }
        )
    return index, conflicts


def load_rule_index_for_source(rules_dir: str, db_path: str | None) -> tuple[str, dict[str, dict[str, str]], list[dict[str, object]]]:
    if db_path:
        index, conflicts = load_rule_index_from_db(db_path)
        return db_path, index, conflicts
    index, conflicts = load_rule_index(rules_dir)
    return rules_dir, index, conflicts


def choose_display_variant(variant_counts: dict[str, int]) -> str:
    return sorted(
        variant_counts,
        key=lambda item: (-variant_counts[item], len(item), item.lower(), item),
    )[0]


def cluster_candidates(candidates: list[str], rule_index: dict[str, dict[str, str]]) -> list[dict[str, object]]:
    grouped_counts: dict[str, dict[str, int]] = {}
    grouped_totals: dict[str, int] = {}
    for term in candidates:
        key = normalize_term(term)
        if not key:
            continue
        grouped_totals[key] = grouped_totals.get(key, 0) + 1
        variants = grouped_counts.setdefault(key, {})
        variants[term] = variants.get(term, 0) + 1

    results: list[dict[str, object]] = []
    for key in sorted(grouped_counts, key=lambda item: (-grouped_totals[item], item)):
        variant_counts = grouped_counts[key]
        variants = sorted(
            variant_counts,
            key=lambda item: (-variant_counts[item], item.lower(), item),
        )
        representative = choose_display_variant(variant_counts)
        occurrence_count = grouped_totals[key]
        existing = rule_index.get(key)
        if existing:
            results.append(
                {
                    "normalized": key,
                    "status": "existing-match",
                    "occurrence_count": occurrence_count,
                    "representative": representative,
                    "variants": variants,
                    "preferred": existing["preferred"],
                    "source_file": existing["source_file"],
                }
            )
        else:
            results.append(
                {
                    "normalized": key,
                    "status": "new-candidate",
                    "occurrence_count": occurrence_count,
                    "representative": representative,
                    "variants": variants,
                    "target_file": target_file_for(representative),
                }
            )
    return results


def print_conflicts(conflicts: list[dict[str, object]]) -> None:
    for conflict in conflicts:
        selected = conflict["selected"]
        ignored = ", ".join(
            f"{entry['original']} -> {entry['preferred']} ({entry['source_file']})"
            for entry in conflict["ignored"]
        )
        print(
            t(
                "normalize.conflict_warning",
                normalized=conflict["normalized"],
                original=selected["original"],
                preferred=selected["preferred"],
                source_file=selected["source_file"],
                ignored=ignored,
            ),
            file=sys.stderr,
        )


def compact_source_label(source_label: str) -> str:
    normalized = source_label.replace("\\", "/").rstrip("/")
    if not normalized:
        return source_label
    tail = normalized.rsplit("/", 1)[-1]
    return tail or source_label


def print_text_result(results: list[dict[str, object]], source_label: str) -> None:
    print(t("normalize.source_label", label=compact_source_label(source_label)))
    if not results:
        print(t("normalize.no_candidates"))
        return
    existing_items = [item for item in results if item["status"] == "existing-match"]
    new_items = [item for item in results if item["status"] == "new-candidate"]
    if existing_items:
        print()
        print(t("normalize.existing_header"))
        for item in existing_items:
            print(f"- {item['representative']} → {item['preferred']}")
    if new_items:
        print()
        print(t("normalize.new_header"))
        for item in new_items:
            suffix = f" x{item['occurrence_count']}" if item["occurrence_count"] > 1 else ""
            print(f"- {item['representative']}{suffix} → {item['target_file']}")


def main() -> int:
    args = parse_args()
    try:
        text = read_input(args)
    except ValueError:
        print(t("normalize.usage_error"), file=sys.stderr)
        return 2
    except OSError as exc:
        print(t("normalize.read_error", exc=exc), file=sys.stderr)
        return 2

    candidates = parse_candidate_lines(text)
    source_label, rule_index, conflicts = load_rule_index_for_source(args.rules_dir, args.db)
    results = cluster_candidates(candidates, rule_index)
    if conflicts:
        print_conflicts(conflicts)

    if args.json:
        existing = [item for item in results if item["status"] == "existing-match"]
        new = [item for item in results if item["status"] == "new-candidate"]
        payload = {
            "source_type": "db" if args.db else "rules-dir",
            "source": source_label,
            "candidate_count": len(candidates),
            "existing": existing,
            "new": new,
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print_text_result(results, source_label)
    return 0


if __name__ == "__main__":
    sys.exit(main())
