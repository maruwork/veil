from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
ADAPTER_PATH = ROOT / "workspace/audit/20260723-real-conversation-ux-v10/adapter_core.py"
FROZEN = ROOT / "workspace/audit/20260721-independent-semantic-holdout-v4/frozen"


def load_adapter():
    spec = importlib.util.spec_from_file_location("v10_adapter_core", ADAPTER_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_adapter_loads_the_real_v4_file_and_never_invokes_legacy_main(monkeypatch: pytest.MonkeyPatch) -> None:
    adapter = load_adapter()
    core = adapter.load_real_v4_core(ROOT)
    assert Path(core.__file__).resolve() == ROOT / adapter.V4_CORE_RELATIVE

    def forbidden_main():
        raise AssertionError("v10 adapter must not call v4 main")

    monkeypatch.setattr(core, "main", forbidden_main)
    monkeypatch.setattr(adapter, "load_real_v4_core", lambda _root: core)
    scored = adapter.score_with_real_v4_core(
        root=ROOT,
        runtime_rows=core.read_jsonl(FROZEN / "runtime-input.jsonl"),
        generated_rows=core.read_jsonl(FROZEN / "generated-frames.jsonl"),
        corpus_rows=core.read_jsonl(FROZEN / "frozen-corpus.jsonl"),
        holdout_id="fixture",
    )
    assert all(scored["summary"]["gates"].values())


def test_adapter_boundary_scores_through_the_real_module() -> None:
    adapter = load_adapter()
    core = adapter.load_real_v4_core(ROOT)
    scored = adapter.score_with_real_v4_core(
        root=ROOT,
        runtime_rows=core.read_jsonl(FROZEN / "runtime-input.jsonl"),
        generated_rows=core.read_jsonl(FROZEN / "generated-frames.jsonl"),
        corpus_rows=core.read_jsonl(FROZEN / "frozen-corpus.jsonl"),
        holdout_id="fixture",
    )
    assert scored["summary"]["holdout_id"] == "fixture"
    assert set(scored["summary"]["gates"]) == core.CORE_SCORE_GATES
