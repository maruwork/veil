# Context Management Policy

**役割**: 長い session、resume、handoff、multi-turn design work で context rot と context pollution を防ぎ、後続 AI でも同じ意味に復元できる状態を保つ。

この policy は
`../frameworks/project-progression-rule.md`
のうち、主に

- `正本への再接地`
- `current を頭の中だけで保持しない`
- `入口を混ぜない`
- `未完了を列挙だけして止まらない`

を具体化する。

## 1. Context は source-first で読む

context は記憶ではなく source から読む。

優先順:

1. search
2. 必要最小限の file / range read
3. generated inventory / projection
4. transcript summary
5. current diff

full reread を前提にせず、source-first で必要部分だけ回収する。

## 2. Canonical state と generated context を分ける

decision、inventory、plan、classification、summary、report は同じものではない。

- canonical state
  - current rule / current path / current truth
- generated context
  - inventory / projection / summary / report / continuation artifact

generated context を canonical state と取り違えない。

## 2.5 ルールの正本を 1 つに固定する

同じ趣旨の reusable rule を複数文書へ書き散らさない。

ルールを追加または補強するときは、先に次を決める。

1. どのファイルをそのルールの正本にするか
2. どのファイルは参照だけに留めるか
3. current case の適用面をどこに置くか
4. validator / healthcheck / gate のどこで fail-close にするか

正本以外の文書に許されるのは、原則として次だけです。

- 正本ルールへの参照
- その場の current case への適用
- その文書に固有の entry / route / file mapping

正本以外の文書で、判定条件、必須項目、停止理由の schema、完了条件を別 wording で再定義してはいけません。

`プロジェクト進行ルール` に関わる最上位の判定条件、停止条件、再接地条件は、
まず `project-progression-rule.md` 側を正本として扱い、
この policy では context 面の具体化だけを行う。

同じ話を別文書で何度も説明しないと通じない場合は、

- 正本が弱い
- entry route が弱い
- current case の適用面が弱い

のどれかとして扱い、重複追記ではなく構造側を直します。

## 3. Drift しやすい作業は continuation note で閉じる

長い task、resume 前提 task、handoff 前提 task は continuation note を残す。

最低限含めるもの:

- goal
- 完了済み作業
- 既知の canonical facts
- already_paid_explanations
- 未完了項目
- touched files
- verification
- next safe action

長期 task や repeated explanation が出た task では、continuation note は「何が fixed でもう説明し直さないか」を明示する。  
memory を session 内期待に残さず、repo-native artifact に戻す。

## 4. Context pollution を避ける

次のものは project knowledge と混同しない。

- logs
- caches
- generated outputs
- historical sessions
- user-global tool state
- repo 外 runtime state

必要なら読むが、canonical としては扱わない。

## 4.5 グローバル設定の境界

- project の構造・配置・検証・workflow・governance を決める rule は、project 内または明示した共通正本に置く。
- 利用者ごとの global 領域には、認証情報、installed tool、plugin、skill、cache、runtime log、session state のような本当に global なものだけを置く。
- global 領域を project 固有 governance の正本の置き場にしない。
- project を理解するために、利用者ごとの非公開 global 設定を読まなければならない状態を作らない。
- global setting が project 実行に影響する場合は、非公開 global file ではなく project 側に要件を書く。

## 5. Clean review

design や review は、作業中の空気ではなく artifact を対象に行う。

必要なら clean-context review pass を挟み、最小限の source だけで再評価する。

ここでいう clean review は、`何を正本として読み直すか` を整えるための規律であり、
不一致の種別分類や false-complete 判定そのものを詳しく行う review 手順は
`../frameworks/decision-to-implementation-consistency-review.md`
側を正本とする。

## 6. Recurring shorthand and comparison target capture

proper noun、比較対象、比喩、shorthand が繰り返し登場し、literal meaning だけでは design / review / tasking の意味が決まらない場合、その語は**期待値つき context object**として扱う。

ルール:

- glossary だけで済ませない
- project-local register に次を保存する
  - 何を指すか
  - どの期待値を背負うか
  - 何を意味しないか
  - どの canonical / intake source が根拠か
  - いつ更新するか
- 後続 AI は、その語を見たら register を優先して読む
- repo にすでに意味がある語を、ユーザーに再説明させる前提で扱わない

このルールは、用語の literal definition を増やすためのものではない。
**「その言葉で何を期待しているか」を保存し、後続 AI の解釈ずれを防ぐためのもの**である。

対象 project では現在、project-local register として
project-local comparison target or shorthand register
を使う。

## 7. English label interpretation rule

英語ラベルは、意味だけでなく**ラベル種別**を明示して扱う。

後続 AI や operator が困るのは、英語そのものではなく、

- それが単なる説明語か
- status / verdict の固定値か
- 変数名 / field 名か
- command / option / policy 名か

が分からない時である。

ルール:

1. 単なる説明語なら、日本語またはカタカナで書く
2. 固定値なら、`status 値` / `verdict 値` / `field 値` のように種別を添える
3. 変数名・field 名なら、``backticks`` で囲み、`変数名` または `field 名` だと明示する
4. command / option / policy 名なら、`command 名` / `option 名` / `policy 名` として明示する
5. 本文は意味を先に書き、必要なら後ろに原文を添える

良い例:

- `現在進行中（status 値: "ACTIVE"）`
- `親タスクは継続判定（parent_verdict の値: "continue"）`
- ``active_branch`` という field 名
- `governance_healthcheck.py の --strict option`

悪い例:

- `active`
- `continue`
- `flowing`
- `reroute`

このルールは翻訳のためではない。
**英語ラベルを見た時に、何の種別の語かを一目で分かるようにするためのルール**である。
