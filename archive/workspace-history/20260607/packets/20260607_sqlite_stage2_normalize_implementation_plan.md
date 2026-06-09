# 実装計画テンプレート準拠

**Task**: VEIL-CANONICAL-003-STAGE2-WAVE2  
**Author**: Codex  
**Date**: 2026-06-07  
**Status**: Draft

## 1. Packet Minimum Fields

| Field | Value |
|---|---|
| task_id | `VEIL-CANONICAL-003-STAGE2-WAVE2` |
| goal | normalize の SQLite source route を追加する |
| owner_role | owner / delegated AI |
| scope_in | normalize packet, `veil-normalize.py`, helper update, smoke |
| scope_out | lint switch |
| next_gate | lint wave packet |

## 2. Implementation Decision Record

- background:
  - audit wave は完了済み
- decision:
  - `veil-normalize.py` に `--db` source を追加し、db index helper を shared module に置く
- rationale:
  - existing-match contract を保ちながら read path を進めるため
- rejected alternatives:
  - normalize file 内で独自 db query
- impact scope:
  - `veil-normalize.py`
  - `veil_rule_store.py`
  - docs/current minimal writeback
- completion conditions:
  - same fixture / db で existing-match が返る
- SSOT declaration when data contracts are involved:
  - existing-match output contract in `veil-normalize.py`

## 3. Preconditions

| Check | Status | Notes |
|---|---|---|
| scope が承認済み | PASS | current next action と一致 |
| dependency が利用可能 | PASS | Stage 1 DB + helper あり |
| 関連 docs が current | PASS | audit wave writeback 済み |

## 4. Files

| Path | Operation | Purpose |
|---|---|---|
| `workspace/20260607_sqlite_stage2_normalize_requirements.md` | create | normalize wave requirements |
| `workspace/20260607_sqlite_stage2_normalize_basic_design.md` | create | normalize wave design |
| `workspace/20260607_sqlite_stage2_normalize_implementation_plan.md` | create | normalize wave plan |
| `workspace/20260607_sqlite_stage2_normalize_task_design.md` | create | normalize wave task design |
| `veil_rule_store.py` | modify | db index helper |
| `veil-normalize.py` | modify | add `--db` route |
| `README.md` | modify | normalize wave note |
| `docs/veil-design.md` | modify | normalize source note |
| `index/project-current-work.md` | modify | next action update |

## 5. Acceptance Mapping

| Acceptance ID | Implementation Point | Verification |
|---|---|---|
| C1 | normalize `--db` route | db smoke output |
| C2 | existing-match contract | JSON key presence |
| C3 | rules-dir compatibility | existing fixture output |
| C4 | compile pass | `python -m py_compile` |

## 6. Verification Plan

- planned checks:
  - `python -m py_compile veil_rule_store.py veil-normalize.py`
  - `python veil-normalize.py --text \"current state\" --rules-dir workspace/veil_stage1_rules_fixture --json`
  - `python veil-normalize.py --text \"current state\" --db workspace/veil_stage1_smoke.db --json`
- planned tests:
  - existing-match parity
  - text output source label
- evidence surface:
  - CLI output
  - execution report

## 7. 作業順序

1. normalize wave packet を作る
2. shared db index helper を追加する
3. normalize source selection を実装する
4. rules-dir/db 両方で smoke する
5. docs/current を最小 writeback する

## 8. Idempotency and Side Effects

- Idempotency type:
  - idempotent
- Writes:
  - repo files
- External calls:
  - なし
- Retry behavior:
  - source option と fixture を変えて再検証可能

## 9. Risks

| Risk | Level | Mitigation |
|---|---|---|
| existing-match field drift | high | JSON key smoke を入れる |
| text output ambiguity | medium | source label を出す |
