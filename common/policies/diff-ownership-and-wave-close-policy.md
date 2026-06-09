# Diff Ownership and Wave Close Policy

**目的**: dirty working tree を場当たり的に片付けるのではなく、差分が未所属のまま積み上がること自体を防ぐ portable rule を定義する。

この policy は
`../frameworks/project-progression-rule.md`
のうち、主に

- `次の 1 手だけを bounded に進める`
- `局所進捗を前進と数えない`
- `止まる時は止まる`
- `未知の差分を残したまま次へ進まない`

を、diff ownership と wave close の文脈で具体化する。

この policy は、ゼロベースで新しい wave を開くときに

- どこまでを mainline に載せるか
- どの差分を residual / monitor / generated follow-up に分けるか
- いつ wave を閉じて次へ進めるか

を固定するために使う。

## 1. 用語

- `wave`
  - repo 内で完了可能な 1 本の execution unit
- `finish line`
  - その wave が到達すべき close 条件
- `mainline`
  - 今回の wave で実際に閉じる対象
- `monitor residual`
  - trigger が出るまで reopen しない監視残差
- `repo-external residual`
  - repo 外 operator action や外部依存のため、この repo 内では完了できない残差
- `generated follow-up`
  - canonical source の変更に追随する index / inventory / generated artifact の更新束
- `scratch`
  - 未確定の下読み、候補、実験、一次出力
- `unknown diff`
  - 上のどれにも所属していない差分

## 2. 原則

### 2.1 One Wave, One Finish Line

- 1 つの wave には、repo 内で完了可能な束しか載せない。
- repo 外依存、人手判断待ち、外部 caller 実装、deploy 作業は最初から `repo-external residual` に分ける。
- finish line が言えない wave は開かない。

### 2.2 Register First, Action Second

- archive / reroute / restore / shelf move は、先に row 化してから実行する。
- 最低限、次を先に固定する。
  - `caller / reference reality`
  - `reroute target`
  - `blast radius`
- 影響範囲未確認のまま archive keep / restore / reroute を確定しない。

### 2.3 Unknown Diff = 0

- すべての差分は次のいずれかに所属していなければならない。
  - `mainline`
  - `monitor residual`
  - `repo-external residual`
  - `generated follow-up`
  - `scratch`
- `unknown diff` が残った状態で新しい wave を開かない。

### 2.4 Wave Close Before Next Wave

- 次の大きい wave を開く前に、前 wave は次まで閉じる。
  - canonical reflection 完了
  - residual separation 完了
  - `unknown diff = 0`
- 前 wave を閉じずに次 wave を重ねない。

### 2.5 Generated Follows Canonical

- `index`、inventory、mirror、generated note は canonical source と同じ束に混ぜない。
- まず canonical を閉じ、その後に `generated follow-up` として追随させる。
- generated file を generator を通さず手修正する場合は、例外理由を明示する。

### 2.6 Workspace Quarantine

- 未確定の下読み、候補、scratch output は `workspace/` に置く。
- canonical shelf に未確定物を直接置かない。
- scratch を昇格させるときは、配置判断と current reflection を通す。

### 2.7 Archive Is Not Disposal

- archive は「削除代替の終点」ではなく historical holding shelf である。
- archive keep も restore も、row 単位で再説明できなければ確定扱いにしない。
- `archive/archive/...` のような多重 archive は作らない。

## 3. Wave を開く前の必須確認

新しい wave を開く前に、少なくとも次を確認する。

1. `finish line`
   - repo 内で完了できるか
2. `scope`
   - cluster / task / register row 単位で閉じられるか
3. `residual split`
   - repo 外依存を最初から mainline から外しているか
4. `diff ownership`
   - 既存差分に `unknown diff` がないか
5. `generated impact`
   - index / inventory / mirror の follow-up が別束として切れているか

どれか 1 つでも曖昧なら、wave を小さく切り直す。

## 4. Wave Close Criteria

wave は次を満たしたときだけ closed 扱いにしてよい。

- finish line に含めた row / cluster / task が完了している
- canonical docs / task / register / handoff が一致している
- reopen 条件が必要なら monitor residual として明示されている
- repo 外でしか進められないものは repo-external residual として分離されている
- `unknown diff = 0`

## 5. 止める条件と切り分け

次が出た場合、その場で broad に抱え込まず切り分ける。

- repo 外 operator action が必要
  - `repo-external residual` に送る
- code / runtime / projection 変更が必要な restore が出た
  - reopen decision だけ current canon に反映し、実装は別 wave に分ける
- cluster が大きすぎて single row では粗い
  - subcluster row に分割して続行する
- generated follow-up が必要
  - canonical close 後の follow-up wave に分ける

## 6. 禁止

- `unknown diff` を残したまま次の wave を開く
- repo 外 residual を mainline に混ぜる
- archive / reroute / restore を row 無しで先に進める
- generated follow-up を canonical source diff と混ぜて close 判定する
- `workspace/` に置くべき未確定物を canonical shelf に置く
- 「clean worktree に見せること」を優先して ownership の無い差分処理を行う

## 7. Report で必ず明示すること

wave を閉じるときは、少なくとも次を report する。

- 今回の finish line
- 完了した mainline
- monitor residual
- repo-external residual
- generated follow-up の有無
- `unknown diff = 0` を満たしたか

## 8. owner-owned dirty area の扱い

- 持ち主が編集中の未確定領域は、AI が勝手に整理対象や上書き対象にしない。
- 優先順位は次のとおり。
  1. 持ち主の未確定変更を守る
  2. 独立に進められる作業を続ける
  3. どうしても必要なら対象ファイルを示して取り込み判断を返す
- まず読み取りだけで続けられないかを確認する。
- 未確定領域と独立した file 群があるなら、そこだけ進める。
- 未確定領域を避けて clean worktree で続ける場合も、持ち主の未コミット変更を見えないまま上書きしない。
- 未確定領域を理由に、読み取りや独立経路で続けられる作業まで止めない。

## 9. 関連

- [agent-workflow-policy.md](./agent-workflow-policy.md)
- [file-operation-policy.md](./file-operation-policy.md)
