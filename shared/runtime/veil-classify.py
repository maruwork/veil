#!/usr/bin/env python3
"""
veil-classify: Classify capture-like terms from free-form text.

Usage:
  python shared/runtime/veil-classify.py --text "..."
  python shared/runtime/veil-classify.py --stdin
  python shared/runtime/veil-classify.py <file>
  python shared/runtime/veil-classify.py --json
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from shared.tools.veil_capture_classifier import (
    extract_adoptable_terms,
    extract_classified_terms,
    extract_investigation_terms,
    extract_preview_terms,
)
from shared.tools.veil_rule_store import DEFAULT_DB_PATH, load_rule_index_from_db


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Classify VEIL capture candidates from free-form text.")
    parser.add_argument("path", nargs="?", help="Text file to classify.")
    parser.add_argument("--stdin", action="store_true", help="Read text from stdin.")
    parser.add_argument("--text", help="Inline text to classify.")
    parser.add_argument(
        "--chat-json",
        action="store_true",
        help="Treat input as chat transcript JSON and extract message text before classification.",
    )
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument(
        "--adoptable-only",
        action="store_true",
        help="Return only repeated local wording that VEIL would still consider worth registering.",
    )
    mode_group.add_argument(
        "--preview-only",
        action="store_true",
        help="Return high-signal preview terms, including single-occurrence draft candidates.",
    )
    mode_group.add_argument(
        "--investigation-only",
        action="store_true",
        help="Return broader draft-investigation terms for HTML review, including suspicious mixed-language singles.",
    )
    parser.add_argument("--db", default=DEFAULT_DB_PATH, help="DB path used to mark already registered terms.")
    parser.add_argument("--json", action="store_true", help="Output JSON.")
    return parser.parse_args()


def read_input(args: argparse.Namespace) -> str:
    if args.text is not None:
        text = args.text
    elif args.stdin or (args.path in (None, "-") and not sys.stdin.isatty()):
        text = sys.stdin.read()
    elif args.path:
        with open(args.path, encoding="utf-8") as handle:
            text = handle.read()
    else:
        raise ValueError("No input text provided.")
    if not text.strip():
        raise ValueError("No input text provided.")
    return text


def load_registered_terms(db_path: str) -> set[str]:
    if not os.path.exists(db_path):
        return set()
    status, index, _, _ = load_rule_index_from_db(db_path)
    if status != "ok":
        return set()
    return set(index.keys())


TEXTUAL_LIST_KEYS = ("messages", "conversation", "turns", "items", "parts")
TEXTUAL_VALUE_KEYS = ("text", "content", "value", "message", "body")


def _extract_chat_segments(payload: Any) -> list[str]:
    if payload is None:
        return []
    if isinstance(payload, str):
        stripped = payload.strip()
        return [stripped] if stripped else []
    if isinstance(payload, list):
        segments: list[str] = []
        for item in payload:
            segments.extend(_extract_chat_segments(item))
        return segments
    if not isinstance(payload, dict):
        return []

    segments: list[str] = []
    for key, value in payload.items():
        if key in TEXTUAL_LIST_KEYS or key in TEXTUAL_VALUE_KEYS:
            segments.extend(_extract_chat_segments(value))
    return segments


def extract_text_from_chat_json(raw: str) -> str:
    payload = json.loads(raw)
    segments = _extract_chat_segments(payload)
    return "\n".join(segments)


def main() -> int:
    args = parse_args()
    try:
        text = read_input(args)
        if args.chat_json:
            text = extract_text_from_chat_json(text)
    except json.JSONDecodeError as exc:
        print(f"ERROR: Invalid chat JSON: {exc}", file=sys.stderr)
        return 1
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    registered_terms = load_registered_terms(args.db)
    if args.adoptable_only:
        extract_terms = extract_adoptable_terms
    elif args.investigation_only:
        extract_terms = extract_investigation_terms
    elif args.preview_only:
        extract_terms = extract_preview_terms
    else:
        extract_terms = extract_classified_terms
    results = [item.to_dict() for item in extract_terms(text, registered_terms=registered_terms)]
    if args.json:
        print(json.dumps({"results": results}, ensure_ascii=False, indent=2))
        return 0

    if not results:
        print("NO-TERMS")
        return 0

    for item in results:
        print(f"{item['label']}\t{item['term']}\t{item['reason']}\toccurrences={item['occurrences']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
