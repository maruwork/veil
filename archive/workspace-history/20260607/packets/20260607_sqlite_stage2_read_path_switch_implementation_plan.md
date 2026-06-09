# 実装計画テンプレート準拠

**Task**: VEIL-CANONICAL-003-STAGE2-WAVE1  
**Author**: Codex  
**Date**: 2026-06-07  
**Status**: Draft

## 1. Packet Minimum Fields

| Field | Value |
|---|---|
| task_id | `VEIL-CANONICAL-003-STAGE2-WAVE1` |
| goal | Stage 2 read path switch の順序を固定し、audit の SQLite read を実装する |
| owner_role | owner / delegated AI |
| scope_in | Stage 2 packet, `veil-profile-audit.py`, smoke verification |
| scope_out | normalize/lint switch |
| next_gate | Stage 2 normalize packet |

## 2. Implementation Decision Record

- background:
  - Stage 1 で SQLite support route は追加済み
- decision:
  - `veil-profile-audit.py` に `--db` source を追加する
- rationale:
  - support runtime から安全に切替を始めるため
- rejected alternatives:
  - lint first
  - all-at-once switch
- impact scope:
  - Stage 2 packet files
  - `veil-profile-audit.py`
  - docs/current minimal writeback
- completion conditions:
  - `veil-profile-audit.py` が rules-dir と db の両 source を読める
- SSOT declaration when data contracts are involved:
  - Stage 1 `veil_rule_store.py` readback contract

## 3. Preconditions

| Check | Status | Notes |
|---|---|---|
| scope が承認済み | PASS | current next action と一致 |
| dependency が利用可能 | PASS | `veil_rule_store.py` がある |
| 関連 docs が current | PASS | Stage 1 current writeback 済み |

## 4. Files

| Path | Operation | Purpose |
|---|---|---|
| `workspace/20260607_sqlite_stage2_read_path_switch_requirements.md` | create | Stage 2 requirements |
| `workspace/20260607_sqlite_stage2_read_path_switch_basic_design.md` | create | Stage 2 architecture/order |
| `workspace/20260607_sqlite_stage2_read_path_switch_implementation_plan.md` | create | Stage 2 wave1 plan |
| `workspace/20260607_sqlite_stage2_read_path_switch_task_design.md` | create | Stage 2 wave1 task design |
| `veil-profile-audit.py` | modify | add `--db` source route |
| `README.md` | modify | Stage 2 first wave support note |
| `docs/veil-design.md` | modify | audit source selection note |
| `index/project-current-work.md` | modify | current next action update |

## 5. Acceptance Mapping

| Acceptance ID | Implementation Point | Verification |
|---|---|---|
| C1 | Stage 2 order packet | packet readback |
| C2 | audit `--db` route | db smoke output |
| C3 | audit rules-dir compatibility | existing rules-dir smoke output |
| C4 | py_compile pass | `python -m py_compile` |

## 6. Verification Plan

- planned checks:
  - `python -m py_compile veil-profile-audit.py veil_rule_store.py`
  - `python veil-profile-audit.py --db workspace/veil_stage1_smoke.db`
  - `python veil-profile-audit.py --rules-dir workspace/veil_stage1_rules_fixture`
- planned tests:
  - text output
  - json output
- evidence surface:
  - CLI output
  - execution report

## 7. 作業順序

1. Stage 2 packet を作る
2. `veil-profile-audit.py` に source selection を入れる
3. db/rules-dir 両方で smoke する
4. docs/current を最小反映する

## 8. Idempotency and Side Effects

- Idempotency type:
  - idempotent
- Writes:
  - repo files
- External calls:
  - なし
- Retry behavior:
  - source option を切り替えて再検証可能

## 9. Risks

| Risk | Level | Mitigation |
|---|---|---|
| audit output contract を壊す | medium | summary field 名を維持する |
| source selection ambiguity | medium | explicit error or clear precedence を入れる |
