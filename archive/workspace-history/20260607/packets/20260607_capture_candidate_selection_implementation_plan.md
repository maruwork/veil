# 実装計画テンプレート準拠

**Task**: VEIL-TUNING-001-CANDIDATE-SELECTION  
**Author**: Codex  
**Date**: 2026-06-07  
**Status**: Draft

## 1. Packet Minimum Fields

| Field | Value |
|---|---|
| task_id | `VEIL-TUNING-001-CANDIDATE-SELECTION` |
| goal | normalize result に candidate selection hint を追加する |
| owner_role | owner / delegated AI |
| scope_in | normalize runtime, skills/docs/current |
| scope_out | lint/schema/UI |
| next_gate | selection hint smoke 完了 |

## 2. Implementation Decision Record

- background:
  - wave 1-3 closed
- decision:
  - wave 4 は capture candidate selection narrowing に入る
- rationale:
  - 候補を少数へ絞る運用を支えやすい
- completion conditions:
  - normalize result に selection hint が出る

## 3. Preconditions

| Check | Status | Notes |
|---|---|---|
| wave 1-3 closed | PASS | reports exist |
| normalize runtime stable | PASS | previous waves complete |
| scope narrow | PASS | output-only extension |

## 4. Files

| Path | Operation | Purpose |
|---|---|---|
| `workspace/20260607_capture_candidate_selection_*.md` | create | wave 4 packet |
| `veil-normalize.py` | modify | selection hint runtime |
| `README.md` | modify | normalize usage update |
| `docs/veil-design.md` | modify | normalize contract update |
| `skills/codex/veil-capture/SKILL.md` | modify | capture use guidance update |
| `skills/claude-code/veil-capture.md` | modify | capture use guidance update |
| `index/project-current-work.md` | modify | wave 4 current writeback |

## 5. Acceptance Mapping

| Acceptance ID | Implementation Point | Verification |
|---|---|---|
| A1 | result fields | json smoke |
| A2 | text output | text smoke |
| A3 | skills/docs wording | readback |

## 6. Verification Plan

- `python -m py_compile veil-normalize.py`
- `--text` smoke with mixed candidates
- readback for `selection_hint`

