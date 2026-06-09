# 実装計画テンプレート準拠

**Task**: VEIL-CANONICAL-003  
**Author**: Codex  
**Date**: 2026-06-07  
**Status**: Draft

## 1. Packet Minimum Fields

| Field | Value |
|---|---|
| task_id | `VEIL-CANONICAL-003` |
| goal | VEIL の語彙正本を SQLite 正本へ移すための current packet と Stage 1 着手入口を固定する |
| owner_role | owner / delegated AI |
| scope_in | SQLite canonical decision、tool routing、stage sequence、Stage 1 task-design |
| scope_out | branch-first expansion、UI 復帰、即時 full implementation |
| next_gate | Stage 1 schema/import task packet 承認 |

## 2. Implementation Decision Record

- background:
  - current mainline は Markdown 正本で整っているが、今後の queue / tuning / lint support 強化に向かない
- decision:
  - SQLite を canonical、Markdown を generated artifact とする packet に切り替える
- rationale:
  - machine-readable canonical と AI-readable text surface を分けるため
- rejected alternatives:
  - Markdown 正本継続
  - JSON 単独正本
  - branch-first の domain profile 拡張を次主題にすること
- impact scope:
  - `workspace/` packet 群
  - `index/project-current-work.md`
- completion conditions:
  - goal / path / checkpoint / task / design が packet 上で一貫し、Stage 1 着手条件が読める
- SSOT declaration when data contracts are involved:
  - current plan SSOT は SQLite canonical migration packet 群

## 3. Preconditions

| Check | Status | Notes |
|---|---|---|
| scope が承認済み | PASS | user が SQLite canonical へ切替指示済み |
| dependency が利用可能 | PASS | `common/` framework と current packet が読める |
| 関連 docs が current | PASS | `index/project-current-work.md` は current bundle を保持 |

## 4. Files

| Path | Operation | Purpose |
|---|---|---|
| `workspace/20260607_sqlite_canonical_migration_requirements.md` | modify | requirement を template 準拠へ補強 |
| `workspace/20260607_sqlite_canonical_migration_basic_design.md` | modify | architecture / option / data / interface を固定 |
| `workspace/20260607_sqlite_canonical_migration_implementation_plan.md` | modify | goal-path-checkpoint-task を実装順へ結ぶ |
| `workspace/20260607_sqlite_canonical_migration_task_design.md` | modify | gate 20 項目を満たす task spec にする |
| `index/project-current-work.md` | modify | current position と next gate を packet に一致させる |

## 5. Acceptance Mapping

| Acceptance ID | Implementation Point | Verification |
|---|---|---|
| C1 | requirements に success subject / scope / workflow を固定 | doc readback で hidden scope がない |
| C2 | basic design に canonical/generated split と option comparison を固定 | `SQLite` / `generated artifact` / `tool routing` が読める |
| C3 | implementation plan に checkpoint と依存順を固定 | CP1-CP4 と対応 task が読める |
| C4 | task design に 20 項目 task spec を入れる | 各 task で required fields が埋まる |
| C5 | current work が new route を指す | `next action` と `next gate` が SQLite Stage 1 を指す |

## 6. Verification Plan

- planned checks:
  - packet readback
  - `common` required fields 照合
  - `current work` 整合確認
- planned tests:
  - text-level consistency check only
- evidence surface:
  - updated packet files
  - final response summary

## 7. 作業順序

1. goal を requirements に固定する
2. path と architecture を basic design に固定する
3. checkpoint と task 順を implementation plan に固定する
4. 各 task を execution-readiness-gate の 20 項目で task design 化する
5. current work へ next gate を書き戻す

### Checkpoints

| Checkpoint | 目的 | 通過前に必要なもの | 通過後に成立するもの |
|---|---|---|---|
| CP-1 | success subject 固定 | SQLite canonical decision note | branch-first ではなく SQLite canonical migration が current 主題だと読める |
| CP-2 | canonical/generated boundary 固定 | requirements 整理 | SQLite と Markdown の役割混同が消える |
| CP-3 | stage 順固定 | basic design | Stage 1-4 の順でしか切替しないと読める |
| CP-4 | Stage 1 着手入口固定 | implementation plan / task design | schema/import/smoke readback を実装着手できる |

## 8. Idempotency and Side Effects

- Idempotency type:
  - idempotent
- Writes:
  - `workspace/` packet files
  - `index/project-current-work.md`
- External calls:
  - なし
- Retry behavior:
  - packet readback に基づいて再編集可能

## 9. Risks

| Risk | Level | Mitigation |
|---|---|---|
| task design が Stage 1 未満の粗さで止まる | high | 20 項目を明示して埋める |
| docs だけ先に SQLite canonical と言い切って runtime と衝突する | medium | current runtime は未移行であることを明記する |
| current work が branch-first の残骸を持つ | medium | writeback で next action / next gate を更新する |
