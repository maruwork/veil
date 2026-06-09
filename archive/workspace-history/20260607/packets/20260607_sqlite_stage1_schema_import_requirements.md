# Requirements テンプレート準拠

**Project**: VEIL SQLite Stage 1  
**Author**: Codex  
**Date**: 2026-06-07  
**Approver**: owner

## 1. Overview

### 目的

VEIL の SQLite 正本化 Stage 1 として、`schema 作成`、`Markdown -> SQLite import`、`smoke readback` を current runtime を壊さずに追加する。  
今回この要求で閉じる範囲は、support code と smoke evidence を追加し、Stage 2 へ渡せる SQLite 初期導入面を作ることまでとする。

### 背景

- mainline plan では `Stage 1 = schema 追加 / import route / smoke readback`
- current runtime はまだ `~/.veil/rules/*.md` を正本として使っている
- そのため Stage 1 では read path を切り替えず、SQLite を support canonical candidate として導入する

### 参考事例 / 参照資料

- 参照仕様:
  - `workspace/20260607_sqlite_canonical_migration_requirements.md`
  - `workspace/20260607_sqlite_canonical_migration_basic_design.md`
  - `workspace/20260607_sqlite_canonical_migration_implementation_plan.md`
  - `workspace/20260607_sqlite_canonical_migration_task_design.md`
- 関連 runtime:
  - `veil-lint.py`
  - `veil-normalize.py`
  - `veil-profile-audit.py`

### Stakeholders

| Stakeholder | Role | Expected Benefit |
|---|---|---|
| owner | 方針決定者 | SQLite 正本化の実装入口ができる |
| delegated AI | 次段実装者 | Markdown parse を再利用できる import route を持てる |
| future maintainer | 運用保守者 | DB 初期化と readback が明示される |

## 2. Scope

### In Scope

- SQLite schema を作る support code
- `rules/*.md` を SQLite に取り込む import support
- imported rows の smoke readback
- Stage 1 実装 packet と evidence

### Out of Scope

- `veil-lint.py` の SQLite read 切替
- `veil-normalize.py` の SQLite read 切替
- `veil-sync.py` の generated Markdown route 実装
- docs authority の全面更新

### Assumptions and Constraints

- SQLite path は repo 内 smoke と `~/.veil/veil.db` 想定の両方を扱えるようにする
- current Markdown runtime は壊さない
- home dir への実 write は approval boundary を意識し、smoke は workspace path で完結できるようにする
- 追加依存は入れず Python stdlib のみ使う

### Success Criteria

- 何を満たせば「完了」とみなすか:
  - schema/init/import/readback support code が repo に追加され、smoke で rows を読み返せる
- どの状態まで検証できれば次工程へ進めるか:
  - workspace rules fixture から SQLite を生成し、件数と level を readback できる
- requirement を basic design に渡してよい条件になっているか:
  - schema path、import source、smoke evidence、非破壊性が hidden で残っていない

### Primary User Workflow

1. 利用者:
   - VEIL maintainer
2. 開始条件:
   - Markdown rules fixture または既存 rules dir がある
3. 主な操作:
   - DB を初期化する
   - Markdown rules を import する
   - readback で rows を確認する
4. 期待結果:
   - SQLite に取り込まれた rule rows を確認でき、Stage 2 へ進める

## 3. Functional Requirements

| ID | Requirement | Acceptance Criteria | Priority |
|---|---|---|---|
| FR-1 | Stage 1 は SQLite schema を初期化できなければならない | CLI から DB file を作成できる | must |
| FR-2 | Stage 1 は section-aware Markdown rules を import できなければならない | `必須 / 推奨 / 観察` が rows に入る | must |
| FR-3 | Stage 1 は imported rows を readback できなければならない | text または JSON で count と row を返せる | must |
| FR-4 | Stage 1 は current runtime を壊してはならない | existing lint/normalize/audit code path を変更しない | must |

### Edge Cases and Failure Conditions

| Case | Condition | Expected Behavior |
|---|---|---|
| EC-1 | rules dir が存在しない | import は skip or explicit error を返す |
| EC-2 | malformed rule line がある | import はその line を無視または warning し、crash しない |
| EC-3 | same normalized key conflict がある | readback 可能な形で conflict を返す |
| EC-4 | DB file path が書けない | non-zero exit と error message を返す |

## 4. Non-Functional Requirements

| ID | Category | Requirement | Target |
|---|---|---|---|
| NFR-1 | Safety | first-run side effect を限定する | Stage 1 は support script のみ追加 |
| NFR-2 | Maintainability | shared module で schema/import/readback を再利用可能にする | Stage 2 で lint/normalize が再利用可能 |
| NFR-3 | Reliability | workspace-only smoke ができる | home dir write なしでも検証できる |

## 5. Risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| schema を広げすぎる | medium | medium | minimum fields に絞る |
| import と current parser がずれる | medium | high | shared parser helper を切る |
| home dir write が blocker になる | medium | medium | workspace DB smoke を primary evidence にする |

## 6. Requirement Quality Check

- [x] 完了報告の主語が固定されている
- [x] In Scope / Out of Scope が衝突していない
- [x] Success Criteria が次工程へ進める条件として書かれている
- [x] Primary User Workflow の開始条件と期待結果が明示されている
- [x] Acceptance Criteria が requirement ごとに確認可能
- [x] 非機能要件に target が入っている
- [x] major edge case が拾えている
- [x] 前提・制約・完了条件が明示されている
- [x] unresolved な論点が hidden で残っていない
