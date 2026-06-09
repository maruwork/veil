# 実装計画テンプレート準拠

**Task**: VEIL-CANONICAL-003-STAGE3-CAPTURE-SYNC  
**Author**: Codex  
**Date**: 2026-06-07  
**Status**: Draft

## 1. Packet Minimum Fields

| Field | Value |
|---|---|
| task_id | `VEIL-CANONICAL-003-STAGE3-CAPTURE-SYNC` |
| goal | capture/sync の write-generate route を SQLite canonical 前提へ切り替える |
| owner_role | owner / delegated AI |
| scope_in | runtime helper, support CLI, sync route, docs, skills |
| scope_out | UI, domain profile, schema redesign |
| next_gate | stage 3 smoke 完了 |

## 2. Implementation Decision Record

- background:
  - Stage 1 で schema/import/readback を実装した
  - Stage 2 で audit/normalize/lint の read path を DB 対応した
  - authority docs は SQLite canonical wording へ遷移済み
- decision:
  - Stage 3 では capture/sync の write-generate route を DB canonical へ寄せる
- rationale:
  - write route まで切り替わって初めて canonical migration が閉じるため
- completion conditions:
  - file 直書き前提が mainline surface から消える

## 3. Preconditions

| Check | Status | Notes |
|---|---|---|
| Stage 2 完了 | PASS | read route switch 実装済み |
| authority wording 更新済み | PASS | final authority transition 完了 |
| support CLI 利用可能 | PASS | `veil-db.py` 既存 route あり |

## 4. Files

| Path | Operation | Purpose |
|---|---|---|
| `workspace/20260607_sqlite_stage3_capture_sync_*.md` | create | stage 3 packet |
| `veil_rule_store.py` | modify | upsert/export helper |
| `veil-db.py` | modify | upsert/export CLI |
| `veil-sync.py` | modify | DB-first mirror generate sync |
| `README.md` | modify | current route update |
| `docs/veil-design.md` | modify | stage 3 write route update |
| `skills/codex/veil-capture/SKILL.md` | modify | DB write route update |
| `skills/claude-code/veil-capture.md` | modify | DB write route update |
| `index/project-current-work.md` | modify | next action writeback |
| `workspace/veil_stage3_capture_sync_smoke.py` | create | smoke |

## 5. Acceptance Mapping

| Acceptance ID | Implementation Point | Verification |
|---|---|---|
| A1 | `veil-db.py upsert-rule` | smoke |
| A2 | `veil-db.py export-mirror` | smoke |
| A3 | `veil-sync.py` DB-first route | smoke |
| A4 | docs/skills/current work | readback |
| A5 | workspace smoke script | execution report |

## 6. Verification Plan

- `python -m py_compile veil_rule_store.py veil-db.py veil-sync.py`
- `python workspace/veil_stage3_capture_sync_smoke.py`
- readback grep for `upsert-rule`, `export-mirror`, `DB canonical`, `mirror`

## 7. 作業順序

1. packet を作る
2. helper / CLI を実装する
3. `veil-sync.py` を DB-first へ切り替える
4. docs / skills / current work を追従させる
5. smoke と execution report を残す

## 8. Idempotency and Side Effects

- Idempotency type:
  - helper / docs update は idempotent
  - smoke は workspace 配下の一時物だけを書く

## 9. Risks

| Risk | Level | Mitigation |
|---|---|---|
| mirror 生成順の崩れ | medium | deterministic sort を固定する |
| sync 互換性の崩れ | medium | rules-dir fallback を維持する |

