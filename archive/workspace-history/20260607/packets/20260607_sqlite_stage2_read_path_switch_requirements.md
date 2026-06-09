# Requirements テンプレート準拠

**Project**: VEIL SQLite Stage 2  
**Author**: Codex  
**Date**: 2026-06-07  
**Approver**: owner

## 1. Overview

### 目的

VEIL の SQLite 正本化 Stage 2 として、`audit -> normalize -> lint` の順で read path を Markdown から SQLite へ寄せる計画と、第一波実装を固定する。  
今回この要求で閉じる範囲は、順序を packet に固定し、第一波として `veil-profile-audit.py` を SQLite 読取対応にすることまでとする。

### 背景

- Stage 1 で SQLite schema / import / readback support は追加済み
- current runtime の読取元はまだ `~/.veil/rules/*.md`
- read path switch は mainline へ直接効くため、一括置換せず最小リスク順に切り替える必要がある

### 参考事例 / 参照資料

- `workspace/20260607_sqlite_stage1_schema_import_implementation_plan.md`
- `workspace/20260607_sqlite_stage1_schema_import_execution_report.md`
- `veil-profile-audit.py`
- `veil-normalize.py`
- `veil-lint.py`

### Stakeholders

| Stakeholder | Role | Expected Benefit |
|---|---|---|
| owner | 方針決定者 | mainline を壊さずに SQLite 読取へ移れる |
| delegated AI | 運用実行者 | どの順で切り替えるか迷わず進められる |
| future maintainer | 保守者 | dual source 混乱を段階的に解消できる |

## 2. Scope

### In Scope

- Stage 2 read path switch の順序固定
- 第一波として `veil-profile-audit.py` の SQLite read route
- SQLite / Markdown dual-read or explicit source selection の設計
- smoke verification

### Out of Scope

- `veil-normalize.py` の SQLite read 切替実装
- `veil-lint.py` の SQLite read 切替実装
- `veil-sync.py` の generated Markdown route 実装
- `capture` 書込先の SQLite 切替

### Assumptions and Constraints

- Stage 1 support route は動作済み
- 第一波は support runtime から始める
- source selection は明示引数で切れるようにする
- current home rules を canonical と言い切る docs 全面更新はまだ行わない

### Success Criteria

- 何を満たせば「完了」とみなすか:
  - Stage 2 の順序が `audit -> normalize -> lint` で packet に固定される
- どの状態まで検証できれば次工程へ進めるか:
  - `veil-profile-audit.py` が rules dir だけでなく SQLite DB も読める
- requirement を basic design に渡してよい条件になっているか:
  - source selection、切替順、非破壊性、第一波対象が hidden で残っていない

### Primary User Workflow

1. 利用者:
   - VEIL maintainer
2. 開始条件:
   - Stage 1 support code がある
3. 主な操作:
   - read path switch 順序を確認する
   - audit を SQLite source で実行する
4. 期待結果:
   - 最小リスクの面から SQLite read を始められる

## 3. Functional Requirements

| ID | Requirement | Acceptance Criteria | Priority |
|---|---|---|---|
| FR-1 | Stage 2 は read path switch 順を固定しなければならない | packet に `audit -> normalize -> lint` が読める | must |
| FR-2 | 第一波は `veil-profile-audit.py` を SQLite source 対応にしなければならない | `--db` など明示 source で audit が動く | must |
| FR-3 | 第一波は current rules-dir audit 互換を壊してはならない | 既存 `--rules-dir` 経路が通る | must |
| FR-4 | 第一波は workspace smoke で検証できなければならない | Stage 1 smoke DB を読める | must |

### Edge Cases and Failure Conditions

| Case | Condition | Expected Behavior |
|---|---|---|
| EC-1 | `--db` と `--rules-dir` の両方指定 | 明示的に優先または error とする |
| EC-2 | DB はあるが rows が空 | total 0 として返す |
| EC-3 | DB schema mismatch | non-zero と error |
| EC-4 | rules-dir audit と db audit の summary 形式がずれる | 出力 contract を保つ |

## 4. Non-Functional Requirements

| ID | Category | Requirement | Target |
|---|---|---|---|
| NFR-1 | Safety | first wave は support runtime に留める | mainline lint behavior を変えない |
| NFR-2 | Compatibility | existing CLI usage を壊さない | `--rules-dir` 互換維持 |
| NFR-3 | Maintainability | normalize/lint へ再利用できる source selection pattern にする | source option の型をそろえる |

## 5. Risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| dual source selection が曖昧 | medium | high | `--db` / `--rules-dir` の contract を明示する |
| audit で summary contract が変わる | medium | medium | current text/json shape を基本維持する |
| normalize/lint より先に audit を切り替えて docs が追いつかない | low | medium | support runtime first と明記する |

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
