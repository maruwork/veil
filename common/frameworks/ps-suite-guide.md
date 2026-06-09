# PS Suite Guide

PS Suite は、設計・開発・ガバナンスにおける
`理解 → 発見 → 定義 → 実行 → 評価 → 改善`
のサイクルを、独立したフレームワーク群として扱うための reusable guide である。

この guide は
`project-progression-rule.md`
のうち、主に

- `どこから理解を始めるか`
- `何が不足しているかをどう見つけるか`
- `改善を次の進行へどう戻すか`

を、補助フレームワーク群として支える文書である。

この文書は project-agnostic baseline であり、特定プロジェクトの current task / current runtime / governance SSOT の代替ではない。

この guide の役割は `PS 系 framework 群をどう読み始め、どう受け渡すか` に限る。

- framework family 全体から何を選ぶか
- prompt / instruction 改善サイクルをどう回すか

までをここで再定義しない。

framework family の横断選定は
`framework-selection-guide.md`
を、prompt / instruction 改善の反復は
`prompt-quality-improvement-cycle.md`
を正本とする。

## 1. What It Is

PS Suite は次の 6 フレームワークで構成される。

| ID | Name | Typical question |
|---|---|---|
| `PSU` | Periodic Structured Understanding | 既存システムの全体像をどう理解するか |
| `PSD` | Periodic Structured Discovery | 何が足りないか、何が壊れているか |
| `PSM` | Periodic Structured Mapping | 現在地と優先順位をどう定義するか |
| `PSX` | Periodic Structured eXecution | 設計をどう実装し、証跡を残すか |
| `PSE` | Periodic Structured Evaluation | 施策は効果があったか |
| `PSI` | Periodic Structured Improvement | 学びをどう次へつなぐか |

## 2. When To Use It

PS Suite は、次のような状況で使う。

- 全体像がつかめない
- 問題は感じるが、何が不足しているか定義できない
- 次に何をやるべきか曖昧
- 実装は進むが、証跡と完了判定が弱い
- 施策の効果測定ができない
- 同じ問題が繰り返される

## 3. Entry Rule

いつも `PSU` から始めるとは限らない。現在の困りごとに応じて開始点を決める。

| Situation | Start from |
|---|---|
| 全体像が不明 | `PSU` |
| 足りないもの・壊れているものが不明 | `PSD` |
| 現在地と優先順位が曖昧 | `PSM` |
| 実装と証跡化を進めたい | `PSX` |
| 効果を測りたい | `PSE` |
| 再発防止をしたい | `PSI` |

## 4. Full-Cycle Reading

フルサイクルで使う場合の標準読解は次の通り。

1. `PSU`: 理解
2. `PSD`: 発見
3. `PSM`: 定義
4. `PSX`: 実行
5. `PSE`: 評価
6. `PSI`: 改善

ただし、必ずしも毎回 1 → 6 を全部回す必要はない。単体利用でもよい。

## 4.1 PS Entry Point

開始点が分からない場合は、困りごとを次のカテゴリで診断する。

| Situation | Start from |
|---|---|
| システムの構造・全体像が把握できていない | `PSU` |
| 何が足りないか・何が壊れているか分からない | `PSD` |
| ゴール・現在地・優先順位が曖昧 | `PSM` |
| 実装方法・証跡化・承認運用が曖昧 | `PSX` |
| 施策の効果を測定できていない | `PSE` |
| 同じ問題が繰り返されている | `PSI` |

複数カテゴリに該当する場合の推奨優先順は次の通り。

- `PSU` が含まれるなら理解を先に置く
- `PSD` と `PSM` が競合するなら発見を先に置く
- `PSX / PSE / PSI` だけで済む時は、必要な問いに最も近いものから始める

## 5. Input / Output Contract

PS Suite を reusable framework として使う場合、各フレームワークは少なくとも次を明示する。

| Framework | Minimum output |
|---|---|
| `PSU` | understanding report / uncertainty list / implementation guide |
| `PSD` | discovery list / priority order / change candidates |
| `PSM` | gap list / success criteria / action list |
| `PSX` | implementation evidence / completion conditions |
| `PSE` | result / metric actuals / fail reasons / side effects |
| `PSI` | root causes / improvement actions / next-cycle handoff |

## 5.1 Framework Handoff Schema

各フレームワークは、次フレームワークへ最低限次の構造を渡せる状態にする。

| Framework | Required handoff fields |
|---|---|
| `PSU` | `understanding_report`, `uncertainty_list`, `implementation_guide` |
| `PSD` | `discovery_list`, `priority_order`, `change_candidates` |
| `PSM` | `gap_list`, `success_criteria`, `constraints`, `action_list` |
| `PSX` | `implementation_evidence`, `completion_conditions`, `scope_id` |
| `PSE` | `result`, `metric_actuals`, `fail_reasons`, `side_effects` |
| `PSI` | `root_causes`, `improvement_actions`, `next_cycle_handoff` |

この handoff schema は project-specific storage や event ledger の代替ではない。採用先では、

- どこへ保存するか
- 誰が読むか
- どの段階で human gate を入れるか

を別途決める。

## 6. Operational Rule

- 単体利用でも、最後は次のアクションまたは handoff を残す
- `見つけた` だけで終わらせない
- `実装した` だけで終わらせない
- `評価した` だけで終わらせない
- 必ず次の判断や改善につながる出力を残す

## 6.1 Multi-Step Execution Rule

PS Suite の complete guide や companion guide は、多段階実行になりやすい。実行時は次を守る。

- 1ステップごとに出力を固定してから次へ進む
- 次ステップは前ステップ出力を参照して開始する
- 前ステップ出力を参照できない時は、次へ進まず前ステップを完了させる

複数ターンや複数 agent を使う場合の推奨運用は次の通り。

1. ターン N で step N の出力を確定する
2. ターン N+1 は step N の出力を引用または構造化参照して開始する
3. 引用・参照できない場合は step N を未完了とみなす

単一ターンで実行せざるを得ない場合も、各 step を区切り、

- `step N 完了`
- `step N+1 開始時の前提参照`

を明示する。要するに、`多段階だから一気に流す` のではなく、`多段階だから前段出力を固定する` を優先する。

## 7. Completion Rule

PS Suite 適用を `complete` とみなすには、少なくとも次を満たす。

- 開始したフレームワークの出力が残っている
- 次の action / decision / handoff が明示されている
- completion 条件と未完了条件が区別されている
- 見かけ上の解決と根本解決が区別されている

## 8. Adoption Notes

別プロジェクトへ持ち出す時は、次をその project 側で定義する。

- action 起票形式
- approval / human gate
- evidence 保存場所
- success criteria の閾値
- completion 判定ルール

この guide 自体は reusable baseline であり、project-specific workflow や storage contract は採用先で明示する。

<a id="psu-complete-guide"></a>
## 9. PSU Complete Guide

PSU（Periodic Structured Understanding）を、project-agnostic に実行するための reusable baseline guide。

### 9.1 Purpose

- 既存システムや断片メモの全体像を構造的に理解する
- discovery / mapping に渡せる形へ理解を整理する

### 9.2 Core Question

「この対象は何で、どう動き、何が重要なのか」

### 9.3 Phase Order

1. target and mode fixation
2. context overview
3. domain deepening
4. dynamic flow understanding
5. summary and integration
6. blind-spot review
7. understanding handoff

### 9.4 Minimum Output

- context map
- domain model
- dynamic flow summary
- integrated understanding summary
- blind spots / uncertainties

### 9.5 Completion Rule

- 境界が定義されている
- context / domain / flow / summary が揃っている
- blind spots が残っているなら明示されている
- downstream framework へ handoff できる

<a id="psd-complete-guide"></a>
## 10. PSD Complete Guide

PSD（Periodic Structured Discovery）を、project-agnostic に実行するための reusable baseline guide。

### 10.1 Purpose

- 構造的な盲点を発見する
- 「存在すべきだが存在しないもの」と「設計レベルの欠陥」を分けて扱う
- 発見結果を優先順位付き action へ落とす

### 10.2 Core Question

「何が足りないか、何が壊れているか、何を次に起票すべきか」

### 10.3 Phase Order

1. retrospective review
2. functional discovery
3. bug discovery
4. integrity confirmation
5. discovery loop
6. prioritization
7. action creation

### 10.4 Minimum Output

- discovery candidate list
- invalid / duplicate / out-of-scope exclusion list
- prioritized action list
- handoff to mapping / execution

### 10.5 Completion Rule

- discovery loop の飽和根拠がある
- prioritization 済みで HIGH action が明示されている
- 「発見しただけ」で終わらず次 action が残っている

<a id="psm-complete-guide"></a>
## 11. PSM Complete Guide

PSM（Periodic Structured Mapping）を、project-agnostic に実行するための reusable baseline guide。

### 11.1 Purpose

- 現在地を定義する
- future state を定量化する
- 過去 / 現在 / 未来の差分から次 action を出す

### 11.2 Core Question

「今どこにいて、どこへ行くべきで、その差分は何か」

### 11.3 Phase Order

1. scope fixation
2. history understanding
3. as-is measurement
4. future definition
5. gap extraction
6. prioritization
7. action creation

### 11.4 Minimum Output

- scoped target
- as-is measures
- target future state
- gap list
- prioritized action list

### 11.5 Completion Rule

- 現在地が測定されている
- 未来定義が明示されている
- gap が action に変換されている
- HIGH action を残して終了しない

<a id="psx-complete-guide"></a>
## 12. PSX Complete Guide

PSX（Periodic Structured eXecution）を、project-agnostic に実行するための reusable baseline guide。

### 12.1 Purpose

- 決定を承認・実装・監査・証跡化まで通す
- 「実装した」だけで終わらせず、設計整合と完了判定を残す

### 12.2 Core Question

「決めたことを、どう安全に実装し、どう証跡化するか」

### 12.3 Phase Order

1. execution scope fixation
2. implementation design record
3. human / design gate
4. implementation execution
5. implementation verification
6. evidence recording
7. handoff

### 12.4 Minimum Output

- scope and completion conditions
- design record
- approval result
- implementation result
- verification result
- evidence bundle
- handoff

### 12.5 Completion Rule

- 実装前に scope と completion condition がある
- 設計記録と承認がある
- verification result がある
- evidence と handoff が残っている

<a id="pse-complete-guide"></a>
## 13. PSE Complete Guide

PSE（Periodic Structured Evaluation）を、project-agnostic に実行するための reusable baseline guide。

### 13.1 Purpose

- 実装完了と目的達成を区別する
- 目標値と実績値の差を判定する
- PASS / FAIL / PARTIAL の evidence を残す

### 13.2 Core Question

「この施策は本当に効果があったか」

### 13.3 Phase Order

1. evaluation target fixation
2. criteria confirmation
3. actual measurement
4. delta calculation
5. quality gate verdict
6. verdict recording
7. next handoff decision

### 13.4 Minimum Output

- evaluation criteria
- actual measurements
- verdict
- reasons
- next handoff

### 13.5 Completion Rule

- 判定基準が先に固定されている
- 実績計測が残っている
- verdict と根拠がある
- 次の execution / improvement / escalation が明示されている

<a id="psi-complete-guide"></a>
## 14. PSI Complete Guide

PSI（Periodic Structured Improvement）を、project-agnostic に実行するための reusable baseline guide。

### 14.1 Purpose

- 評価結果を学習へ変える
- 再発要因と成功要因を抽出する
- 次 cycle で実行すべき改善 action を定義する

### 14.2 Core Question

「この結果から、何を次の改善として固定すべきか」

### 14.3 Phase Order

1. evaluation intake
2. cause analysis
3. learning extraction
4. application scope decision
5. improvement action definition
6. prioritization
7. improvement action creation

### 14.4 Minimum Output

- success / failure causes
- reusable learnings
- application scope
- prioritized improvement actions

### 14.5 Completion Rule

- 学習が抽出されている
- 適用範囲が明示されている
- 改善 action が起票可能な粒度に落ちている
- 次 cycle への handoff がある

<a id="system-understanding-approaches-guide"></a>
## 15. System Understanding Approaches

対象理解を `俯瞰 / 深掘 / 動態 / 要約 / 検証` の 5 観点で進める reusable baseline guide。

### 15.1 Purpose

- コンテキスト、概念、動き、要約、盲点を段階的に理解する
- 既存システム理解にも、断片メモからの構造化にも使う

### 15.2 Approaches

1. context overview
2. domain deepening
3. dynamic flow tracing
4. summary and integration
5. blind-spot review

### 15.3 Minimum Output

- context map
- domain model
- flow trace
- layered summary
- risks / uncertainties

### 15.4 Completion Rule

- 5観点の出力が揃っている
- downstream discovery / mapping に渡せる

<a id="history-understanding-framework"></a>
## 16. History Understanding

過去の意思決定、変更、未解決事項を事実ベースで整理する reusable baseline framework。

### 16.1 Purpose

- 現在の状態がなぜ生じたかを把握する
- 主観ではなく事実を時系列で残す
- 未解決事項を次の測定や gap 抽出に渡す

### 16.2 Phase Order

1. fact extraction
2. decision extraction
3. issue / failure extraction
4. delta extraction
5. unresolved carryover extraction

### 16.3 Minimum Output

- chronological facts
- decisions and reasons
- issues and responses
- key deltas
- unresolved carryovers

### 16.4 Completion Rule

- 解釈ではなく事実で書かれている
- 時系列が保たれている
- 未解決事項が次 phase に渡せる形で残っている

<a id="functional-identification-framework"></a>
## 17. Functional Identification

設計や要求から必要機能を網羅的に洗い出すための portable baseline framework。

### 17.1 Purpose

- 設計固着を崩し、見落としやすい機能を見つける
- 正常系だけでなく例外、運用、時間軸まで含めて洗い出す

### 17.2 Core Approaches

1. 制約反転
2. 極端ユーザー
3. 代替世界比較
4. 逆目的化
5. 分解限界
6. 時間軸展開

### 17.3 Output Contract

- 各観点ごとの発見結果
- 統合後カテゴリ一覧
- 重複除去済みの最終機能リスト

### 17.4 Handoff Rule

- 統合済み機能リストを次の bug / integrity 側チェックに渡す

<a id="bug-discovery-framework"></a>
## 18. Bug Discovery

異常入力、過負荷、不整合、仕様ズレなどの観点から不具合を網羅的に洗い出す portable baseline framework。

### 18.1 Purpose

- 正常系バイアスを外し、異常系を体系的に観測する
- 実運用で破綻する条件を設計段階から洗い出す

### 18.2 Core Approaches

1. 破壊前提
2. 極端負荷
3. 状態不整合
4. 逆仕様
5. 分解検証
6. 時間破壊

### 18.3 Output Contract

- 異常条件
- 想定バグ
- 優先度や再現条件

### 18.4 Handoff Rule

- 状態不整合や逆仕様は integrity 側の追加確認へ送る
- 高リスク候補は prioritization 側で優先度付けする

<a id="integrity-confirmation-framework"></a>
## 19. Integrity Confirmation

発見・設計・要件定義の内容に矛盾、抜け漏れ、ズレがないかを確認する portable baseline framework。

### 19.1 Purpose

- 発見した内容が論理的に整合しているかを確認する
- 生成物の量ではなく、一貫性と妥当性を担保する

### 19.2 Review Axes

1. 前提衝突
2. 因果整合
3. 目的適合
4. 網羅整合
5. 状態遷移整合

### 19.3 Output Contract

- 問題箇所
- 問題種別
- 修正方針または除外理由

### 19.4 Handoff Rule

- 除外候補、確定候補、再検討候補に分けて後続へ送る

<a id="discovery-operation-template"></a>
## 20. Discovery Operation

発散、統合、検証、再探索を反復運用するための portable baseline template。

### 20.1 Fixed Loop

1. 発散
2. 統合
3. 検証
4. 再探索

### 20.2 Phase Prompts

- 発散: 観点別に最大量を列挙する
- 統合: 重複除去、分類、抽象化を行う
- 検証: 抜けた観点と放置リスクを出す
- 再探索: 不足分だけを補い、既出内容は繰り返さない

### 20.3 Loop End Condition

- 新規発見が飽和する
- 構造が安定する
- 追加観点が減少または 0 になる

### 20.4 Record Rule

- 各周回を明示する
- 周回ごとの追加件数を記録する
- 前周との差分が分かる形で残す

<a id="prioritization-decision-framework"></a>
## 21. Prioritization Decision

候補群の実装順や修正順を客観的に決めるための portable baseline framework。

### 21.1 Fixed Axes

- 影響度
- 発生頻度
- 実装コスト
- リスク

### 21.2 Scoring

- 各軸を 1 から 5 で評価する
- 優先度スコアは `(影響度 × 発生頻度 × リスク) ÷ 実装コスト` で算出する

### 21.3 Decision Bands

- 15 以上: 即対応
- 5〜14: 条件付き対応
- 5 未満: 保留または不採用

### 21.4 Output Contract

- 項目名
- 4軸スコア
- 算出スコア
- 対応方針

### 21.5 Merge Rule

- 根本原因、実装 file、解決経路が同一なら統合候補
- score 差が大きいもの、担当や blocker が異なるものは統合しない

<a id="retrospective-verification-framework"></a>
## 22. Retrospective Verification

過去の実装や判断が、起票時の問題を本当に解決したかを確認する portable baseline framework。

### 22.1 Purpose

- 過去の問題が未解決のまま再発見される空回りを防ぐ
- 実装後に生じた副作用や前提崩れを早期に見つける

### 22.2 Review Axes

1. 問題解決確認
2. 副作用確認
3. 意図適合確認
4. 完全性確認
5. 陳腐化確認

### 22.3 Output Contract

- 各項目を `解決済み / 部分的 / 未解決 / 陳腐化` で分類する
- 部分的、未解決、陳腐化には理由を付ける
- 次の発見フェーズへ引き継ぐ項目を明示する

### 22.4 Handoff Rule

- 部分的: 再設計または不足領域の再探索へ送る
- 未解決: 問題再発見の優先候補として扱う
- 陳腐化: 前提更新を伴う再設計候補として扱う

<a id="as-is-measurement-framework"></a>
## 23. As-Is Measurement

対象の現在地を、生成ではなく測定として扱う reusable baseline framework。

### 23.1 Purpose

- 現在地を定量化する
- discovery と measurement を混同しない
- リスクと不確実性を明示する

### 23.2 Phase Order

1. coverage measurement
2. progress measurement
3. quality measurement
4. risk measurement
5. uncertainty measurement

### 23.3 Minimum Output

- coverage
- progress
- quality
- risk
- uncertainty

### 23.4 Completion Rule

- 新規列挙ではなく既存対象の測定に徹している
- 5観点の数値または分類が残っている
- future definition に渡すリスク / 不確実性が明示されている

<a id="future-state-definition-framework"></a>
## 24. Future State Definition

到達すべき future state を、客観的・測定可能に定義する reusable baseline framework。

### 24.1 Purpose

- goal を曖昧な願望で終わらせない
- completion と success criteria を分ける
- current-state との差分を計算可能にする

### 24.2 Phase Order

1. purpose definition
2. completion condition definition
3. constraint definition
4. success metric definition
5. target-state concretization

### 24.3 Minimum Output

- purpose
- completion conditions
- constraints
- success metrics
- target state description

### 24.4 Completion Rule

- 第三者が完了判定できる
- 測定方法がある
- current-state と対比できる
