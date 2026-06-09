# Project Navigation テンプレート

**使う場面**: project の入口、正式文書、補助文書、今の状態を見る場所を分ける時に使う。  
**差し替える所**: project ID、入口ファイル、棚名、current surface、補助棚の構成。  
**書かないこと**: 各棚の詳細 rule 本文、project 固有の task 正本、日々の更新ログ。  

**Project ID**:
**目的**:
**Phase**:
**Updated**: YYYY-MM-DD

## 0. この雛形で決めること

- 入口を 1 つにする
- 案内文を増やしすぎない
- 今の状態を見る場所を分ける
- 正式文書と補助文書を混ぜない
- template 側が吸収する分岐条件を先に固定する

この template は navigation の project-local 具体化に使う。
最上位の進め方そのものは
`../frameworks/project-progression-rule.md`
を正本とし、この template では

- その project の唯一入口
- current を見る順
- 正式文書と補助文書の分離

だけを固定する。

先に固定する分岐条件は次のとおり。

- `current ownership`
- `restart aid`
- `publication mode`
- `structure weight`
- `runtime placement`

## 1. 入口

**唯一入口**:
- `{example only: README.md / index.md / docs/README.md}`

入口ファイルでは少なくとも次を案内する。

| 見たいこと | 開く先 |
|---|---|
| この project は何か |  |
| 今どこを見るか |  |
| 設計をどこから読むか |  |
| rule / governance の正本はどこか |  |
| runtime / DB / tool 実体はどこか |  |

## 1.5 Template Branch Decisions

| 項目 | 値 | navigation への影響 |
|---|---|---|
| `current ownership` |  | local current を自棚で案内するか、downstream current 正本へ戻すか、current 不在を明示するか |
| `restart aid` |  | handoff を補助として出すか、出さないか |
| `publication mode` |  | 公開責務 bundle を入口で前に出すか |
| `structure weight` |  | 軽量 / 標準 / 拡張のどこまで入口で見せるか |
| `runtime placement` |  | runtime surface を local で案内するか、downstream 側へ戻すか、runtime 不在を明示するか |

branch decision を書いたら、少なくとも次も合わせて決める。

- local current path か downstream current path のどちらを使うか
- `no-current-canonical` なら current 不在と唯一入口だけで扱うか
- restart aid path を持つか `none` にするか
- publication responsibility path を持つか `none` にするか
- local runtime-sensitive path か downstream runtime authority path のどちらへ戻すか
- `runtime-none` なら runtime 面を `none` にするか

## 2. 案内文

案内文は 3 本までを原則とする。

| 案内文 | 役割 | 開く時 |
|---|---|---|
| `{example only: guide-first-read.md}` | 初見の理解順 | 全体像から入る時 |
| `{example only: guide-current-work.md}` | 今の作業を追う順 | 今動いている束を追う時 |
| `{example only: guide-runtime.md}` | 実装面や実体を辿る順 | 実装面や実行系を見る時 |

追加の案内文が必要なら、既存文書に吸収できない理由を書く。

## 3. 正式文書

| 文書 | 役割 | Path |
|---|---|---|
| overview / concept |  |  |
| 今の状態 |  |  |
| governance / rule SSOT |  |  |
| runtime / implementation |  |  |

## 4. 補助棚

inventory、generated index、backlog catalog、historical lookup は reference shelf に寄せる。

| Path | 役割 | 非正本メモ |
|---|---|---|
|  |  |  |

補助文書は今の状態の正本を兼ねない。

## 5. 今の状態の入口

最初に今の状態を読む面だけを最小セットで宣言する。

project によっては、この shelf 自体が daily current を持たない場合がある。
その場合は、ここを空欄のままにせず、

- `この shelf に local current はない`
- `どの downstream / operator / integration surface が current 正本か`

を明記する。

また、project によっては daily current 自体を持たない静的棚もある。
その場合は、

- `この project に daily current 正本はない`
- `唯一入口と正式文書だけで扱う`

を明記する。

| 順番 | Path | 役割 |
|---|---|---|
| 1 |  |  |
| 2 |  |  |
| 3 |  |  |

## 5.2 入口の役割分離

今の project では、少なくとも次を混ぜずに書く。

| 入口の種類 | Path | 役割 |
|---|---|---|
| 全体理解の入口 |  |  |
| 現在作業の入口 |  |  |
| 設計の入口 |  |  |
| 実行面の入口 |  |  |

## 5.3 bundle declaration と continue の戻り先

| 項目 | Path | 役割 |
|---|---|---|
| bundle declaration surface |  | active bundle id / type / success subject を読む |
| continue check surface |  | `続行` 時の next action / stop reason を読む |
| close record surface |  | close 済み bundle を読む |
| residual bundle surface |  | post-close residual を別 bundle として読む |

`continue` をする時は、bundle declaration surface から戻る。
close 済み bundle を読んだだけで active bundle を確定しない。

## 5.5 今の状態の入口に使わない面

次の面は `support / audit / inventory / boundary` として扱い、daily current の入口に使わない。

- `{example only: pending-tasks.md}`
- `{example only: repo-file-disposition-audit.md}`
- `{example only: runtime-structure-map.md}`
- `{example only: *-boundary-register.md}`

これらを visible support として残す場合も、current progress の正本や primary current surface の代用にしない。

## 5.6 restart と handoff の扱い

handoff は restart aid には使ってよいが、canonical current surface の代替にはしない。

- handoff がある時は、先にそれを読んで `どの lane を再開するか` を絞ってよい
- ただし current parent / current branch / latest close record の正式状態は、必ず current の正本へ戻って確認する
- handoff だけを読んで daily current を確定しない

## 6. 読む順

| 知りたいこと | 順路 |
|---|---|
| 初見で全体像を掴みたい | `唯一入口` -> `全体理解の入口` -> `overview / concept` -> `governance / rule SSOT` |
| いま進んでいる作業を追いたい | `唯一入口` -> `現在作業の入口` -> `今の状態` -> `current 正本` |
| runtime / DB / tool 実体を見たい | `唯一入口` -> `実行面の入口` -> `runtime / implementation` |

## 7. 完了確認

- 入口ファイルだけで next step を選べる
- 案内文が入口の代わりや補助棚の代わりになっていない
- 補助文書を今の状態の正本と誤認しにくい
- 新しい文書を追加する時に置き場所を判断できる
- local current を持たない shelf の場合、その理由と downstream current 正本が明示されている
- daily current 自体を持たない project の場合、その不在が入口で明示されている
- bundle declaration surface と continue check surface が明示されている
- close 済み bundle と residual bundle が混ざらない
