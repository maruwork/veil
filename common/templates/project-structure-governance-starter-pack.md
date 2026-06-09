# Project Structure Governance Starter Pack

**使う場面**: project の file / folder 構成を最初に整え、配置の崩れを防ぐ枠組みを入れる時に使う。  
**差し替える所**: 採用する棚構成、AI が触れる範囲、人の最終判断点、導入順。  
**書かないこと**: 個別 project の daily current 運用、各棚の全文 rule、repo 固有の履歴事情。 

> **用途**:
> file / folder 構成整理から切り出した、他 project に移植できる最小構成セット。
> repo が成長するにつれて配置が崩れやすい project に最初に入れる。

> **reading note**:
> project 構造整理を別 project に持ち込む時は、まず
> `project-progression-rule.md`
> と
> `project-progression-rule-integration-audit.md`
> を読み、その後にこの 1 本を読む。
> template 一覧や個別 rule を先に横断しない。
> ここで pack 全体像、導入順、AI が自動でできる範囲、人が最終判断する範囲を決めてから各 template に降りる。
> 具体的な整理手順は本書の cleanup procedure 章で読む。
> 配置表は `project-file-taxonomy-template.md` で読む。

ただし、この pack 自体が最上位進行ルールではない。
開始前に
`../frameworks/project-progression-rule.md`
と
`../frameworks/project-progression-rule-integration-audit.md`
を読み、
その後に構造整理という局所面へ降りる前提で使う。

## 0. 最初に見ること

この pack を使う時は、reading note にある次の 5 点だけ先に押さえる。

1. 何のために構造整理を入れるか
2. どの雛形を使うか
3. どこが AI だけで進められる所か
4. どこが人の最終判断になるか
5. 他 project に持ち込む時に何を差し替えるか

## 0.5 先に差し替えるもの

他 project に持ち込む時は、次をその project 用に差し替える。

- 入口ファイルの path
- 棚名
- workspace / archive / generated の置き場
- 今の状態を見るファイル名
- project 固有の command 名や rule 名

加えて、次の template 分岐条件も先に決める。

- `current ownership`
- `restart aid`
- `publication mode`
- `structure weight`
- `runtime placement`

## 1. この pack で防ぐこと

この pack は次の崩れを防ぐ。

- file の置き場が毎回 ad hoc に決まる
- 今の正本と generated output が混ざる
- 今の状態の正本と補助文書が混ざる
- docs / design / history / scratch の境界が曖昧なまま増殖する
- legacy path が残っているのに見た目だけ rename / move して壊す
- project 固有の file が共通資産と混ざる

## 2. 最低限使う雛形

次の 4 つを project 用に起こす。

| file | role |
|---|---|
| 本書の cleanup procedure 章 | 整理手順 |
| [project-file-taxonomy-template.md](./project-file-taxonomy-template.md) | 配置表 |
| [project-boundary-register-template.md](./project-boundary-register-template.md) | 境界登録表 |
| [project-workspace-and-artifact-policy-template.md](./project-workspace-and-artifact-policy-template.md) | workspace / generated / archive の方針 |

加えて共通 rule として次を読む。

- `../policies/file-operation-policy.md`
- `../policies/naming-and-shelf-policy.md`

上の path は、この repository 構造で使う時の例である。
他 project へ移植する時は、同じ役割を持つ project 側の path へ差し替えてよい。

### 2.1 読む順番

この pack を採用する project では、次を正式な読む順番とする。

1. `project-progression-rule.md`
2. `project-progression-rule-integration-audit.md`
3. 本書
4. 本書の cleanup procedure 章
5. `project-file-taxonomy-template.md`
6. `project-boundary-register-template.md`
7. `project-workspace-and-artifact-policy-template.md`

この読む順は、単なる推奨順ではなく、

- `goal`
- `path`
- `checkpoint`
- `task`
- `design`

の 5 層を読むための正式な順として扱う。

したがって project 側では、

1. どのファイルが `goal` か
2. どのファイルが `path` か
3. どのファイルが `checkpoint` か
4. どのファイルが `task` か
5. どのファイルが `design` か

を入口文書に明記する。

5層が存在していても、

- 対応ファイルが書かれていない
- 読み順が書かれていない
- 下位層から先に読み始められる

なら、構造整理の基準としては未整備とみなす。

project ごとの入口ファイルから見ても、
- 「どの file をどこに置くか」
- 「どの棚が今の正本か」
- 「workspace / archive / generated をどう分けるか」
- 「cleanup をどこで止めずに閉じるか」

の 4 点に、最短で戻れるようにする。

### 2.2 追加で読むもの

他者へ導入作業を渡す時は、次も読む。

1. `project-template-adoption-packet-template.md`
2. `../policies/project-template-adoption-completion-policy.md`

## 3. 導入順

1. entry file を決める
2. file taxonomy を埋める
3. boundary register を埋める
4. workspace / artifact policy を埋める
5. cleanup procedure を埋める
6. 今ある repo を taxonomy と register に照らして棚卸しする
7. hidden active assets / placeholder shelves / runtime residue を抽出する
8. rename / move 候補を別に出す

## 3.2 導入パターン

すべての project に最初から重い構成を入れる必要はない。
最低限、次の 3 パターンで始める。

### 軽量

- `project-file-taxonomy-template.md`
- `project-workspace-and-artifact-policy-template.md`

向いている project:
- 小さい web site
- file 数が少ない
- docs / generated / archive がまだ薄い

### 標準

- `project-file-taxonomy-template.md`
- `project-boundary-register-template.md`
- `project-workspace-and-artifact-policy-template.md`
- 本書の cleanup procedure 章

向いている project:
- 今の正本と補助文書が増え始めている
- AI / generated output が出る
- cleanup を後回しにしたくない

### 拡張

- 標準一式
- project ごとに必要な template / guide / register

向いている project:
- docs / tasks / runtime / archive の棚が増えている
- hidden active assets や legacy path がある
- 複数 agent / 複数 workspace が絡む

通常の web site は、まず `軽量` か `標準` から始める。

## 3.5 English Label Rule

他 project に移植する時も、英語ラベルは**語の意味だけでなく種別**を分かる形で書く。

最低ルール:

1. 単なる説明語なら、日本語またはカタカナで書く
2. 固定値なら、`status 値` / `verdict 値` / `field 値` のように種別を添える
3. 変数名・field 名なら、``backticks`` で囲み、`変数名` または `field 名` だと明示する
4. command / option / policy 名なら、その種別を添える
5. 本文は意味を先に書き、必要なら後ろに原文を添える

この rule の目的は翻訳ではない。
**operator や後続 AI が、英語ラベルを見た時に「説明語 / 固定値 / 変数名 / command 名」のどれかを迷わないようにすること**である。

## 4. この pack で固定されること

この pack を入れた project は最低限、次を答えられるようになる。

- file type ごとの置き場
- 今の正本と補助面の境界
- 入口 / generated / archive / temporary の分離
- hidden active asset / placeholder shelf / residue の扱い
- 英語ラベルの種別の読み分け
- local current を自棚に持つか、downstream 側へ持たせるか
- restart aid を持つか、持たないか
- runtime 実体を local で持つか、downstream 側に寄せるか

## 4.5 AI が自動で進められること

この pack を渡された AI は、少なくとも次までは自動で進められる。

- taxonomy の初稿を作る
- boundary register の初稿を作る
- workspace / generated / archive policy の初稿を作る
- 今ある repo の file / shelf inventory を出す
- hidden active assets / placeholder shelf / runtime residue の候補を列挙する
- 今の正本 / 補助 / generated / historical の仮分類を出す
- safe rename / move candidate を separate list に出す

## 4.6 人が最終判断すること

この pack があっても、次は人が最終判断する。

- 今の正本と historical の最終線引き
- archive / restore / delete の最終判断
- hidden active asset を残すか正本化するか
- external / foreign / pre-existing 変更を今の branch に残すか
- DB / CI / caller / runtime 影響がある rename / move / delete
- experiment / sample / scratch を今の mainline に混ぜるか

つまり、この pack は **完全自動整理** の約束ではない。
**初期整理を AI に寄せ、最後の disposition だけ人に止める**ための pack である。

## 5. やらないこと

- repo 全体の自動 enforcement 実装そのもの
- DB-backed allowlist や SSOT guard の移植
- source-project 固有の棚名のコピー
- 人の最終判断が必要な destructive action の自動決定

## 5.5 止まる条件

AI は次の時、整理を止めて人の判断に戻す。

- 今の正本か historical かを file 単位で断定できない
- delete / archive / restore のいずれかで、caller 影響が読めない
- generated artifact に見えるが今も呼ばれている
- hidden active asset を見つけたが、manifest / entry 導線がない
- experiment lane と production/mainline lane が同じ branch に混ざっている

「まだ整理できる file がある」ことと、
「人の判断が必要な decision が残っている」ことを混同しない。

## 6. 完了条件

この pack の導入は、次の条件を満たして初めて完了とみなす。

- placement matrix が埋まっている
- boundary register が 今の正本 / 補助 / generated / historical を区別している
- 最初に見る入口が最小面として明示されている
- workspace / archive / generated output の置き場が宣言されている
- cleanup procedure があり、end-to-end close 条件が書かれている
- entry file が上記 3 面と矛盾していない
- 今ある repo 上の主要棚が「未分類」のまま残っていない
- gitignore / hidden path に現役 asset がある場合、repo-visible な manifest または entry 導線がある
- placeholder shelf は `reserved-empty` として register 済みで、ad hoc write 禁止が明記されているか、削除されている

## 7. Cleanup Procedure

### 7.1 棚の種類

| 区分 | 意味 |
|---|---|
| `current canonical` | 今の判断に直接使う正本 |
| `front current surface` | 今の状態を見る時に最初に開く最小面 |
| `support` | 正本を補助するが、それ自体は正本ではない |
| `visible support` | 目立つ補助文書。今の進行の代わりにはしない |
| `generated` | 機械生成や実行結果。自動では正本にしない |
| `historical` | 履歴保管。今の判断元ではない |
| `external` | repo 外または外部にある正本 |
| `reserved-empty` | 将来用の空棚。思いつきで書き込まない |

### 7.2 workspace と生成物の基本ルール

- active workspace は 1 つに寄せる
- generated output は canonical shelf と混ぜない
- archive と active workspace を混ぜない
- workspace を permanent storage にしない
- generated artifact は review と placement decision を通すまで canonical にしない
- 見えにくい現役 file は manifest や入口案内なしに残さない
- 実行後の残り物は未分類のまま残さない
- visible support document は current progress の前面に出さない

### 7.3 洗い出し順

1. root files
2. current canonical shelves
3. generated / workspace shelves
4. archive / historical shelves
5. 見えにくい現役 file や ignore された現役 file
6. 実行後や agent 作業後の残り物
7. 空棚や将来用にだけ残している棚
8. file picker / docs root で目立つ補助文書

### 7.4 Mandatory Checks

- gitignore / hidden path に現役 tool / script / generator があるか
- root に misplaced generated artifact が残っていないか
- 空棚が正体不明の置き場になっていないか
- `.claude/`, `.cache/`, runtime worktree, browser state などの残り物が残っていないか
- visible support document が current progress / completion claim を独自に持っていないか

### 7.5 Cleanup Actions

- hidden / ignored path に現役 asset がある場合:
  - repo-visible manifest を作る
  - entry file から導線を張る
  - canonical 化するなら shelf を決めて昇格する
- 空棚を残す場合:
  - boundary register で `reserved-empty` と明記する
  - authority なし
  - ad hoc write 禁止
- 実行後や agent 作業後の残り物は、削除 / 退避か support/generated 残置のどちらかに必ず振り分ける
- visible support document を残す場合:
  - 非正本注記を書く
  - current の戻り先を entry file と current task surface に固定する

### 7.6 分割してよい条件

- 同じ構造整理 objective に属する作業は、原則 1 回で end-to-end に閉じる
- `first wave / second wave` に分けてよいのは次の場合だけ:
  - 呼び出し元への影響がある
  - 古い参照を一時的に残す必要がある
  - 担当者の境界が異なる
  - destructive action に別承認が必要

### 7.7 Completion Checklist

- root misplaced artifact が整理済み
- docs family が所定 shelf に入っている
- generated output shelf が固定されている
- archive が active shelf と混ざっていない
- hidden active assets に manifest / entry 導線がある
- placeholder shelf が `reserved-empty` として固定済み、または削除済み
- runtime residue の扱いが決まっている
- front current surface が最小セットで決まっている
- visible support document に残留条件 / current への戻り先がある
- AI worktree / runtime residue が cleanup scope 外なら、その理由と owner が書かれている
- visible support document がある場合、非正本注記・今の状態への戻り先・降格条件が書かれている

## 6.5 終了状態

この pack を使った整理の着地は、次の 3 つに分ける。

1. `structure aligned`
   - taxonomy / boundary / workspace policy / cleanup procedure が揃った
   - 今の棚の大分類が終わった
2. `owner judgment pending`
   - structure は揃ったが、archive / canonical / foreign / sample lane の判断が残る
3. `cleanup closed`
   - 人の最終判断まで終わり、今の branch に残すもの / 外すものが確定した

project によっては、AI の担当範囲は `structure aligned` または `owner judgment pending` までで十分である。

## 7. Why This Exists

file / folder 構成を整理した目的は、特定の 1 repo だけを綺麗にすることではない。

本来の目的は、

- project が大きくなっても崩れにくい構造規律を作ること
- その規律を共通棚や handoff packet と同じように他 repo へ持ち出せること

にある。

この starter pack はその切り出し版である。

## 8. 最短手順

新しい project へ最短で入れる時は、まず次だけやればよい。

1. パターンを `軽量 / 標準 / 拡張` から選ぶ
2. entry file を 1 本決める
3. taxonomy を埋める
4. workspace / generated / archive を宣言する
5. 今ある repo を inventory する
6. AI に仮分類させる
7. 人の最終判断が必要な残件だけ分ける

この shortcut で、template pack・placement rule・boundary rule・cleanup procedure を別々に説明し直さずに済む。
