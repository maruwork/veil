"""Read-only v9 validation for exact Unicode evidence in blind output."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from shared.tools.veil_decision_frames import BLIND_GENERATED_ROW_FIELDS, FrameValidationError, analyze_decision_frames

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


def validate_generated_payloads(*, runtime_input: Path, generated_frames: Path, require_ascii_output: bool = True) -> dict[str, Any]:
    runtime: dict[str, dict[str, Any]] = {}
    for number, row in enumerate(_read_jsonl(runtime_input), start=1):
        if set(row) != RUNTIME_FIELDS or not isinstance(row.get("session_id"), str) or not row["session_id"] or row["session_id"] in runtime:
            raise ValueError(f"runtime row {number} has an invalid field set or session")
        if not isinstance(row.get("source_text"), str) or not row["source_text"] or not isinstance(row.get("registered_terms"), list) or any(not isinstance(term, str) for term in row["registered_terms"]):
            raise ValueError(f"runtime row {number} is invalid")
        runtime[row["session_id"]] = row
    raw = generated_frames.read_bytes() if generated_frames.is_file() else None
    if raw is None:
        raise ValueError(f"required file is missing: {generated_frames}")
    if require_ascii_output:
        try:
            raw.decode("ascii")
        except UnicodeDecodeError as exc:
            raise ValueError("generated output must use ASCII-only JSON escapes") from exc
    seen: set[str] = set(); frame_count = 0
    for number, row in enumerate(_read_jsonl(generated_frames), start=1):
        if set(row) != BLIND_GENERATED_ROW_FIELDS or not isinstance(row.get("session_id"), str) or row["session_id"] not in runtime or row["session_id"] in seen or not isinstance(row.get("payload"), dict):
            raise ValueError(f"generated row {number} has an invalid outer envelope")
        try:
            analysis = analyze_decision_frames(runtime[row["session_id"]]["source_text"], row["payload"], runtime[row["session_id"]]["registered_terms"])
        except FrameValidationError as exc:
            raise ValueError(f"generated row {number} has invalid exact evidence: {exc}") from exc
        frame_count += analysis.validated_frame_count; seen.add(row["session_id"])
    if seen != set(runtime):
        raise ValueError("generated output session IDs do not exactly match runtime input")
    return {"status": "passed", "runtime_row_count": len(runtime), "output_row_count": len(seen), "validated_frame_count": frame_count, "generated_sha256": hashlib.sha256(raw).hexdigest(), "ascii_output": require_ascii_output}
