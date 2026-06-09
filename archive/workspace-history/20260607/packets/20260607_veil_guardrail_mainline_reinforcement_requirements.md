# VEIL Guardrail Mainline Reinforcement Requirements

## 1. Overview

### 目的

VEIL を `AI-assisted technical writing` 向けの terminology guardrail として成立させるため、mainline を `capture -> normalize -> sync -> lint` の workflow gate として再定義する。

この wave では特に次を固める。

- `capture` を会話区切り / task close の必須閉じ処理へ寄せる
- `lint` を最終返答前の必須 gate にする
- rule を `必須 / 推奨 / 観察` の 3 層で扱う
- VEIL core と domain profile の境界を固定する

### 背景

- VEIL の本線価値は、static guide ではなく `会話から拾う -> 正規化 -> AI に読ませる -> 出力前検査` を閉じることにある
- これが弱いままだと、VEIL は語彙収集棚や軽い補助スクリプトに留まる
- 一方で、全語彙や自然文全体を全面統制すると過剰統制になりやすい
- よって、厳しく縛るべきものと緩く扱うべきものを structure と運用 rule の両方で切り分ける必要がある

### 参考 / 根拠

- `README.md`
- `docs/veil-design.md`
- `AGENTS.md`
- `skills/codex/veil-capture/SKILL.md`
- `skills/claude-code/veil-capture.md`
- `workspace/reference/20260607_veil_public_release_deep_research.md`
- `common/frameworks/project-progression-rule.md`
- `common/frameworks/goal-path-checkpoint-task-design-framework.md`
- `common/policies/agent-workflow-policy.md`
- `common/policies/verification-and-retry-policy.md`

## 2. Scope

### In Scope

- VEIL の target を `AI-assisted technical writing` 向け terminology guardrail に固定する
- mainline flow における `capture` 必須化と `lint` 必須 gate 化を canonical docs と skill に明記する
- rule レベルを `必須 / 推奨 / 観察` に分ける方針を定義する
- core と profile の責務境界を設計書レベルで固定する
- 判別順を `残す / 訳す / 定義する / 禁止する / 保留` へ再整理する
- high-demand / high-impact 語だけを厳格統制対象にする方針を明記する

### Out of Scope

- この packet での runtime code 実装
- `~/.veil/rules/` の既存フォーマット全面変更
- domain profile の複数実装追加
- 外部 AI tool への自動 hook 実装
- UI / helper DB の再活用

### Assumptions and Constraints

- 語彙正本 authority は引き続き `~/.veil/rules/`
- mainline は `rules / capture / normalize / sync / lint` に限定する
- 機械処理語、コード識別子、ファイル名、CLI option は全面統制対象にしない
- 低頻度語、文脈依存語、未確定の project 固有語は保留または観察へ逃がす

## 3. Success Criteria

- VEIL の説明主語が `AI-assisted technical writing guardrail` に統一される
- `capture` と `lint` が optional helper ではなく workflow gate として読める
- rule 3 層の違いが fail / warning / observe と結びついている
- core と profile の責務境界が明示され、業界別適用の見通しが立つ
- 判別順と report 形式の固定対象が明文化されている

## 4. Functional Requirements

1. VEIL は、high-demand / high-impact 語だけを厳格統制対象にできること
2. `capture` は会話区切り / task close の閉じ処理として運用位置を持つこと
3. `lint` は最終返答前 gate として運用位置を持つこと
4. rule は `必須 / 推奨 / 観察` の 3 レベルで扱えること
5. `必須` は lint violation 時に修正必須、`推奨` は warning、`観察` は集計のみと読めること
6. 判別は少なくとも `固有名として残す`, `一般語として訳す`, `定義語にする`, `禁止語にする`, `保留` の 5 方向へ流せること
7. core と profile の差し替え点が、rules だけでなく判別基準と厳格度も含むと明記されること

## 5. Non-Functional Requirements

- 既存 mainline を壊さない additive な設計であること
- `common` の設計順に従い、先に packet を固定してから実装へ進めること
- mainline 説明面は軽く、人が一読で判断できること
- 業界別転用時に profile 差し替えで説明可能な構造であること

## 6. Risks

- rule 3 層を入れても、現行 rule file format に level 情報をどう載せるか未確定のままだと implementation wave が滞る
- `capture` 必須化を強めすぎると、日次運用で負担感が出る
- `lint` 必須 gate を prose 全体へ広げすぎると過剰統制になる
- profile 差し替えの自由度を先に広げすぎると、current default profile が曖昧になる

## 7. Deferred Follow-up

- rule file format への level 表現追加方法
- `lint` の warning / observe 出力の具体仕様
- domain profile の physical layout
- `capture` trigger の半自動化手段
