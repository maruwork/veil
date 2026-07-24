from __future__ import annotations

import importlib.util
import json
import sqlite3
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / "workspace/audit/20260723-real-conversation-ux-v10"
V4 = ROOT / "workspace/audit/20260721-independent-semantic-holdout-v4/frozen"
sys.path.insert(0, str(RUN))


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module


def fixture(tmp_path: Path):
    runner = load("v10_runner", RUN / "integration_runner.py")
    for name in ("runtime-input.jsonl", "generated-frames.jsonl", "frozen-corpus.jsonl"):
        (tmp_path / name).write_bytes((V4 / name).read_bytes())
    manifest_path, attestation_path = tmp_path / "manifest.json", tmp_path / "attestation.json"
    result = tmp_path / "results/first-run"; runtime = tmp_path / "runtime-input.jsonl"; generated = tmp_path / "generated-frames.jsonl"; corpus = tmp_path / "frozen-corpus.jsonl"
    relative = lambda path: path.relative_to(ROOT).as_posix()
    args = ["--corpus", relative(corpus), "--runtime-input", relative(runtime), "--generated-frames", relative(generated), "--manifest", relative(manifest_path), "--attestation", relative(attestation_path), "--result-dir", relative(result)]
    probe = tmp_path / "declared-source.py"; probe.write_text("before\n", encoding="utf-8")
    inventory = [RUN / "adapter_core.py", RUN / "integration_runner.py", ROOT / "workspace/audit/20260721-independent-semantic-holdout-v4/evaluate_semantic_holdout.py", probe]
    state = runner.compute_source_state(ROOT, inventory)
    manifest = {"contract_version":"2","holdout_id":"v10-disposable","status":"frozen","evaluator_args":args,"runtime_input":runner._record(ROOT,runtime),"reviewed_corpus":runner._record(ROOT,corpus),"source_state":state}
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    attestation = {"contract_version":"2","holdout_id":"v10-disposable","manifest":runner._record(ROOT,manifest_path),"runtime_input":manifest["runtime_input"],"reviewed_corpus":manifest["reviewed_corpus"],"source_state":state}
    attestation_path.write_text(json.dumps(attestation), encoding="utf-8")
    return runner, manifest_path, attestation_path, corpus, runtime, generated, result, args, inventory, probe


def test_disposable_v10_preflight_runtime_real_core_and_terminal_gates(tmp_path: Path) -> None:
    runner, manifest_path, attestation_path, corpus, runtime, generated, result, args, inventory, _probe = fixture(tmp_path)
    assert runner.run_once(root=ROOT,manifest_path=manifest_path,attestation_path=attestation_path,corpus=corpus,runtime=runtime,generated=generated,result_dir=result,args=args,inventory=inventory) == 0
    terminal = json.loads((result / "result-manifest.json").read_text(encoding="utf-8"))
    assert terminal["status"] == "scored"
    assert set(terminal["gates"]) == runner.ALL_GATES
    assert all(terminal["gates"].values())


def test_real_core_db_attempt_is_a_measured_terminal_runtime_error(tmp_path: Path) -> None:
    runner, manifest_path, attestation_path, corpus, runtime, generated, result, args, inventory, _probe = fixture(tmp_path)
    import shared.tools.veil_decision_frames as frames
    original = frames.analyze_decision_frames
    def db_attempt(*_args, **_kwargs):
        sqlite3.connect(":memory:")
    def inject():
        frames.analyze_decision_frames = db_attempt
    try:
        assert runner.run_once(root=ROOT,manifest_path=manifest_path,attestation_path=attestation_path,corpus=corpus,runtime=runtime,generated=generated,result_dir=result,args=args,inventory=inventory,after_runtime_start=inject) == 1
    finally:
        frames.analyze_decision_frames = original
    terminal = json.loads((result / "result-manifest.json").read_text(encoding="utf-8"))
    assert terminal["status"] == "runtime-error"
    assert terminal["runtime_access"] == {"canonical_db_access_attempts": 1, "raw_text_fallback_attempts": 0}


def test_real_core_raw_fallback_attempt_is_a_measured_terminal_runtime_error(tmp_path: Path) -> None:
    runner, manifest_path, attestation_path, corpus, runtime, generated, result, args, inventory, _probe = fixture(tmp_path)
    import shared.tools.veil_decision_frames as frames
    original = frames.analyze_decision_frames
    def raw_attempt(*_args, **_kwargs):
        runner.raw_text_fallback()
    def inject():
        frames.analyze_decision_frames = raw_attempt
    try:
        assert runner.run_once(root=ROOT,manifest_path=manifest_path,attestation_path=attestation_path,corpus=corpus,runtime=runtime,generated=generated,result_dir=result,args=args,inventory=inventory,after_runtime_start=inject) == 1
    finally:
        frames.analyze_decision_frames = original
    terminal = json.loads((result / "result-manifest.json").read_text(encoding="utf-8"))
    assert terminal["status"] == "runtime-error"
    assert terminal["runtime_access"] == {"canonical_db_access_attempts": 0, "raw_text_fallback_attempts": 1}


def test_post_start_exception_is_terminal(tmp_path: Path) -> None:
    runner, manifest_path, attestation_path, corpus, runtime, generated, result, args, inventory, _probe = fixture(tmp_path)
    def explode():
        raise ValueError("fixture post-start failure")
    assert runner.run_once(root=ROOT,manifest_path=manifest_path,attestation_path=attestation_path,corpus=corpus,runtime=runtime,generated=generated,result_dir=result,args=args,inventory=inventory,after_runtime_start=explode) == 1
    terminal = json.loads((result / "result-manifest.json").read_text(encoding="utf-8"))
    assert terminal["status"] == "runtime-error"
    assert terminal["runtime_error"] == {"type": "ValueError", "message": "fixture post-start failure"}


def test_declared_source_change_forces_a_false_source_state_gate(tmp_path: Path) -> None:
    runner, manifest_path, attestation_path, corpus, runtime, generated, result, args, inventory, probe = fixture(tmp_path)
    assert runner.run_once(root=ROOT,manifest_path=manifest_path,attestation_path=attestation_path,corpus=corpus,runtime=runtime,generated=generated,result_dir=result,args=args,inventory=inventory,after_runtime_start=lambda: probe.write_text("changed\n", encoding="utf-8")) == 1
    terminal = json.loads((result / "result-manifest.json").read_text(encoding="utf-8"))
    assert terminal["status"] == "scored"
    assert terminal["gates"]["source_state_unchanged"] is False


def test_real_core_score_mismatch_is_scored_failure_not_a_runtime_pass(tmp_path: Path) -> None:
    runner, manifest_path, attestation_path, corpus, runtime, generated, result, args, inventory, _probe = fixture(tmp_path)
    rows = [json.loads(line) for line in generated.read_text(encoding="utf-8").splitlines()]
    sentence = "The lattice beside the loading bay casts a narrow shadow each morning."
    rows[0]["payload"] = {"contract_version":"2","frames":[{"frame_id":"mismatch-1","term":"lattice","intent":"define","persistence":"durable","polarity":"affirmed","scope":"project","from_term":None,"preferred":None,"conflict_group":None,"impact":"high","term_evidence":{"text":"lattice","occurrence":1},"intent_evidence":[{"text":sentence,"occurrence":1}],"confidence":"high"}],"critic":{"status":"confirmed","confirmed_frame_ids":["mismatch-1"],"rejected_frame_ids":[],"unresolved_frame_ids":[],"missing_frames":[]}}
    generated.write_text("".join(json.dumps(row, ensure_ascii=True) + "\n" for row in rows), encoding="utf-8")
    assert runner.run_once(root=ROOT,manifest_path=manifest_path,attestation_path=attestation_path,corpus=corpus,runtime=runtime,generated=generated,result_dir=result,args=args,inventory=inventory) == 1
    terminal = json.loads((result / "result-manifest.json").read_text(encoding="utf-8"))
    assert terminal["status"] == "scored"
    assert terminal["gates"]["all_case_outcomes_exact"] is False


def test_preflight_rejection_creates_no_result_and_never_reaches_runtime_hook(tmp_path: Path) -> None:
    runner, manifest_path, attestation_path, corpus, runtime, generated, result, args, inventory, _probe = fixture(tmp_path)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["status"] = "invalid"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    called = False
    def runtime_hook():
        nonlocal called
        called = True
    try:
        runner.run_once(root=ROOT,manifest_path=manifest_path,attestation_path=attestation_path,corpus=corpus,runtime=runtime,generated=generated,result_dir=result,args=args,inventory=inventory,after_runtime_start=runtime_hook)
    except ValueError as exc:
        assert "metadata identity" in str(exc)
    else:
        raise AssertionError("invalid preflight unexpectedly started runtime")
    assert called is False
    assert result.exists() is False
