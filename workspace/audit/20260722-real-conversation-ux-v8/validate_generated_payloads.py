"""Read-only v8 blind-output validation.

This module reads only a label-free runtime-input JSONL and a generated-frame
JSONL.  It deliberately has no reviewed-corpus, canonical-DB, or evaluator
argument, so the same operation can gate a disposable rehearsal, G7, and G8
preflight before any expected label is read.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from shared.tools.veil_decision_frames import (  # noqa: E402
    BLIND_GENERATED_ROW_FIELDS,
    FrameValidationError,
    analyze_decision_frames,
)


RUNTIME_FIELDS = frozenset({"session_id", "source_text", "registered_terms"})


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise ValueError(f"duplicate JSON key: {key}")
        value[key] = item
    return value


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        raise ValueError(f"required file is missing: {path}")
    rows: list[dict[str, Any]] = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            raise ValueError(f"{path.name}:{number}: blank JSONL line")
        value = json.loads(line, object_pairs_hook=_reject_duplicate_keys)
        if not isinstance(value, dict):
            raise ValueError(f"{path.name}:{number}: row must be an object")
        rows.append(value)
    if not rows:
        raise ValueError(f"{path.name} must contain at least one row")
    return rows


def _validate_runtime(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    by_session: dict[str, dict[str, Any]] = {}
    for number, row in enumerate(rows, start=1):
        if set(row) != RUNTIME_FIELDS:
            raise ValueError(f"runtime row {number} has an invalid field set")
        session_id = row.get("session_id")
        if not isinstance(session_id, str) or not session_id or session_id in by_session:
            raise ValueError(f"runtime row {number} has an invalid session_id")
        if not isinstance(row.get("source_text"), str) or not row["source_text"]:
            raise ValueError(f"runtime row {number} has an invalid source_text")
        registered_terms = row.get("registered_terms")
        if not isinstance(registered_terms, list) or any(not isinstance(term, str) for term in registered_terms):
            raise ValueError(f"runtime row {number} has invalid registered_terms")
        by_session[session_id] = row
    return by_session


def validate_generated_payloads(
    *, runtime_input: Path, generated_frames: Path, require_ascii_output: bool = True
) -> dict[str, Any]:
    """Validate a blind output without reading labels or any review artifact."""
    runtime_by_session = _validate_runtime(_read_jsonl(runtime_input))
    raw_output = generated_frames.read_bytes() if generated_frames.is_file() else None
    if raw_output is None:
        raise ValueError(f"required file is missing: {generated_frames}")
    if require_ascii_output:
        try:
            raw_output.decode("ascii")
        except UnicodeDecodeError as exc:
            raise ValueError("generated output must use ASCII-only JSON escapes") from exc
    output_rows = _read_jsonl(generated_frames)
    output_sessions: set[str] = set()
    validated_frame_count = 0
    for number, row in enumerate(output_rows, start=1):
        if set(row) != BLIND_GENERATED_ROW_FIELDS:
            raise ValueError(f"generated row {number} has an invalid outer envelope")
        session_id = row.get("session_id")
        payload = row.get("payload")
        if not isinstance(session_id, str) or session_id not in runtime_by_session or session_id in output_sessions:
            raise ValueError(f"generated row {number} has an invalid session_id")
        if not isinstance(payload, dict):
            raise ValueError(f"generated row {number} payload must be an object")
        runtime = runtime_by_session[session_id]
        try:
            analysis = analyze_decision_frames(runtime["source_text"], payload, runtime["registered_terms"])
        except FrameValidationError as exc:
            raise ValueError(f"generated row {number} has an invalid payload: {exc}") from exc
        validated_frame_count += analysis.validated_frame_count
        output_sessions.add(session_id)
    if output_sessions != set(runtime_by_session):
        raise ValueError("generated output session IDs do not exactly match runtime input")
    return {
        "status": "passed",
        "runtime_row_count": len(runtime_by_session),
        "output_row_count": len(output_rows),
        "validated_frame_count": validated_frame_count,
        "generated_sha256": hashlib.sha256(raw_output).hexdigest(),
        "ascii_output": require_ascii_output,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate v8 blind generated payloads without reading labels.")
    parser.add_argument("--runtime-input", type=Path, required=True)
    parser.add_argument("--generated-frames", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    print(json.dumps(validate_generated_payloads(runtime_input=args.runtime_input, generated_frames=args.generated_frames)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
