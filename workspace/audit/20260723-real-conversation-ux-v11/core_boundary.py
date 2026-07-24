"""Production boundary between validated v11 runtime rows and the real v4 core."""
from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any, Callable


ROOT = Path(__file__).resolve().parents[3]
V10_ADAPTER = ROOT / "workspace/audit/20260723-real-conversation-ux-v10/adapter_core.py"


def _adapter() -> Any:
    spec = importlib.util.spec_from_file_location("veil_v11_real_adapter", V10_ADAPTER)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load real-v4 adapter")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def require_label_free_runtime(
    runtime_rows: list[dict[str, Any]],
    *,
    raw_text_fallback: Callable[[dict[str, Any], str], None],
) -> list[dict[str, Any]]:
    """Return rows safe for real-core scoring or invoke the production deny hook.

    A scorer never reconstructs a missing label-free runtime record from another
    text source. A missing or malformed source_text is the only fallback-shaped
    condition; the supplied callback records and rejects it.
    """
    prepared: list[dict[str, Any]] = []
    for row in runtime_rows:
        source = row.get("source_text") if isinstance(row, dict) else None
        terms = row.get("registered_terms") if isinstance(row, dict) else None
        if not isinstance(source, str) or not source or not isinstance(terms, list) or any(not isinstance(term, str) for term in terms):
            raw_text_fallback(row if isinstance(row, dict) else {}, "runtime row cannot be scored without its label-free source_text")
            raise AssertionError("raw_text_fallback must raise")
        prepared.append(row)
    return prepared


def score_real_core(
    *,
    runtime_rows: list[dict[str, Any]],
    generated_rows: list[dict[str, Any]],
    corpus_rows: list[dict[str, Any]],
    holdout_id: str,
    raw_text_fallback: Callable[[dict[str, Any], str], None],
) -> dict[str, Any]:
    prepared = require_label_free_runtime(runtime_rows, raw_text_fallback=raw_text_fallback)
    return _adapter().score_with_real_v4_core(
        root=ROOT,
        runtime_rows=prepared,
        generated_rows=generated_rows,
        corpus_rows=corpus_rows,
        holdout_id=holdout_id,
    )
