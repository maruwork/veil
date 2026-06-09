# Requirements テンプレート準拠

**Project**: VEIL SQLite Stage 2 Lint Wave  
**Author**: Codex  
**Date**: 2026-06-07  
**Approver**: owner

## 1. Overview

### 目的

VEIL の SQLite 正本化 Stage 2 の最終波として、`veil-lint.py` を SQLite source 対応にする。  
今回この要求で閉じる範囲は、`必須 / 推奨 / 観察` の検査契約を維持したまま、rules-dir と db の両 source を選べるようにすることまでとする。

### 背景

- Stage 2 第一波で `veil-profile-audit.py` は SQLite source を読めるようになった
- Stage 2 次波で `veil-normalize.py` も SQLite source を読めるようになった
- 最後に mainline gate である `veil-lint.py` を切り替える必要がある
- ここは最終出力を止める面なので、output contract を壊さず慎重に進める必要がある

### 参考事例 / 参照資料

- `workspace/20260607_sqlite_stage2_wave1_audit_execution_report.md`
- `workspace/20260607_sqlite_stage2_wave2_normalize_execution_report.md`
- `veil-lint.py`
- `veil_rule_store.py`

### Stakeholders

| Stakeholder | Role | Expected Benefit |
|---|---|---|
| owner | 方針決定者 | mainline gate まで SQLite read に寄せられる |
| delegated AI | 返答前検査実行者 | source selectable な lint を使える |
| future maintainer | 保守者 | canonical source 切替が mainline gate まで閉じる |

## 2. Scope

### In Scope

- `veil-lint.py` の `--db` source route
- `必須 / 推奨 / 観察` の検査契約維持
- text/json output 互換維持
- workspace smoke

### Out of Scope

- `capture` 書込先 SQLite 化
- `veil-sync.py` generated Markdown route
- home dir の実 canonical 切替宣言

### Assumptions and Constraints

- default source は still `--rules-dir`
- `--db` 指定時だけ SQLite source を読む
- `violations / warnings / clean / skip` の返し方は維持する
- inline code / fenced code 保護はそのまま保つ

### Success Criteria

- 何を満たせば「完了」とみなすか:
  - `veil-lint.py` が db source でも rules-dir source と同じ検査階層で返る
- どの状態まで検証できれば次工程へ進めるか:
  - same rule set で rules-dir/db 両方から `violation`, `warning`, `clean` の smoke を取れる
- requirement を basic design に渡してよい条件になっているか:
  - source selection、level mapping、output contract、skip behavior が hidden で残っていない

### Primary User Workflow

1. 利用者:
   - 最終返答前に lint を通す delegated AI
2. 開始条件:
   - rules-dir または SQLite DB がある
3. 主な操作:
   - prose を `veil-lint.py` に渡す
   - violation / warning / clean を見る
4. 期待結果:
   - SQLite source でも current lint gate と同じ感覚で使える

## 3. Functional Requirements

| ID | Requirement | Acceptance Criteria | Priority |
|---|---|---|---|
| FR-1 | `veil-lint.py` は `--db` source を受けなければならない | db path 指定で lint できる | must |
| FR-2 | `veil-lint.py` は `必須 / 推奨 / 観察` の扱いを維持しなければならない | required は violation, recommended は warning, observe は skip | must |
| FR-3 | `veil-lint.py` は rules-dir 互換を壊してはならない | existing CLI usage が通る | must |
| FR-4 | `veil-lint.py` は JSON payload に source 情報を含めるべきである | source_type/source/db_path/rules_dir が出る | should |

### Edge Cases and Failure Conditions

| Case | Condition | Expected Behavior |
|---|---|---|
| EC-1 | db source に rows がない | skip として返す |
| EC-2 | db source に observe しかない | clean or warning/violation なしで返す |
| EC-3 | source_context が file 名でない | lint 自体は継続する |
| EC-4 | text output が source 切替で崩れる | summary wording を維持する |

## 4. Non-Functional Requirements

| ID | Category | Requirement | Target |
|---|---|---|---|
| NFR-1 | Compatibility | current exit code contract を維持する | violation=1, else 0 |
| NFR-2 | Safety | code mask behavior を変えない | fenced/inline code は lint 対象外 |
| NFR-3 | Maintainability | source selection pattern を audit/normalize と揃える | `--db` optional pattern |

## 5. Risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| violation/warning mapping drift | medium | high | db source smoke で required/recommended を確認する |
| skip behavior drift | medium | medium | empty db smoke を確認する |
| text output wording drift | low | medium | current summary phrase を維持する |

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
