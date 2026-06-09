# PJ Template

**目的**: プロジェクトを組む時の型の正本。

ここでは、特定プロジェクトの current 状態や運用結果は持たない。
持つのは、プロジェクトをどう組み、どう案内し、どう分解して進めるかの型だけである。

## 棚

- `frameworks/`: 設計・分解・意思決定の進め方
- `policies/`: 再利用可能な運用ルール
- `templates/`: 再利用可能な文書雛形
- `checklists/`: 確認項目
- `examples/`: 使用例

## まず読む順

1. `frameworks/project-progression-rule.md`
2. `frameworks/project-progression-rule-integration-audit.md`
   - 接続図・読む順・棚ごとの役割整理だけを読む
3. `frameworks/goal-path-checkpoint-task-design-framework.md`
4. `policies/execution-readiness-gate-policy.md`
5. プロジェクトへ適用する前に `policies/project-template-installation-gate-policy.md`
6. GitHub 公開を扱うプロジェクトでは `policies/project-publication-responsibility-policy.md`
7. 必要なら `templates/project-structure-governance-starter-pack.md`
8. 必要なら `templates/navigation-template.md`
9. プロジェクトへ設置する時は `templates/project-template-adoption-packet-template.md`

## 用語の正本

この template では、少なくとも次の言い方を固定して使う。

- `プロジェクト進行ルール`
- `テンプレート内ルール`
- `プロジェクト固有ルール`
- `完成の定義`
- `現在地`
- `停止理由`
- `書き戻し先`

同じものを別名で呼ばない。
project 側へ落とす時も、まずこのラベルへ寄せてから局所名を足す。

## そのまま使うもの

- プロジェクト進行の最上位ルール
- 5 層の考え方
- 着手前確認の考え方
- task 設計の必須観点
- プロジェクト構造整理の型
- 入口文書の型
- GitHub 公開時の責務分担の型

## 3層の使い分け

この template は、少なくとも次の 3 層を分けて使う。

1. `プロジェクト進行ルール`
   - 最上位の正本
   - 主語、進行、停止、再接地を定める
2. `テンプレート内ルール`
   - 上位ルールを project に落とすための共通具体化
   - gate、雛形、checklist、構造整理、入口整理を持つ
3. `プロジェクト固有ルール`
   - その project の目的、current、runtime 実体、owner 判断だけを持つ

下位層は上位層に反してはならない。

## プロジェクトごとに差し替えるもの

- 入口 file の path
- 今の状態を見る file 名
- command 名
- 棚名
- プロジェクト固有の運用ルール名

## template 側へ寄せるもの

次は、できるだけ project 固有へ残す前に template 側へ寄せる。

- 進め方
- 完成までの骨格
- 入口の作り方
- `current / support / historical / generated` の分け方
- restart / handoff の扱い
- 公開責務の扱い方
- 構造整理の重さ
- runtime 実体を local に持つか downstream に持たせるか

つまり、`やり方` と `分岐条件` は template 側の責務とする。

## project 固有へ残すもの

次は project 固有へ残す。

- その project の completion definition
- その project の current 正本
- その project の runtime / DB / caller 実体
- owner-only decision
- project 固有の path、棚名、command、運用事情

つまり、`中身` と `その project にしか属さない最終判断` は project 固有側に残す。

## 書かないこと

- 特定プロジェクト固有の current 状態
- 特定プロジェクトの task 状態
- 特定プロジェクトの運用ログ
- 特定プロジェクトの register 本文

## 戻り先

迷ったら `../README.md` に戻る。

## reference との境界

`../refernce/` にある議論ログは、経緯と失敗分析の記録として参照してよい。
ただし、現行の正本はこの `pj-template` 側にある。

`project-progression-rule-integration-audit.md` から切り出した時点判断や波の監査記録は、
`../refernce/pj-template-progression-rule-audit-history-20260608.md`
を参照する。
