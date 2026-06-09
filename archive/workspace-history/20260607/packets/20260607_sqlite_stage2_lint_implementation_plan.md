# 実装計画テンプレート準拠

**Task**: VEIL-CANONICAL-003-STAGE2-WAVE3  
**Author**: Codex  
**Date**: 2026-06-07  
**Status**: Draft

## 1. Packet Minimum Fields

| Field | Value |
|---|---|
| task_id | `VEIL-CANONICAL-003-STAGE2-WAVE3` |
| goal | lint の SQLite source route を追加する |
| owner_role | owner / delegated AI |
| scope_in | lint packet, `veil-lint.py`, helper update, smoke |
| scope_out | capture write switch, sync generated route |
| next_gate | SQLite canonical docs authority update packet |

## 2. Implementation Decision Record

- background:
  - audit と normalize の db source route は完了済み
- decision:
  - `veil-lint.py` に `--db` source を追加し、db rule loader を shared helper に置く
- rationale:
  - mainline gate を SQLite canonical route に寄せるため
- rejected alternatives:
  - lint file 内で独自 db query
- impact scope:
  - `veil-lint.py`
  - `veil_rule_store.py`
  - docs/current minimal writeback
- completion conditions:
  - rules-dir/db 両 source で violation/warning/clean が返る
- SSOT declaration when data contracts are involved:
  - current lint output contract in `veil-lint.py`

## 3. Preconditions

| Check | Status | Notes |
|---|---|---|
| scope が承認済み | PASS | current next action と一致 |
| dependency が利用可能 | PASS | Stage 1/2 helpers available |
| 関連 docs が current | PASS | normalize wave writeback 済み |

## 4. Files

| Path | Operation | Purpose |
|---|---|---|
| `workspace/20260607_sqlite_stage2_lint_requirements.md` | create | lint wave requirements |
| `workspace/20260607_sqlite_stage2_lint_basic_design.md` | create | lint wave design |
| `workspace/20260607_sqlite_stage2_lint_implementation_plan.md` | create | lint wave plan |
| `workspace/20260607_sqlite_stage2_lint_task_design.md` | create | lint wave task design |
| `veil_rule_store.py` | modify | db rule loader |
| `veil-lint.py` | modify | add `--db` route |
| `README.md` | modify | lint wave note |
| `docs/veil-design.md` | modify | lint source note |
| `index/project-current-work.md` | modify | next action update |

## 5. Acceptance Mapping

| Acceptance ID | Implementation Point | Verification |
|---|---|---|
| C1 | lint `--db` route | db smoke output |
| C2 | level mapping preserved | required/recommended cases |
| C3 | rules-dir compatibility | rules-dir smoke output |
| C4 | compile pass | `python -m py_compile` |

## 6. Verification Plan

- planned checks:
  - `python -m py_compile veil_rule_store.py veil-lint.py`
  - `python veil-lint.py --text "current state" --rules-dir workspace/veil_stage1_rules_fixture`
  - `python veil-lint.py --text "current state" --db workspace/veil_stage1_smoke.db`
  - `python veil-lint.py --text "summary" --db workspace/veil_stage1_smoke.db`
  - `python veil-lint.py --text "今の状態を整理した" --db workspace/veil_stage1_smoke.db`
- planned tests:
  - violation
  - warning
  - clean
- evidence surface:
  - CLI output
  - execution report

## 7. 作業順序

1. lint wave packet を作る
2. shared db rule loader を追加する
3. lint source selection を実装する
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
  - source option と texts を変えて再検証可能

## 9. Risks

| Risk | Level | Mitigation |
|---|---|---|
| violation/warning mapping drift | high | required/recommended smoke を分けて確認する |
| skip behavior ambiguity | medium | empty db smoke 方針を固定する |
