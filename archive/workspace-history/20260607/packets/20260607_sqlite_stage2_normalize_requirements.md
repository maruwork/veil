# Requirements テンプレート準拠

**Project**: VEIL SQLite Stage 2 Normalize Wave  
**Author**: Codex  
**Date**: 2026-06-07  
**Approver**: owner

## 1. Overview

### 目的

VEIL の SQLite 正本化 Stage 2 次波として、`veil-normalize.py` を SQLite source 対応にする。  
今回この要求で閉じる範囲は、source selection を packet に固定し、existing-match contract を維持したまま `--db` 読取を追加することまでとする。

### 背景

- Stage 2 第一波で `veil-profile-audit.py` は SQLite source を読めるようになった
- 次は capture の直後に使う `veil-normalize.py` を寄せるのが順序として自然
- `veil-lint.py` は mainline gate なので、その前に normalize の source 契約を固める

### 参考事例 / 参照資料

- `workspace/20260607_sqlite_stage2_read_path_switch_implementation_plan.md`
- `workspace/20260607_sqlite_stage2_wave1_audit_execution_report.md`
- `veil-normalize.py`
- `veil_rule_store.py`

### Stakeholders

| Stakeholder | Role | Expected Benefit |
|---|---|---|
| owner | 方針決定者 | lint 前に normalize source を安全に切り替えられる |
| delegated AI | capture 実行者 | rules-dir / db の両 source で統合候補を出せる |
| future maintainer | 保守者 | dual source の既存契約を崩さず移行できる |

## 2. Scope

### In Scope

- `veil-normalize.py` の `--db` source route
- existing-match / new-candidate の返却契約維持
- workspace smoke
- current docs/current writeback

### Out of Scope

- `veil-lint.py` の SQLite read 切替
- `veil-sync.py` generated route
- `capture` 書込先切替

### Assumptions and Constraints

- default source は still `--rules-dir`
- `--db` 指定時だけ SQLite を読む
- `existing-match` payload の主要 field は維持する
- rule conflict reporting は SQLite source では empty でもよい

### Success Criteria

- 何を満たせば「完了」とみなすか:
  - `veil-normalize.py` が rules-dir と db の両 source を読める
- どの状態まで検証できれば次工程へ進めるか:
  - same fixture / same DB で normalized cluster と existing-match を返せる
- requirement を basic design に渡してよい条件になっているか:
  - source selection、existing-match field、conflict 扱いが hidden で残っていない

### Primary User Workflow

1. 利用者:
   - `veil-capture` 後に normalize する delegated AI
2. 開始条件:
   - rules-dir または Stage 1/2 の DB がある
3. 主な操作:
   - 候補語を `veil-normalize.py` に渡す
   - existing-match や level 提案を見る
4. 期待結果:
   - SQLite source でも current normalize output に近い結果が得られる

## 3. Functional Requirements

| ID | Requirement | Acceptance Criteria | Priority |
|---|---|---|---|
| FR-1 | `veil-normalize.py` は `--db` source を受けなければならない | db path 指定で existing rules を読める | must |
| FR-2 | `veil-normalize.py` は existing-match contract を維持しなければならない | `existing_original`, `preferred`, `level`, `source_file` が返る | must |
| FR-3 | `veil-normalize.py` は rules-dir 互換を壊してはならない | current CLI usage が通る | must |
| FR-4 | `veil-normalize.py` は source 情報を結果で判別できなければならない | JSON payload に source info が入る | should |

### Edge Cases and Failure Conditions

| Case | Condition | Expected Behavior |
|---|---|---|
| EC-1 | db source に rows がない | new-candidate として処理できる |
| EC-2 | db source の `source_context` が file 名でない | `source_file` は source_context 由来の保守的値で返す |
| EC-3 | rules-dir と db source で同じ candidate の結果がずれる | fixture smoke で差を確認する |

## 4. Non-Functional Requirements

| ID | Category | Requirement | Target |
|---|---|---|---|
| NFR-1 | Compatibility | current text output の見え方を大きく崩さない | `参照ルール:` と existing-match 行を維持 |
| NFR-2 | Safety | lint behavior には触れない | `veil-lint.py` unchanged |
| NFR-3 | Maintainability | source selection pattern を audit とそろえる | `--db` optional pattern |

## 5. Risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| existing-match field drift | medium | high | fixture で key readback を確認する |
| db source で conflict reporting が曖昧 | low | medium | Stage 2 wave では empty conflicts を許容する |
| source info が text output で不明瞭 | medium | low | source label を text output に含める |

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
