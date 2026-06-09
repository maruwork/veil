# 実装計画テンプレート準拠

**Task**: VEIL-TUNING-001-CAPTURE-REPORT-LIGHTENING  
**Author**: Codex  
**Date**: 2026-06-07  
**Status**: Draft

## 1. Packet Minimum Fields

| Field | Value |
|---|---|
| task_id | `VEIL-TUNING-001-CAPTURE-REPORT-LIGHTENING` |
| goal | capture report を軽量化する |
| owner_role | owner / delegated AI |
| scope_in | skills/docs/current |
| scope_out | runtime changes |
| next_gate | report contract readback 完了 |

## 2. Implementation Decision Record

- background:
  - tuning wave 1, 2 は closed
- decision:
  - wave 3 は report contract の軽量化に絞る
- rationale:
  - 日常運用の読解負荷を下げるため
- completion conditions:
  - 採用行が候補1中心で読める

## 3. Preconditions

| Check | Status | Notes |
|---|---|---|
| tuning wave 1 close | PASS | lint guidance 完了 |
| tuning wave 2 close | PASS | normalize precision 完了 |
| scope narrow | PASS | skills/docs only |

## 4. Files

| Path | Operation | Purpose |
|---|---|---|
| `workspace/20260607_capture_report_lightening_*.md` | create | wave 3 packet |
| `skills/codex/veil-capture/SKILL.md` | modify | report contract update |
| `skills/claude-code/veil-capture.md` | modify | report contract update |
| `README.md` | modify | output example update |
| `docs/veil-design.md` | modify | report wording update |
| `index/project-current-work.md` | modify | wave 3 current writeback |

## 5. Acceptance Mapping

| Acceptance ID | Implementation Point | Verification |
|---|---|---|
| A1 | skill report contract | readback |
| A2 | README output example | readback |
| A3 | design/current wording | readback |

## 6. Verification Plan

- `rg` readback for `補助候補`, `採用:`, `保留:`, `同期:`, `返答前検査:`

## 7. 作業順序

1. packet を作る
2. skill contract を更新する
3. README / design / current を追従させる
4. execution report を残す

