# 実装計画テンプレート準拠

**Task**: VEIL-TUNING-001-LINT-FIX-GUIDANCE  
**Author**: Codex  
**Date**: 2026-06-07  
**Status**: Draft

## 1. Packet Minimum Fields

| Field | Value |
|---|---|
| task_id | `VEIL-TUNING-001-LINT-FIX-GUIDANCE` |
| goal | lint を直しやすい report へ改善する |
| owner_role | owner / delegated AI |
| scope_in | lint runtime, docs/current |
| scope_out | normalize/capture/profile tuning |
| next_gate | lint guidance smoke 完了 |

## 2. Implementation Decision Record

- background:
  - canonical migration は閉じた
  - 次 bundle は precision / usability tuning
- decision:
  - wave 1 は lint fix guidance に絞る
- rationale:
  - 返答前 gate の使い勝手改善が最短で効くため
- completion conditions:
  - violation / warning 出力で修正先がすぐ分かる

## 3. Preconditions

| Check | Status | Notes |
|---|---|---|
| SQLite canonical migration close | PASS | Stage 3 まで完了 |
| lint runtime available | PASS | current route stable |
| scope narrow | PASS | lint only |

## 4. Files

| Path | Operation | Purpose |
|---|---|---|
| `workspace/20260607_lint_fix_guidance_*.md` | create | tuning packet |
| `veil-lint.py` | modify | fix guidance 実装 |
| `README.md` | modify | lint usability update |
| `docs/veil-design.md` | modify | lint output contract update |
| `index/project-current-work.md` | modify | new bundle writeback |

## 5. Acceptance Mapping

| Acceptance ID | Implementation Point | Verification |
|---|---|---|
| A1 | lint item guidance fields | json smoke |
| A2 | text guidance output | text smoke |
| A3 | hit-level preview fields | json smoke |
| A4 | existing status contract | clean/warning/violation smoke |

## 6. Verification Plan

- `python -m py_compile veil-lint.py`
- rules-dir or db fixture で violation / warning / clean smoke
- json readback

## 7. 作業順序

1. packet を作る
2. `veil-lint.py` に guidance を追加する
3. docs/current を追従させる
4. smoke と execution report を残す

## 8. Idempotency and Side Effects

- runtime report change only
- no schema change

## 9. Risks

| Risk | Level | Mitigation |
|---|---|---|
| preview が誤解を招く | medium | preview は first-hit line only と明記する |

