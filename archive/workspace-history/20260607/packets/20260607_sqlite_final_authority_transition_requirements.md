# Requirements テンプレート準拠

**Project**: VEIL SQLite Final Authority Transition  
**Author**: Codex  
**Date**: 2026-06-07  
**Approver**: owner

## 1. Overview

### 目的

VEIL の canonical docs / governance を、SQLite 正本化の current phase に合わせて整理する。  
今回この要求で閉じる範囲は、`SQLite = current canonical route`、`rules-dir = transition mirror / AI-readable surface` という説明へ current authority 面をそろえることまでとする。

### 背景

- Stage 1 で SQLite schema/import/readback support は追加済み
- Stage 2 で `audit / normalize / lint` は `--db` で SQLite source を読める
- ただし `capture / sync` の write/generate route はまだ完全移行していない
- そのため docs をいきなり「完全移行済み」と書くのは不正確で、移行 phase を current authority に正直に反映する必要がある

### 参考事例 / 参照資料

- `index/project-current-work.md`
- `workspace/20260607_sqlite_canonical_migration_requirements.md`
- `workspace/20260607_sqlite_stage2_wave3_lint_execution_report.md`

### Stakeholders

| Stakeholder | Role | Expected Benefit |
|---|---|---|
| owner | 方針決定者 | docs/governance と current implementation のズレを減らせる |
| delegated AI | 読解実行者 | SQLite canonical route と transition mirror の区別を誤らない |
| future maintainer | 保守者 | final migration の残り work を誤認しない |

## 2. Scope

### In Scope

- README / design / AGENTS / governance の authority wording 更新
- SQLite canonical route と rules-dir transition mirror の切り分け
- current next action を final migration 実装へ寄せる

### Out of Scope

- `capture` write path の SQLite 化
- `veil-sync.py` の generated route 実装
- home dir real canonical の強制切替

### Assumptions and Constraints

- SQLite support/read route は存在する
- rules-dir 依存はまだ一部残る
- 説明は「移行完了」ではなく「current phase」に合わせる

### Success Criteria

- 何を満たせば「完了」とみなすか:
  - docs/governance 上で SQLite canonical route と rules-dir mirror の役割が一貫して読める
- どの状態まで検証できれば次工程へ進めるか:
  - root authority docs から `rules-dir only canonical` 表現が消え、current phase wording に揃う
- requirement を basic design に渡してよい条件になっているか:
  - fully migrated と transitional の境界が hidden で残っていない

## 3. Functional Requirements

| ID | Requirement | Acceptance Criteria | Priority |
|---|---|---|---|
| FR-1 | docs は SQLite canonical route を current phase として明示しなければならない | README / docs / AGENTS / index で読める | must |
| FR-2 | docs は rules-dir を transition mirror / AI-readable surface として扱わなければならない | rules-dir only canonical wording を外す | must |
| FR-3 | docs は capture/sync 未移行を隠してはならない | transitional wording がある | must |

## 4. Non-Functional Requirements

| ID | Category | Requirement | Target |
|---|---|---|---|
| NFR-1 | Honesty | current implementation を誇張しない | fully migrated と書かない |
| NFR-2 | Governance | authority wording を current work と揃える | AGENTS / index / docs alignment |

## 5. Risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| docs が先走って完了済みと読める | medium | high | transition wording を入れる |
| transitional wording が増えすぎて読みにくい | medium | medium | root authority 面だけに絞る |

## 6. Requirement Quality Check

- [x] 完了報告の主語が固定されている
- [x] In Scope / Out of Scope が衝突していない
- [x] Success Criteria が次工程へ進める条件として書かれている
- [x] Acceptance Criteria が requirement ごとに確認可能
