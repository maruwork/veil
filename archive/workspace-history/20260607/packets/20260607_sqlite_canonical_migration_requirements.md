# Requirements テンプレート準拠

**Project**: VEIL  
**Author**: Codex  
**Date**: 2026-06-07  
**Approver**: owner

## 1. Overview

### 目的

VEIL の語彙正本を `~/.veil/rules/*.md` から SQLite 正本へ切り替える計画を固定する。  
今回この要求で閉じる範囲は、`SQLite を正本、Markdown を生成物とする方針`、`段階移行の道のり`、`Stage 1 へ着手できる task-design 粒度` を current packet にそろえることまでとする。

### 背景

- current 実装は `~/.veil/rules/*.md` を正本としている
- section-aware 化と `必須 / 推奨 / 観察` への整理は完了した
- ただし Markdown 正本では、queue、見直し候補、統計、lint 補助、将来の query 中心運用に弱い
- user 判断として、domain profile 分岐よりも current tool の精度と使い勝手向上を優先する
- そのため、まず保存形式の正本を機械向きに変える必要がある

### 参考事例 / 参照資料

- 類似事例:
  - `workspace/20260607_required_rule_tuning_execution_report.md`
- 参照仕様:
  - `common/frameworks/project-progression-rule.md`
  - `common/frameworks/goal-path-checkpoint-task-design-framework.md`
  - `common/policies/execution-readiness-gate-policy.md`
- 関連 ADR / decision:
  - `workspace/20260607_sqlite_canonical_migration_decision_note.md`

### Stakeholders

| Stakeholder | Role | Expected Benefit |
|---|---|---|
| owner | 方針決定者 | Markdown 正本依存をやめ、今後の改善をしやすくする |
| delegated AI | `capture / normalize / lint / sync` 実行者 | file browse ではなく query / generated surface で運用できる |
| future maintainer | 運用保守者 | level 管理、統計、見直し候補抽出を構造化データで扱える |

## 2. Scope

### In Scope

- SQLite 正本化の completion 主語を固定する
- SQLite 正本と Markdown 生成物の責務境界を固定する
- `capture / normalize / lint / sync / audit` の読取・生成経路を段階移行で定義する
- Stage 1 着手に必要な checkpoint / task / task-design を固定する
- branch-first / domain-first 計画を superseded と明記する

### Out of Scope

- この packet だけで SQLite 実装を完了させること
- 直ちに `~/.veil/rules/` を削除すること
- UI / helper DB 系を mainline へ戻すこと
- 分野別 profile を増やすこと

### Assumptions and Constraints

- current runtime はまだ Markdown 正本前提で動いている
- `~/.veil/rules/` は当面 generated mirror または移行元として残る
- top-level shelf は増やさない
- user 指示により PowerShell は使わない
- mainline を壊す一括置換ではなく staged migration にする

### Success Criteria

- 何を満たせば「完了」とみなすか:
  - SQLite 正本化の要求が `requirements / basic design / implementation plan / task design / current work` で一貫して読める
- どの状態まで検証できれば次工程へ進めるか:
  - Stage 1 の schema / import / smoke readback を着手できる粒度まで task-design が固定される
- requirement を basic design に渡してよい条件になっているか:
  - `正本 = SQLite`、`生成物 = Markdown`、`tool routing`、`段階移行`、`停止条件` が hidden で残っていない

### Primary User Workflow

1. 利用者:
   - VEIL を整備する owner / delegated AI
2. 開始条件:
   - current rules は `~/.veil/rules/*.md` に存在し、mainline は still alive
3. 主な操作:
   - SQLite 正本化の方針を読む
   - Stage 別の切替順を確認する
   - Stage 1 task-design を使って実装着手する
4. 期待結果:
   - VEIL の正本切替が branch / UI / helper DB にぶれず、SQLite 正本移行として進められる

## 3. Functional Requirements

### Requirement Structuring Notes

- 主語は `VEIL の語彙正本を SQLite に切り替える計画` に固定する
- plan packet 自体に Stage 4 以降の実装完了を混ぜない
- branch-first や UI 復帰など別 capability を混ぜない

| ID | Requirement | Acceptance Criteria | Priority |
|---|---|---|---|
| FR-1 | packet は `正本 = SQLite`、`生成物 = Markdown` を明示しなければならない | requirements / basic design / implementation plan で同じ表現が読める | must |
| FR-2 | packet は mainline tool の routing を段階移行として示さなければならない | `capture / normalize / lint / sync / audit` の各役割が stage ごとに読める | must |
| FR-3 | packet は Stage 1 実装の入口を task-design 粒度まで固定しなければならない | schema、import、smoke readback の task が 20 項目設計で読める | must |
| FR-4 | packet は superseded 方向を明示しなければならない | branch-first / Markdown 長期正本維持が current 主題でないと読める | should |
| FR-5 | packet は mainline を壊さない停止条件を明示しなければならない | 一括切替禁止、generated route 不明時停止、write boundary 停止が書かれている | must |

### Edge Cases and Failure Conditions

| Case | Condition | Expected Behavior |
|---|---|---|
| EC-1 | SQLite schema は決まったが generated Markdown route が曖昧 | Stage 1 以降へ進めず停止する |
| EC-2 | tool routing が tool ごとに別主語になる | split するか packet を差し戻す |
| EC-3 | Markdown 正本と SQLite 正本の二重 authority が残る | `current authority ambiguity` として停止する |
| EC-4 | branch/profile 拡張へ話が戻る | current bundle 外として停止する |

## 4. Non-Functional Requirements

| ID | Category | Requirement | Target |
|---|---|---|---|
| NFR-1 | Reliability | staged migration で rollback / coexistence を確保する | Stage 1-2 は current Markdown route を併存させる |
| NFR-2 | Maintainability | query 中心の改善余地を残す schema にする | level / status / preferred alternatives / timestamps を保持できる |
| NFR-3 | Governance | `common` の gate を満たす packet にする | goal/path/checkpoint/task/design が traceable |
| NFR-4 | Safety | current mainline を即破壊しない | 本番 rules 削除は今回 scope 外 |

## 5. Risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| SQLite schema を広げすぎる | medium | medium | Stage 1 は minimum viable canonical schema に限定する |
| Markdown generated route が後回しで曖昧になる | medium | high | basic design と task-design に明示し、曖昧なら停止する |
| tool 切替順が逆転し mainline を壊す | medium | high | Stage 順序を固定し、一括切替を禁止する |
| current docs と current work の不整合 | medium | medium | current companion への writeback を task に含める |

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

## 7. Glossary

| Term | Definition |
|---|---|
| SQLite 正本 | VEIL の語彙 rule の source of truth として扱う SQLite DB |
| Markdown 生成物 | AI に読ませるために SQLite から生成する `~/.veil/rules/*.md` |
| Stage 1 | schema 追加、Markdown import、smoke readback までの初回導入段 |
