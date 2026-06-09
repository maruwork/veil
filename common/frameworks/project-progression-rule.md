# プロジェクト進行ルール

**目的**: AI がプロジェクトを進める時に、主語をずらさず、現在地を見失わず、ずれたら止まり、正本へ戻って再開できるようにするための最上位ルールを定義する。

この文書は `pj-template` の中核正本として扱う。

## 1. 位置づけ

強さ関係は次のとおり。

1. `プロジェクト進行ルール`
2. `テンプレート内ルール`
3. `プロジェクト固有ルール`

下位ルールは上位ルールに反してはならない。

## 2. この文書が必要な理由

AI は数ターンでも認識がずれる。

- 主語がずれる
- 手段が目的化する
- 局所進捗を前進と誤認する
- `current` と全体理解を混ぜる
- 未完了を見つけても列挙だけで止まる

したがって、AI の頭の中の記憶だけで進行を維持することはできない。

必要なのは、

- 何を正とするか
- 何をもって進めるか
- どこで止まるか
- どこへ戻るか

を外部正本として固定し、毎回そこへ再接地することである。

## 3. 核心

このルールの核心は次のとおり。

`正しい認識を外部正本として固定し、毎回そこへ再接地しながら、正しい進行だけを許可する`

したがって、プロジェクト進行とは

- 記憶で保つこと
- 勘でつなぐこと
- 進んだ気になること

ではない。

`正本 -> 判定 -> 実行 -> 検証 -> 記録反映 -> 再接地`

を繰り返すことが進行である。

## 4. 3層構造

このルールは、少なくとも次の 3 層で構成する。

### 4.1 完了骨格

プロジェクトを何をもって閉じるかを定義する層。

- 完成の定義
- 完成に必要なゴール
- 各ゴールまたは各面の完了条件
- 未決事項
- 作業項目

### 4.2 進行ルール

AI が完了骨格に沿ってどう進むかを定義する層。

- 何の入口から読むか
- 今どこにいるか
- 次の 1 手は何か
- 何をもって checkpoint 前進とみなすか
- 何を `current` に残すか

### 4.3 認識・補正規律

AI の認識ずれをどう止め、戻し、補正してから再開するかを定義する層。

- ずれ検出
- 自動停止
- 正本への再接地
- 補正後の再開

## 5. 進行の開始順

AI は task から始めてはならない。

少なくとも次の順で進める。

1. そのプロジェクトで何を扱うか確認する
2. 何をもって完成とみなすかを定める
3. その完成に必要なゴールを洗い出す
4. ゴールに対する完了条件を明示化して固定する
5. 何の入口から読むべきかを判定する
6. 道のりを整理する
7. checkpoint を置く
8. task を洗い出す
9. task を設計に落とす
10. 実行する
11. 検証する
12. 記録を正本へ反映する

## 6. 完了条件の扱い

完了条件は AI が無根拠に決めてよいものではない。

AI は次を踏まえて、暗黙の条件を明示条件として外へ出し、正本に固定する。

- ユーザー要求
- 既存文書
- プロジェクトの性質
- 公開責務
- 運用責務
- 現実の制約

つまり AI の役割は、`勝手に決めること` ではなく、`根拠から定義して固定すること` である。

## 7. 入口の定義

`入口` とは、最初に開く 1 ファイルのことではない。

入口とは、`その時点の目的に対して、どこから読めば正しく理解を始められるかという正本の種類` である。

少なくとも次の入口を区別する。

### 7.1 全体理解の入口

- このプロジェクトは何か
- 何を完成とするか
- どの範囲までが対象か

### 7.2 現在作業の入口

- 今どこを進めているか
- 今の `current` は何か
- 次の 1 手は何か

### 7.3 設計の入口

- どの設計書群から読むか
- どの順で読むか
- 何が `current authoritative source` か

### 7.4 実行の入口

- 何を実行するか
- 何で確認するか
- 結果をどこへ残すか

入口を混ぜてはならない。

## 8. AI が必ず確認すること

AI は少なくとも次を固定できなければ進んではならない。

### 8.1 成功主語

- 今回何が成立すれば成功か
- 完了報告の主語は何か
- 手段を主語にしていないか

### 8.2 読解経路

- 対象全体を理解するためにどのファイル群を読むか
- その順で何が分かるか
- 何がまだ未確定か

### 8.3 進んでよい条件

- 何が揃えば進んでよいか
- 何が未達なら止まるか
- それが観点ではなく停止条件になっているか

### 8.4 現在地

- 今どのゴール配下か
- 今どの checkpoint の前後か
- 今どの task を扱っているか

### 8.5 次の 1 手

- その 1 手が上位主語に直接効くか
- checkpoint を前進させるか
- 局所整備だけで終わらないか

## 9. 進行ループ

AI は毎ターン少なくとも次の順で進める。

1. `再接地`
   - 成功主語
   - `current`
   - 未決事項
   - 次の checkpoint
   を正本から読み直す

2. `次の1手選定`
   - 今やる 1 手が上位主語に直接効くか判定する

3. `着手前確認`
   - 前提条件
   - blocker
   - 読むべき入口
   - 手段の目的化有無
   を確認する

4. `限定実行`
   - 今回の 1 作業束だけを進める
   - 横に広げない

5. `検証`
   - checkpoint が本当に前進したか確認する
   - 局所進捗だけなら前進扱いしない

6. `書き戻し`
   - `current`
   - evidence
   - next action
   - stop reason
   を正本へ戻す

7. `次動作判定 / close / 停止`
   - 次へ進む
   - close する
   - blocker として止まる
   のいずれかを必ず決める

### 9.1 監督出力契約

毎ターンの進行結果は、少なくとも次の項目名で外に残せる形で持つ。

- `成功主語`
- `現在地`
- `今回の 1 手`
- `完了条件`
- `強い証拠`
- `停止理由`
- `次の 1 手`
- `書き戻し先`

会話で説明しただけでは残したことにならない。
これらは project 側の current 正本、reporting 面、adoption packet のいずれかに書ける粒度で定義する。

### 9.2 作業束宣言

AI は、active な作業束を宣言できなければ着手してはならない。

最低限固定するもの:

- `active bundle id`
- `active bundle type`
  - `mainline`
  - `residual`
  - `historical`
  - `migration`
- `成功主語`
- `完了条件`
- `今回やる範囲`
- `今回やらない範囲`
- `次の 1 手`
- `停止条件`

これらが current 正本、packet、reporting 面のどれにも書けないなら開始禁止とする。

### 9.3 close と residual の分離

close 済み束のあとに residual を続ける時は、同じ束の続きとして扱ってはならない。

- `close record` は close として閉じる
- residual を続ける時は新しい bundle id を立てる
- `close 済み bundle の current 変更` と `post-close residual` を混ぜない

### 9.4 続行時再確認と plan 戻り条件

`次` や `続行` であっても、少なくとも次を再確認する。

- いまの active bundle id は何か
- その bundle は `active` か `closed` か
- 次の 1 手は plan にあるか
- 触ろうとしている file はその bundle の対象か

次のどれかが出たら、実装を止めて plan に戻る。

- 削りすぎると証跡が消える懸念が出た
- current / historical の境界が弱くなる懸念が出た
- family 統合で読み筋が悪くなる懸念が出た
- active bundle に属さない file を触ろうとしている
- close 済み bundle なのに新規 current 変更をしようとしている

## 9.5 連続進行規律

このルールでは、`普通の段の切り替わり` を停止理由にしてはならない。

つまり、次のようなものは停止理由にならない。

- 入口確認が終わった
- 整理台帳を置いた
- 監査表を置いた
- 未完了項目が見えた
- 次にやるべきことが明確に残っている

これらは `次の作業へ続行すべき状態` である。

AI は次の条件を満たす限り、止まらずに続行する。

1. 次の 1 手が特定できる
2. その 1 手が上位主語に直接効く
3. owner 判断が新しく必要になっていない
4. 権限、破壊操作、外部依存の新 blocker が出ていない

逆に、停止してよいのは次の場合だけである。

1. owner 判断が新しく必要
2. 権限不足または破壊的変更判断が必要
3. 正本同士が矛盾し、先に裁定が必要
4. 次の 1 手が特定できない
5. 次の 1 手が特定できても、上位主語に直接つながらない

したがって、`未完了が見えているのに区切りで止まる` のはルール違反として扱う。

## 10. ズレ補正

AI は `ずれないこと` を前提にしてはならない。

`ずれたら止まり、戻り、補正してから再開すること` を前提にする。

### 10.0 強制確認タイミング

次のタイミングでは、ずれ検出を省略してはならない。

1. 作業開始前
2. 次の 1 手を選ぶ時
3. 1 束の作業を終えた直後
4. ユーザーから認識ずれを指摘された時
5. 全体理解、入口、current、正本、project 固有 rule の話題が出た時

### 10.1 ズレ検出

少なくとも次を検査する。

- 今の作業は成功主語に直接効いているか
- 今読んでいる面は正しいか
- 上位問いに未回答なのに局所進捗を前進扱いしていないか
- 未完了を列挙したまま次へ進もうとしていないか

### 10.2 自動停止

ずれを検出したら、

- 続けない
- 進捗扱いしない
- 別作業へ広げない

を強制する。

### 10.3 正本への再接地

停止後は少なくとも次へ戻る。

- 成功主語
- 読解経路
- `current`
- 未達条件
- next action

### 10.4 補正後の再開

再開時は少なくとも次を明示する。

- 修正後の成功主語
- 修正後の `current`
- 修正後の次の 1 手
- 修正後の停止条件

## 11. 未完了を見つけた時の規律

AI は未完了を見つけた時、列挙だけで止まってはならない。

少なくとも次を行う。

1. 最重要の未完了項目を選ぶ
2. それを今ここで閉じるべき項目として扱う
3. 定義または判定の水準まで進める

`必要なら次に出せる` という形で、展開責任を返してはならない。

この規律は `連続進行規律` と一体である。

- 未完了が見えた
- 次の 1 手も見えている

なら、停止せずそのまま次の 1 手へ進む。

## 12. 前進の定義

次は前進とみなさない。

- ファイルを増やしただけ
- section をそろえただけ
- register を整えただけ
- 見た目だけ整理しただけ
- 上位問いにまだ答えられないまま局所改善しただけ
- 入口 README や補助整理だけを進めたが、主線の yes / no 判定は増えていない
- template で吸える差分を project 固有 rule として追加しただけ

次は前進とみなす。

- 上位の問いに yes / no で答えられるようになった
- 未達が停止対象か進行可能か判定できた
- 読解経路が一意になった
- checkpoint が通過した
- 主語に直接ぶら下がる不足が 1 つ閉じた

停止すべき例は次である。

- 次の 1 手はあるが、上位主語に直接効かない
- branch decision を埋めずに project 固有 rule を増やそうとしている
- current 正本が曖昧なまま handoff や support 文書で代用しようとしている

## 13. 人間が監督する時に見えるべきもの

人間は中身の完全正解を知らなくても、少なくとも次が見えれば監督できる。

- 今回の成功主語
- 今の現在地
- 今回進める 1 手
- その完了条件
- 強い証拠
- 停止理由
- 今回の結果
- 次の 1 手
- 書き戻し先

この項目群は、`監督出力契約` として project 側の reporting 面にも残せるようにする。

## 14. `pj-template` 内ルールとの関係

この文書は `pj-template` の最上位ルールである。

既存文書との関係は次のとおり。

- 5 層分解の具体化
  - `goal-path-checkpoint-task-design-framework.md`
- 着手前確認と停止条件の具体化
  - `execution-readiness-gate-policy.md`
- task 状態と `current` 正本運用の具体化
  - `task-realtime-operation-policy.md`
- 業務全体の流れの具体化
  - `business-workflow-spine.md`

既存文書はこの文書に従属する具体化文書として扱う。

## 14.5 template 側へ吸収する分岐

プロジェクトごとの差は、できるだけ project 固有 rule に落とす前に、
template 側の `分岐条件` として吸収する。

ここで扱うのは `Pier型` や `ACI型` のような名前ではなく、
`何が可変で、何を template が受け止めるか` である。

少なくとも次を分岐条件として扱う。

### 14.5.1 current 所有位置

- `local-current`
  - その shelf 自身が daily current の正本を持つ
- `no-local-current`
  - その shelf 自身は daily current の正本を持たず、downstream / operator / integration 側の current 正本へ戻る
- `no-current-canonical`
  - その project は日次 current 正本を持たず、静的な入口と正式文書を中心に扱う

### 14.5.2 restart 補助の有無

- `restart-aid-present`
  - handoff や restart aid を持つ
- `restart-aid-none`
  - restart aid を持たない

restart aid があっても、canonical current の代替にはしない。

### 14.5.3 公開責務の有無

- `publication-planned`
  - 公開責務、公開前確認、公開後責務分担を持つ
- `publication-not-planned`
  - 現時点では公開責務を持たない

### 14.5.4 構造整理の重さ

- `lightweight`
- `standard`
- `extended`

これは file / shelf / generated / archive / boundary の整理にどこまで template を使うかの差であり、
進行ルールそのものの差ではない。

### 14.5.5 runtime 実体の位置

- `runtime-local`
  - 実行主体や runtime-sensitive path がその project 自身に強くある
- `runtime-downstream`
  - 実行主体は downstream / caller / operator 側にあり、この shelf は entry / contract / support を主に持つ
- `runtime-none`
  - この project 自身は runtime 実体を持たず、文書、schema、artifact、static content を主に持つ

AI は project を読む時、まずこの分岐条件を埋める。
分岐条件で吸収できる差を、安易に `別型` や `project 固有例外` にしてはならない。

分岐条件は記入して終わりではない。
少なくとも次の連動制約を満たす。

- `current ownership = local-current`
  - local shelf 側の `current canonical` を持つ
- `current ownership = no-local-current`
  - local shelf 側の `current canonical = none`
  - downstream / operator / integration 側の current 正本 path を持つ
- `current ownership = no-current-canonical`
  - local shelf 側の `current canonical = none`
  - downstream / operator / integration 側の current 正本 path も `none`
  - 唯一入口と正式文書だけで current 不在を説明できる
- `restart aid = restart-aid-present`
  - restart aid path を持つ
  - canonical current の代替ではないと明示する
- `restart aid = restart-aid-none`
  - restart aid path は `none`
- `publication mode = publication-planned`
  - 公開責務 path または packet 側の公開責務記録を持つ
- `runtime placement = runtime-local`
  - local runtime-sensitive path を持つ
- `runtime placement = runtime-downstream`
  - downstream 側 runtime authority path を持つ
- `runtime placement = runtime-none`
  - local runtime-sensitive path も downstream 側 runtime authority path も `none`
  - runtime 面がないことを入口か packet で説明できる

### 14.5.6 project 固有ルールへ残してよいもの

次は project 固有ルールへ残してよい。

- その project の completion definition
- その project の current canonical
- その project の runtime / DB / caller 実体
- owner-only decision
- project 固有の path、棚名、command、外部依存

project 固有ルールへ残す場合は、必ず `template で吸えなかった理由` を残す。
記録せずに project 固有 rule を増やしてはならない。

逆に、次は project 固有ルールへ落とす前に、まず template 側で吸収できないか確認する。

- 進め方
- 停止条件の型
- current / support / generated / historical の分け方
- restart / handoff の扱い
- 公開責務の扱い
- 構造整理の重さ
- runtime を local / downstream のどちらで持つか

ここを安易に project 固有へ落とすと、再利用可能な rule が増えず、
同じ認識ずれを project ごとに繰り返す。

## 15. プロジェクト適用時の使い方

各プロジェクトでは少なくとも次の順で使う。

1. この文書を読む
2. completion definition を作る
3. template 側の分岐条件を埋める
4. goal / path / checkpoint / task / design をプロジェクトに落とす
5. `current` 正本と記録先を決める
6. 進行中は毎ターンこのループに戻る
7. ずれたら停止し、正本へ再接地する

## 16. 最低限守ること

少なくとも次を破ってはならない。

- task から始めない
- 完成の定義より前にゴールを固定しない
- ゴールより前に道のりを作らない
- 完了条件なしに進めない
- 入口を混ぜない
- 未完了を列挙だけして止まらない
- 局所進捗を前進と数えない
- `current` を頭の中だけで保持しない
- ずれを見つけたのに止まらない進行をしない

## 17. 次に読む文書

1. [project-progression-rule-integration-audit.md](project-progression-rule-integration-audit.md)
2. [goal-path-checkpoint-task-design-framework.md](goal-path-checkpoint-task-design-framework.md)
3. [business-workflow-spine.md](business-workflow-spine.md)
4. [execution-readiness-gate-policy.md](../policies/execution-readiness-gate-policy.md)
5. [task-realtime-operation-policy.md](../policies/task-realtime-operation-policy.md)
