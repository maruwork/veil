# 実装計画テンプレート準拠

**Task**: VEIL-TUNING-001-NORMALIZE-SINGLE-WORD  
**Author**: Codex  
**Date**: 2026-06-07  
**Status**: Draft

## 1. Packet Minimum Fields

| Field | Value |
|---|---|
| task_id | `VEIL-TUNING-001-NORMALIZE-SINGLE-WORD` |
| goal | normalize の単語判定精度を保守的に改善する |
| owner_role | owner / delegated AI |
| scope_in | normalize runtime, docs/current |
| scope_out | lint/capture redesign |
| next_gate | normalize precision smoke 完了 |

## 2. Implementation Decision Record

- background:
  - tuning wave 1 で lint fix guidance は完了
- decision:
  - wave 2 は normalize single-word precision に入る
- rationale:
  - 精度側の改善として最も局所的で効果が高い
- completion conditions:
  - single-word lowercase 判定が少し改善される

## 3. Preconditions

| Check | Status | Notes |
|---|---|---|
| tuning wave 1 完了 | PASS | execution report 済み |
| normalize runtime stable | PASS | db/rules-dir route stable |
| scope narrow | PASS | single-word heuristic only |

## 4. Files

| Path | Operation | Purpose |
|---|---|---|
| `workspace/20260607_normalize_single_word_precision_*.md` | create | wave 2 packet |
| `veil-normalize.py` | modify | heuristic 改善 |
| `README.md` | modify | normalize hint wording update |
| `docs/veil-design.md` | modify | normalize hint wording update |
| `index/project-current-work.md` | modify | wave 2 current writeback |

## 5. Acceptance Mapping

| Acceptance ID | Implementation Point | Verification |
|---|---|---|
| A1 | single-word lowercase heuristic | text/json smoke |
| A2 | level suggestion remains conservative | smoke |
| A3 | identifier/proper-noun path unchanged | smoke |

## 6. Verification Plan

- `python -m py_compile veil-normalize.py`
- `--text` smoke with:
  - `verification`
  - `normalization`
  - `summary`
  - `close`
  - `GitHub`
  - `status=close`

## 7. 作業順序

1. packet を作る
2. heuristic を実装する
3. docs/current を追従させる
4. smoke と execution report を残す

