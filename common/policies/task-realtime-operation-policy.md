# Task Realtime Operation Policy

## Purpose

AI が task をリアルタイムで管理できる状態を、repo canonical 上で再現可能な運用ルールとして定義する。
この policy が扱う「リアルタイム」は、秒単位の自動同期ではなく、**task state を変えた同じ作業ターンの中で canonical task state まで閉じること**を意味する。

## 1. Core Rule

- task state mutation と canonical task update は分離しない
- task state を変えたら、その same turn で canonical task state も更新する
- 「後でまとめて task を直す」は許可しない
- AI の頭の中だけで current state を保持しない
- task mutation の前に、その mutation を支える spec / scope / blocker の checkpoint を `fixed / unknown / blocked / non-goal` で明示する
- task mutation の前に `active bundle id` と `active bundle type` を固定する
- close 済み bundle の residual を続ける時は、新しい bundle id を立てる

## 2. Canonical Targets

project が current task register を採用している場合、task mutation 時の canonical target は次の順で扱う。

1. item state record
2. current task register
3. overview hub
4. execution board
5. backlog catalog
6. external mirror

canonical target には、最低限次を同ターンで残せる必要がある。

- `active bundle id`
- `active bundle type`
- `success subject`
- `current position`
- `next action`
- `stop reason if any`
- `writeback target`

この policy は `current task register を採用する project` ではそのまま使う。
採用しない project では、次の読み替えを置く。

- `current task register`
  - その project の `current canonical`
- `overview hub`
  - その project の current summary 面
- `execution board`
  - その project の active execution 面

つまり、この policy の主語は `task 状態変更と current 正本の同ターン書き戻し` であり、
特定ファイル名の採用を強制するものではない。

`external mirror` は optional であり、使う場合でも canonical 更新の後に従う。

### 2.1 Canonical と mirror の原則

- task 状態の正本は repo 内に 1 つだけ置く
- external board や tracker は mirror であり、正本の理解を置き換えない
- 日々の「今の task」は current task register から読む
- overview と execution は projection であり、日々の主操作面ではない
- mirror の再構築は canonical 更新の後に従う

## 3. Mutation Events

task state mutation とみなす event:

- new current parent を作る
- backlog item を current parent に昇格する
- new branch task を作る
- new human decision を作る
- branch task を `MERGED` にする
- branch task を `BLOCKED` / `ARCHIVED` にする
- decision を解決して `ARCHIVED` にする
- parent を `ACTIVE / HUMAN_DECISION / BLOCKED / DORMANT / DONE / ARCHIVED` に変える
- next action / next return point / needs_human を変える

次は mutation に含めない:

- typo fix のみ
- wording cleanup のみ
- report-only inventory

## 4. Required Update Set

### 4.1 Item state record

最初に更新するもの:

- project-local task item shelf

最低限そろえる field:

- `status`
- `parent`
- `route`
- `needs_human`
- `branch`
- `pr`
- `next_action`
- `next_return_point`
- `decision_note`

### 4.2 Current task register

project が current task register を持つ場合:

- mutation 後の current row set を同じ change set で更新する
- row の追加 / 削除 / bucket 移動 / zero-count bucket を同期する
- current から外れた task を register に残さない

### 4.3 Overview hub

次の場合に overview を更新する:

- active parent が変わる
- dormant parent が変わる
- blocked parent が変わる
- human decision summary が変わる
- recent merged summary が変わる
- parent の next action / next return point が変わる

### 4.4 Execution board

次の場合に execution board を更新する:

- active branch task が増減する
- unresolved decision が増減する
- recent merged row が増減する
- active parent の next action が変わる

### 4.5 Backlog catalog

backlog catalog を更新するのは次の場合だけ:

- backlog item 自体を追加 / 昇格 / 完了 / 削除 / 置換する

current execution だけの変化で backlog catalog を current board 代わりに使わない。

## 5. Operation Order

task mutation の標準順序:

1. spec checkpoint と precondition を確認する
2. item state record を更新する
3. current task register を更新する
4. overview hub / execution board を必要な範囲で更新する
5. backlog catalog を必要な場合だけ更新する
6. verify を実行する
7. external mirror を使う場合だけ sync する

順序を逆転させない。

## 6. Event-by-Event Rule

### 6.1 Backlog -> Parent 昇格

- `parent-task` item を作る
- current task register に `active-parent` row を追加する
- overview hub に active parent を追加する
- execution board に active parent を追加する

### 6.2 Parent -> Branch 開始

- `branch-task` item を `PLANNED` または `IN_PROGRESS` で作る
- current task register に `active-branch-task` row を追加する
- execution board に active branch row を追加する
- parent item の `active_branch_count` を更新する

### 6.3 Human Decision 発生

- `decision` item を作る
- current task register に `open-decision` row を追加する
- execution board に active decision row を追加する
- parent item の `open_decision_count` を更新する
- parent item の status は `HUMAN_DECISION` または `BLOCKED` のどちらか一方にする

### 6.4 Branch Merge

- source `branch-task` を `MERGED` または `ARCHIVED` に移す
- `merged-record` item を current reroute context として追加する
- current task register から active branch row を外す
- current task register に `recent-merged` row を追加する
- execution board から active branch row を外し、recent merged に追加する
- parent item の `active_branch_count` を更新する

### 6.5 Decision Resolution

- `decision` item を `ARCHIVED` にする
- current task register から open decision row を外す
- execution board から active decision row を外す
- parent item の `open_decision_count` を更新する

### 6.6 Parent Close / Reroute

- child 0 / unresolved decision 0 / reroute pending 0 の条件を満たしたら `DONE` 候補にできる
- close しない場合は `next_action` と `next_return_point` を次の parent work に更新する
- close した場合は current task register から current row を外す

## 7. Verification Rule

mutation のたびに最低限確認すること:

- mutation の根拠になった `fixed / unknown / blocked / non-goal` が current state と矛盾していない
- current task register と item state record の row set が一致している
- current に出るべき item が漏れていない
- current から外れるべき archived item が残っていない
- parent / branch / decision / merged の parent 関係が壊れていない
- zero-count bucket の表現が current state と一致している

verify を通さずに mirror sync しない。

## 8. Handoff Rule

別の AI に引き継ぐときは、最低限次を repo に残す。

- active bundle id
- active bundle type
- current task register
- 変更した item file
- overview / execution の同期結果
- unresolved decision の有無
- next action
- next return point

新しい AI は次の順で読む。

1. current task register
2. item file
3. execution board
4. overview hub
5. backlog catalog

## 9. Route And Priority

### 9.1 route は canonical target で決める

利用する route:

- `github-pr`
- `replica`
- `db`
- `planning-only`

1 task には 1 primary route を持たせる。

### 9.2 route selection

- `db`
  - canonical target が database / queue / ledger / persistent state
- `replica`
  - protected source に直接書かず、replica 上で差分を作り owner promotion する
- `github-pr`
  - code / docs / config の canonical file を branch -> PR -> CI -> merge で更新する
- `planning-only`
  - output が plan / memo / packet / inventory / classification に留まり、canonical state mutation を含まない

複数 route に見える時は次で決める。

1. canonical target が DB / persistent state なら `db`
2. protected source に対する owner promotion なら `replica`
3. repo canonical file を review 経由で更新するなら `github-pr`
4. 実装変更がなく packet / plan だけなら `planning-only`

### 9.3 active parent priority

複数 active parent があるときの優先順位:

1. unresolved `needs_human=yes` を持つ parent
2. active branch-local task を持つ parent
3. blocked item を解消できる parent
4. close 直前で current execution から片付けられる parent
5. 上位 goal への波及が大きい parent

同時 active parent は原則 2 件までに抑える。

### 9.4 branch completion 後の reroute

1. その branch の direct parent
2. その parent の close 可否確認
3. close しないなら parent の次 branch / decision / blocker を選ぶ
4. close するなら overview 上の次 priority parent に戻る

current execution からの戻り順は固定する。

1. execution item
2. direct parent
3. overview
4. backlog catalog

branch completion 自体は task completion ではない。

## 10. Keep / Avoid

keep:

- mutation と canonical update を同じターンで閉じる
- current task register を current-state read surface にする
- item -> register -> overview/execution -> verify の順を守る

avoid:

- state change 後に task docs を後回しにする
- backlog catalog を current task board 代わりに使う
- external tracker だけ更新して canonical を後回しにする
- AI の記憶だけで current state を運用する
