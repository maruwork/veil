"""v10 boundary for invoking the real v4 scoring kernel after strict preflight."""
from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any


V4_CORE_RELATIVE = Path("workspace/audit/20260721-independent-semantic-holdout-v4/evaluate_semantic_holdout.py")


def load_real_v4_core(root: Path) -> Any:
    path = (root / V4_CORE_RELATIVE).resolve()
    spec = importlib.util.spec_from_file_location("v10_real_v4_scoring_core", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load the real v4 scoring core")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if Path(module.__file__).resolve() != path or not callable(getattr(module, "score_prevalidated", None)):
        raise RuntimeError("loaded module is not the required real v4 scoring core")
    return module


def score_with_real_v4_core(
    *,
    root: Path,
    runtime_rows: list[dict[str, Any]],
    generated_rows: list[dict[str, Any]],
    corpus_rows: list[dict[str, Any]],
    holdout_id: str,
) -> dict[str, Any]:
    """Invoke only the side-effect-free real-core kernel; never legacy main()."""
    core = load_real_v4_core(root)
    return core.score_prevalidated(
        runtime_rows=runtime_rows,
        generated_rows=generated_rows,
        corpus_rows=corpus_rows,
        holdout_id=holdout_id,
    )
