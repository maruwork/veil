from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import sqlite3
import sys
from types import ModuleType
from typing import Any, Callable
from unittest.mock import patch

from holdout_integrity import _validate_source_state, validate_preflight


ROOT = Path(__file__).resolve().parents[3]
CORE = ROOT / "workspace/audit/20260721-independent-semantic-holdout-v4/evaluate_semantic_holdout.py"


class RuntimeAccessAudit:
    """Measured, fail-closed counters for capabilities barred during scoring."""

    def __init__(self) -> None:
        self.canonical_db_access_attempts = 0
        self.raw_text_fallback_attempts = 0
        self.semantic_frame_calls = 0

    def forbid_db_connect(self, *args: object, **kwargs: object) -> object:
        self.canonical_db_access_attempts += 1
        raise RuntimeError("canonical DB access is prohibited during blinded evaluation")

    def forbid_raw_text_fallback(self, *args: object, **kwargs: object) -> object:
        self.raw_text_fallback_attempts += 1
        raise RuntimeError("raw-text fallback is prohibited during blinded evaluation")

    def result_fields(self) -> dict[str, object]:
        return {
            "canonical_db_access_attempts": self.canonical_db_access_attempts,
            "raw_text_fallback_attempts": self.raw_text_fallback_attempts,
            "semantic_frame_calls": self.semantic_frame_calls,
            "canonical_db_access_performed": self.canonical_db_access_attempts > 0,
            "raw_text_fallback_count": self.raw_text_fallback_attempts,
        }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate a frozen v7 real-conversation holdout once.")
    parser.add_argument("--corpus", type=Path, required=True)
    parser.add_argument("--runtime-input", type=Path, required=True)
    parser.add_argument("--generated-frames", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--attestation", type=Path, required=True)
    parser.add_argument("--result-dir", type=Path, required=True)
    return parser.parse_args(argv)


def project_path(root: Path, path: Path) -> Path:
    return path if path.is_absolute() else root / path


def load_core(core_path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location("v7_scoring_core", core_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load v7 scoring core")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path.name} must contain an object")
    return value


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def finalize_runtime_audit(result_dir: Path, audit: RuntimeAccessAudit, *, error: Exception | None = None) -> int:
    """Write measured access evidence after a scorer has created first-run state."""
    manifest_path = result_dir / "result-manifest.json"
    if not manifest_path.is_file():
        raise RuntimeError("scoring core did not create a runtime-started manifest")
    manifest = read_json(manifest_path)
    manifest.update(audit.result_fields())
    if error is not None:
        manifest.update(
            {
                "status": "runtime-error",
                "runtime_error": {"type": type(error).__name__, "message": str(error)},
            }
        )
        write_json(manifest_path, manifest)
        return 1

    summary_path = result_dir / "summary.json"
    if not summary_path.is_file():
        raise RuntimeError("scoring core completed without a summary")
    summary = read_json(summary_path)
    gates = summary.get("gates")
    if not isinstance(gates, dict):
        raise ValueError("scoring summary gates are invalid")
    gates["zero_raw_text_fallback"] = audit.raw_text_fallback_attempts == 0
    gates["no_canonical_db_access"] = audit.canonical_db_access_attempts == 0
    passed = all(value is True for value in gates.values())
    summary["gates"] = gates
    summary["status"] = "passed" if passed else "failed"
    write_json(summary_path, summary)
    manifest.update({"status": summary["status"], "gates": gates})
    write_json(manifest_path, manifest)
    return 0 if passed else 1


def run(
    argv: list[str],
    *,
    project_root: Path = ROOT,
    core_loader: Callable[[Path], ModuleType] = load_core,
    verify_git_state: bool = True,
) -> int:
    """Run exactly one preflighted evaluation with measured forbidden-access gates."""
    root = project_root.resolve()
    args = parse_args(argv)
    validate_preflight(
        project_root=root,
        corpus=project_path(root, args.corpus),
        runtime_input=project_path(root, args.runtime_input),
        generated_frames=project_path(root, args.generated_frames),
        manifest_path=project_path(root, args.manifest),
        attestation_path=project_path(root, args.attestation),
        result_dir=project_path(root, args.result_dir),
        evaluator_args=argv,
        verify_git_state=verify_git_state,
    )
    module = core_loader(root / CORE.relative_to(ROOT))
    audit = RuntimeAccessAudit()
    # The generic scorer resolves its CLI paths through this module-level root.
    # Keeping it equal to the preflight root makes test fixtures and production
    # execution use the same verified path boundary.
    module.PROJECT_ROOT = root

    # The reused scorer asks this hook before and after scoring. Keep the v7
    # inventory/source-state contract instead of accepting the v4 shape.
    def compute_v7_source_state(manifest: dict[str, object]) -> dict[str, object]:
        value = manifest.get("source_state")
        _validate_source_state(root, value, verify_git_state=verify_git_state)
        return value  # type: ignore[return-value]

    module.compute_source_state = compute_v7_source_state
    module.runtime_access_snapshot = audit.result_fields
    module.raw_text_fallback = audit.forbid_raw_text_fallback
    from shared.tools import veil_decision_frames  # noqa: PLC0415

    original_analyze = veil_decision_frames.analyze_decision_frames

    def audited_analyze(*args: object, **kwargs: object) -> object:
        audit.semantic_frame_calls += 1
        return original_analyze(*args, **kwargs)

    original_argv = sys.argv
    sys.argv = [str(CORE), *argv]
    result_dir = project_path(root, args.result_dir)
    try:
        with patch.object(sqlite3, "connect", audit.forbid_db_connect), patch.object(
            veil_decision_frames, "analyze_decision_frames", audited_analyze
        ):
            result = module.main()
    except Exception as exc:
        if (result_dir / "result-manifest.json").is_file():
            return finalize_runtime_audit(result_dir, audit, error=exc)
        raise
    finally:
        sys.argv = original_argv
    return finalize_runtime_audit(result_dir, audit) if (result_dir / "result-manifest.json").is_file() else result


def main() -> int:
    return run(sys.argv[1:])


if __name__ == "__main__":
    raise SystemExit(main())
