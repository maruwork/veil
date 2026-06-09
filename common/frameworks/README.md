# 共通フレームワーク

判断、分析、設計、実装分割に使う共通の考え方を置く。

本文は日本語正本とする。traceability、task、requirement など、既存開発文脈で固定された語は必要に応じて英語のまま使ってよい。

## Project Progression Rule

[project-progression-rule.md](./project-progression-rule.md) は、
AI がプロジェクトをどう読み、どう進め、どう止まり、どう戻るかの最上位ルールを定義する。

これは `pj-template` の中核正本であり、

- 完了骨格
- 進行ルール
- 認識・補正規律

を 1 本でつなぐ。

## Workflow Spine

[business-workflow-spine.md](./business-workflow-spine.md) は、
domain が変わっても維持される共通の業務骨格を定義する。

- `設計`
- `事前確認`
- `実行`
- `事後確認`

## Five-Layer Work Design

[goal-path-checkpoint-task-design-framework.md](./goal-path-checkpoint-task-design-framework.md) は、
`ゴール`、`道のり`、`チェックポイント`、`タスク`、`設計`
の 5 層を、プロジェクト非依存の上位分解として定義する。

これは作業前に何を固定するかの共通骨格であり、
詳細な着手前確認、作業設計、停止条件は
`../policies/execution-readiness-gate-policy.md`
を正に読む。

## 他案件で最初に読む順

1. まず [project-progression-rule.md](./project-progression-rule.md) を読む
2. 次に [project-progression-rule-integration-audit.md](./project-progression-rule-integration-audit.md) を読む
   - 接続図・読む順・棚ごとの役割整理を確認する
3. その後 [goal-path-checkpoint-task-design-framework.md](./goal-path-checkpoint-task-design-framework.md) を読む
4. 業務ワークフロー全体の骨格も必要なら [business-workflow-spine.md](./business-workflow-spine.md) を読む
5. 詳細な確認項目は `../policies/README.md` から読む

この棚の他の文書は、必要になった時に追加で読む。
最初の入口に戻る時は `../README.md` を開く。

## 本体として前に出す文書

- 最上位進行ルール
  - [project-progression-rule.md](./project-progression-rule.md)
- 最上位進行ルールの統合監査表
  - [project-progression-rule-integration-audit.md](./project-progression-rule-integration-audit.md)
- 上位分解
  - [goal-path-checkpoint-task-design-framework.md](./goal-path-checkpoint-task-design-framework.md)
- 業務骨格と状態整理
  - [business-workflow-spine.md](./business-workflow-spine.md)
  - [ps-suite-guide.md](./ps-suite-guide.md)
- 振り返りと整合
  - [decision-to-implementation-consistency-review.md](./decision-to-implementation-consistency-review.md)
  - [framework-selection-guide.md](./framework-selection-guide.md)
  - [prompt-quality-improvement-cycle.md](./prompt-quality-improvement-cycle.md)

入口では上の本体だけを見せ、残りは必要時だけ開く。

## 保管資産として残す文書

- 発見、分類、質問設計、PS 系の詳細 guide は、必要時だけ開く
- 入口では全件列挙しない
- 統合や examples送りを後続で判断する
- 詳細な統合元一覧は入口 README に抱え込まず、必要時だけ本文・履歴・監査記録で辿る
- 波ごとの監査履歴や時点判断は `../../refernce/` 側の reference 記録で辿る
