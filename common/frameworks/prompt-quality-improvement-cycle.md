# prompt quality improvement cycle

失敗ログや差し戻し傾向をもとに、プロンプトや agent instruction を `調査 → 仮説化 → 改訂 → 再測定` で改善するための共通サイクル。

この framework は
`project-progression-rule.md`
のうち、主に

- `ずれを検出する`
- `同じ失敗を繰り返さない`
- `補正後により良い規律へ戻す`

を、prompt / instruction 改善の面で支える文書である。

この framework は `改善サイクル` を扱うのであって、

- どの framework family を選ぶか
- project 全体の開始点をどこに置くか
- PS 系 framework 群の全体読解

を決める文書ではない。

framework family の選定は
`framework-selection-guide.md`
を、PS 系 framework 群の読解は
`ps-suite-guide.md`
を正本とする。

## 1. Purpose

- 感覚ではなく失敗データに基づいて prompt quality を改善する
- `プロンプト改善` と `プロセス改善` を混同しない
- 改訂項目を優先順位づけし、効果測定まで含めて閉じる

## 2. Inputs

- review / audit の差し戻し記録
- failure taxonomy
- representative bad examples
- current prompt / instruction / checklist / workflow spec
- success metric

## 3. Core Loop

1. 現状の失敗を集計する
   - 失敗率
   - 集中ステップ
   - 再発パターン
2. 根本原因を分類する
   - プロンプト構造で改善できる問題
   - プロセス設計の問題
   - current truth 不整合
   - handoff 契約不足
3. 外部知見と照合する
   - reusable pattern
   - anti-pattern
   - 代替構造
4. 改訂候補を優先順位づけする
   - 効果の大きさ
   - 実装コスト
   - 回帰リスク
5. 改訂を実施する
   - wording
   - structure
   - gate
   - expectation contract
6. 再測定する
   - failure rate
   - revision count
   - repeated explanation count
   - handoff loss

## 4. Decision Questions

- これは prompt の問題か、workflow の問題か
- current output contract が次ステップに渡る形になっているか
- gate を増やすべきか、質問や expectation を改善すべきか
- 局所修正で済むか、framework 自体を作り直すべきか

## 5. Output Contract

最低限の出力:

- baseline_failure_pattern
- root_causes
- adopted_changes
- rejected_changes
- expected_effect
- measurement_method
- success_threshold

## 6. Completion

次を満たしたら 1 cycle を閉じてよい:

- 改訂理由が記録されている
- 採用案と非採用案が分かれている
- 効果測定の方法がある
- 再測定後の改善 / 未改善が読める

## 7. Portable Boundary

この文書は prompt quality 改善サイクルの骨格だけを扱う。  
特定 framework 名、特定 product 名、特定 repo の event 名は local source 側に残す。

<a id="automated-discovery-prompt-design"></a>
## 8. Discovery Prompt Design

発見作業を AI と人間の双方で再現可能に回すための portable baseline framework。

### 8.1 Purpose

- 発見を単発の思いつきではなく、反復可能な loop として設計する
- 発散、統合、検証、再探索を分離し、どこで何を確認するかを固定する

### 8.2 Core Loop

1. 発散
2. 統合
3. 検証
4. 再探索

### 8.3 Prompt Guidance

- 発散では「重複を気にせず最大量を出す」ことを先に固定する
- 統合では「カテゴリ」「上位概念」「残る差分」を出させる
- 検証では「何が不足か」だけでなく「なぜ不足したか」を出させる
- 再探索では、既出内容を再掲させず不足分だけを補わせる

### 8.4 Escalation Options

- 制約強化
- 抽象度変更
- 組み合わせ強制

### 8.5 Completion Signal

- 新規カテゴリがほぼ出なくなる
- 統合後の構造が安定する
- 検証フェーズで追加観点が減少または 0 になる

<a id="prompt-question-set-design-framework"></a>
## 9. Prompt Question-Set Design

複雑な調査・設計・比較 task を、順番に答える質問セットへ分解するための共通 framework。

### 9.1 Purpose

- 調査対象が大きい時に、いきなり結論を書かせず段階的に解かせる
- 調査前に質問構造を作り、後付けの軌道修正を減らす
- 前段の答えが後段へ反映されるようにする

### 9.2 Use Cases

- 複数候補の比較
- root cause 調査
- 改善案の発見
- 導入計画や migration 設計
- prompt / framework 自体の見直し

### 9.3 Design Rules

- 質問は 3〜7 個程度に分ける
- 各質問は次の質問に使われる形で出力を残す
- `何を知りたいか` と `何を決めたいか` を混ぜない
- 最後の質問は必ず `推奨` と `理由` と `残る不確実性` を出させる

### 9.4 Recommended Question Order

1. 何が問題か
2. どんな失敗・差分・制約があるか
3. 外部知見や代替案は何か
4. どれを採るべきか
5. どう測るか、どう閉じるか

### 9.5 Output Contract

- question_set
- intermediate_findings
- comparison_axes
- recommended_option
- why_recommended
- remaining_risks

<a id="token-optimization-baseline"></a>
## 10. Token Optimization Baseline

AI agent の token 最適化では、volume reduction と authority boundary を混同しない。

優先する観点:

1. 定型 CLI 出力を薄くする
2. entry file を太らせない
3. boundary-first で読む
4. compact / plan discipline を使う
5. authority source を tool に奪わせない

今すぐ採りやすいもの:

- 定型 CLI 出力圧縮
- 薄い入口文書
- search / read の境界 discipline
- compact / clear / plan の運用

deferred にしやすいもの:

- repo 外 runtime や proxy を増やすもの
- authority surface を増やすもの
- rollback が重いもの

completion を判定する時は、次を確認する。

- token 削減で current canonical reading が遅くなっていないか
- 重要な error cause が隠れていないか
- authority / truth / state / owner を tool 側が決めていないか
