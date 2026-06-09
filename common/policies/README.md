# 共通ポリシー

プロジェクト横断で再利用できる運用ルールを置く。

ここにある文書は `project-progression-rule.md` の下にある共通の具体化文書である。

強さ関係は次のとおり。

1. `project-progression-rule.md`
2. `policies/` の各共通ルール
3. project 固有ルール

project 固有ルールは、この棚の共通ルールを具体化してよいが、上位ルールに反してはならない。

本文は日本語正本とする。ただし、ファイル名、status、分類コード、schema key、CLI option など機械処理に関係する語は英語を維持する。

## 入口で戻る文書

この棚は `project-progression-rule.md` の下にある具体化棚として扱う。
最初に進行全体を読む時は、
[../frameworks/project-progression-rule.md](../frameworks/project-progression-rule.md)
と
[../frameworks/project-progression-rule-integration-audit.md](../frameworks/project-progression-rule-integration-audit.md)
を先に読む。

### 最優先の着手前 gate

次の 1 本は補助資料ではなく、着手前の最優先 gate として扱う。

- [execution-readiness-gate-policy.md](./execution-readiness-gate-policy.md)

`ready to proceed`、`ready to execute`、`ready to handoff`、`planning/spec complete` を主張する前に、必ずこの確認を通す。

5 層の上位説明は policy 棚ではなく、
[../frameworks/goal-path-checkpoint-task-design-framework.md](../frameworks/goal-path-checkpoint-task-design-framework.md)
を先に読む。

## 他案件で使う時の基本

- 5 層の本文は framework 側をそのまま使う
- この棚では、着手前確認と作業設計の必須項目を読む
- template 側で吸収する分岐条件は、project 固有 rule に落とす前に確認する
- project 固有の path、今の状態を見るファイル名、確認 command 名は project ごとに差し替える
- ルールの意味を保ったまま、その project の file 名や command 名へ置き換える
- 最初の入口に戻る時は `../README.md` を開く

この棚は、`project 固有ルールを増やす棚` ではない。
ここで増やすのは、上位 rule を project に落とすための共通具体化だけである。

## 本体として前に出す文書

- 実行と停止
  - [execution-readiness-gate-policy.md](./execution-readiness-gate-policy.md)
  - [verification-and-retry-policy.md](./verification-and-retry-policy.md)
- 入口と読み分け
  - [entry-guide-reference-separation-policy.md](./entry-guide-reference-separation-policy.md)
- file と棚
  - [file-operation-policy.md](./file-operation-policy.md)
  - [naming-and-shelf-policy.md](./naming-and-shelf-policy.md)
  - [project-template-installation-gate-policy.md](./project-template-installation-gate-policy.md)
  - [project-publication-responsibility-policy.md](./project-publication-responsibility-policy.md)
- agent 作業
  - [context-management-policy.md](./context-management-policy.md)

## 保管資産として残す文書

- agent 詳細、task 詳細、project-template adoption 詳細は必要時だけ開く
- 入口では全件列挙しない
- 似た役割の policy は後続で統合候補として扱う
