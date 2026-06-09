# ゴール・道のり・チェックポイント・タスク・設計

**目的**: 作業を始める前に、何をどう決めるかを 1 本で読むための共通文書。

## 1. 使い方

この順で読む。

1. `ゴール`
2. `道のり`
3. `チェックポイント`
4. `タスク`
5. `設計`

`設計` から先に読まない。

## 2. 5つの意味

### 2.1 ゴール

今から行うことのゴールを決める。

最低限、次を言えること。

- 何が完成状態か
- 何が今回の範囲か
- 何が今回の範囲外か
- 何が残っていれば未達か
- この作業で終わることは何か
- この作業で終わらないことは何か
- 完了報告の主語は何か

### 2.2 道のり

ゴールまでの道のりを明確にする。

最低限、次を言えること。

- 今の状態からどの順で進むか
- どこで止まるか
- どの段がどの前段に依存するか

### 2.3 チェックポイント

ゴールまでの道のりで通るべきチェックポイントを明らかにする。

最低限、次を言えること。

- どのチェックポイントがあるか
- どの順で通るか
- 各チェックポイントが何のズレを防ぐか
- 通過前に何が必要か
- 通過後に何が成立するか

### 2.4 タスク

各チェックポイントを通すための作業単位に落とす。

最低限、次を言えること。

- どのタスクがどのチェックポイントに属するか
- そのタスクが本当に必要か
- 抜け漏れがないか
- 順番が正しいか

### 2.5 設計

各タスクごとに、何を読み、何を書き、何をしたら完了かを決めてから実行する。

最低限、次を言えること。

- 着手条件
- 読むもの
- 書くもの
- 触ってはいけない場所
- やること
- 完了条件
- 失敗条件
- 停止条件
- 証拠
- 記録先
- 最終判定者

詳しい必須項目は `../policies/execution-readiness-gate-policy.md` を読む。

## 3. つながり

5つは次の順でつながる。

- `ゴール` が決まる
- `道のり` が決まる
- `チェックポイント` が決まる
- `タスク` が決まる
- `設計` が決まる

どこか 1 つでも切れているなら未完了。

## 4. 実行前に固定すること

少なくとも次を先に決める。

- 今回どこまで進めるか
- 今回どこで完了と切るか
- 今回やらないことは何か
- 足りないものがあるなら blocker として明記されているか

## 5. 入口文書に必要なこと

この考え方を使う文書群では、入口文書に次を書く。

- どのファイルが `ゴール` か
- どのファイルが `道のり` か
- どのファイルが `チェックポイント` か
- どのファイルが `タスク` か
- どのファイルが `設計` か
- その順で読むこと

## 6. 次に読むもの

- 着手前確認:
  - [../policies/execution-readiness-gate-policy.md](../policies/execution-readiness-gate-policy.md)

<a id="requirements-to-design-workflow"></a>
## 7. Requirements から Design への流れ

request を implementation-ready な作業へ落とす時は、少なくとも次の順に進める。

```text
request
  -> requirements
  -> basic design
  -> detailed design
  -> task breakdown
  -> traceability matrix
  -> quality gate
  -> implementation cycle
```

各段で最低限確認すること:

- requirements
  - purpose / scope / functional / non-functional / assumptions / risks がある
- basic design
  - boundary / major components / data / interfaces / rejected choice がある
- detailed design
  - contract / validation / error / state / test condition が具体化されている
- task breakdown
  - one clear outcome
  - target files
  - dependency
  - acceptance criteria
  - verification method
- traceability
  - requirement と design と task と evidence がつながる

<a id="task-splitting-methodology"></a>
## 8. Task 分割方法

task 分割では、design document を task の数だけ物理分割しない。  
design は一体のまま保ち、task 側に precise reference を持たせる。

原則:

- 可能な限り vertical slice を使う
- horizontal slice は shared foundation / migration / infrastructure / explicit refactor の時だけにする
- size が読めない時は短い spike を先に作る

review trigger:

| Signal | Suggested Limit | 超過時 |
|---|---:|---|
| referenced design docs | 3 | split または scope clarify |
| implementation files | 5 | capability または component で split |
| single-file estimated size | 200 lines | component または helper を split |
| dependencies | 3 blockers | sequencing を見直す |

各 task に最低限含めるもの:

- referenced design sections
- dependencies and blockers
- target files/components
- acceptance criteria
- test / evidence mapping
- explicit out-of-scope items
