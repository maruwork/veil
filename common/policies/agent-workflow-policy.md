# Agent Workflow ポリシー

**目的**: agent-assisted development work を、調査から実装・検証・引き継ぎまで一貫して進めるための portable workflow を定義する。
このポリシーは、作業の流れだけでなく、設計者と作業者の境界、branch 完了後の再ルーティング、停止すべき場面の扱いも含めて定義する。

この policy は
`../frameworks/project-progression-rule.md`
のうち、主に

- `次の 1 手の選定`
- `限定実行`
- `停止条件`
- `継続か終了かの判定`
- `未完了が見えている時に status 報告だけで終わらない`

を、agent の日常運用として具体化する。

## 1. 作業フェーズ

基本の流れは次の 7 段階とする。

1. `Investigate`
   - 関連ファイル、入力、データ、依存関係を読む
2. `Diagnose`
   - 問題、scope、影響、未確定事項を特定する
3. `Propose`
   - 実装方針、検証方法、次アクションを明示する
4. `Implement`
   - 決まった scope だけを変更する
5. `Verify`
   - lint、test、inventory、read-only check を行う
6. `Report`
   - 変更内容、検証結果、残課題、次アクションをまとめる
7. `Close`
   - acceptance criteria を満たしていれば閉じる。未達なら次タスクへ再ルーティングする

作業はできるだけこの順番で進める。ただし、小さな typo 修正や inventory-only 作業では、必要な段だけを短く通してよい。

## 1.5 着手前の標準判断順

新しい命令を受けたときは、着手前に次の 6 段で考える。

1. `分類`
   - 命令の種類を `実装 / 調査 / 再編 / 修正 / 確認` で切る
   - 作業の層を `基盤作成 / 日次運用 / 非本線` で切る
   - 判断の根拠状態を `未固定 / task化済み / ルール化済み` で切る
   - external tool / tracker / memory / helper を使うなら、`運用組込 / 作成補助` と `interface / mechanism / scaling` もここで切る
2. `現在位置`
   - current parent / branch / PT / dirty state / branch state を確認する
   - 既存 task の続きか、新しい workstream かを判定する
   - 依存関係、blocker、runtime / DB / route 前提を確認する
3. `進め方`
   - task 生成が必要かを判定する
   - 補助 planning surface が必要かを判定する
   - 補助 agent へ調査を委譲するかを判定する
4. `進行の基本3分割`
   - 作業を `調査 / 裁定 / 反映` に分ける
   - この 3 つを混ぜない
5. `実行と検証`
   - 実行する
   - 検証する
   - task / current を更新する
6. `継続か終了か`
   - 自然に続けられる次タスクがあるなら続ける
   - それが無いときだけ閉じる

補足:

- `連続実施可能タスクの可否` は最初に考えない
- `補助 planning surface` と `補助 agent への調査委譲` は毎回必須ではないが、毎回この位置で要否を判定する
- `task 生成` は必要な場合だけでよい。既存 task の続きなら増やさない
- `基盤作成 / 日次運用 / 非本線` の分類は、記憶ではなく毎回明示する
- `未固定 / task化済み / ルール化済み` の分類も、記憶ではなく毎回明示する
- external tool を持ち込む時は、対象 project 側で定義された導入 checklist / evaluation template / operator guide に従う

### 1.5.1 分類の意味

- `基盤作成`
  - DB / schema / tool / policy / task system / file topology / canonical docs を直接変える
- `日次運用`
  - manager 操作 / review / PR / handoff / daily workflow を助ける
- `非本線`
  - 今の本線や canonical に直結しない便利機能・周辺論点

境界が曖昧な場合は、`主分類` と `副作用先` を分けて示す。

- `未固定`
  - その場の文脈判断に強く依存し、policy / checklist / template / task / register に落ちていない
- `task化済み`
  - task / workplan / register には落ちているが、common policy / checklist / template までは届いていない
- `ルール化済み`
  - common policy / checklist / template、または project canonical rule に明示され、次セッションや他 agent でも再現しやすい

再発しそうな判断、引き継ぎで詰まりやすい判断、他プロジェクトへ移植したい判断は `ルール化済み` へ寄せる。

### 1.5.2 進行の基本3分割

作業が長引きやすいときは、次の 3 つを混ぜない。

1. `調査`
   - 本文を読む
   - 参照元と影響範囲を集める
   - ここでは最終判断しない
2. `裁定`
   - keep / archive / remove / reroute を決める
   - SSOT 更新判断、task state 判断、棚判断はここでだけ行う
3. `反映`
   - register / task / policy / checklist / file move を更新する

ルール:

- `調査` が終わる前に `裁定` しない
- `裁定` が終わる前に `反映` しない
- `補助 agent` に渡せるのは原則 `調査` まで
- `最終判断を持つ担当` は `裁定` と `反映` を持つ

要するに、`調査担当` と `最終判断担当` を分ける。これを崩すと、判断が早すぎるか、止まりすぎる。

### 1.6 着手前の対ユーザー明示

`補助 planning surface` と `補助 agent への調査委譲` を判定したら、**実際に着手する前にユーザーへ明示**する。

明示は、次のように **そのまま行動判断に使える文** で書く。

- `追加の planning surface は使います。<理由>` または `追加の planning surface は不要です。<理由>`
- `補助 agent へ調査を委譲します。<理由>` または `補助 agent への調査委譲は不要です。<理由>`

`補助 agent へ調査を委譲します` の場合は、続けて **依頼文または dispatch 条件をそのまま提示**する。

ルール:

- 単に「判定した」だけでは不十分
- user が次の操作を迷わない粒度で書く
- 作業開始メッセージの先頭で明示する

## 2. branch 完了は task 完了ではない

`branch`、`PR`、`patch` の完了だけでは `no task left` にしない。

次のいずれかが残っている場合は、親タスクへ再ルーティングする。

- 親 task の未完了項目
- 同じ goal に属する次の branch-local task
- 同じ dispatch の次アクション
- read-only で続けられる inventory / verification / classification

branch 完了時には、次を必ず明示する。

- 完了した branch-local scope
- 親 task の残件
- 次に進める branch-local action か read-only action

複数の active parent task がある場合の次親選択は [task-realtime-operation-policy.md](./task-realtime-operation-policy.md) の route / priority 章に従う。

## 3. Gate と停止判断

人間判断が必要な場面、または停止理由の整理は [execution-readiness-gate-policy.md](./execution-readiness-gate-policy.md) に従う。

このポリシーで重要なのは次の 2 点である。

- gate が propose と implement の間にある場合、判断前に branch-local で進められる作業が残っていないか確認する
- reversible な preflight、read-only inventory、局所的な additive documentation は、人間判断待ちでも先に進めてよい
- owner-owned dirty area がある場合の continuation route は [diff-ownership-and-wave-close-policy.md](./diff-ownership-and-wave-close-policy.md) に従う

追加ルール:

- `owner 判断が必要か = no` なのに user へ進行可否を聞いて止まってはいけない
- その場合は、current surface に `次に埋めること` と `継続できる範囲` を書き、続行する
- さらに `次に必ず編集するファイル` と `このターンで最低限埋める範囲` を書く
- この条件では `status報告だけで終了してはいけないか: yes` を明記する
- user へ戻すのは、owner-level choice が新しく発生したときだけにする

## 3.5 コードハーネス優先

agent-assisted work では、自然言語の頑張りより **コードハーネス資産** を増やすことを優先する。

優先順位:

1. 毎回の説明で回している手順を script / hook / test / checklist に落とせないか考える
2. recurring な前提や禁止事項を policy または project 側の明示ルール面に固定できないか考える
3. agent 間の受け渡しを会話だけでなく file / diff / log / queue に残せないか考える
4. 同じ問題が再発するなら prompt を長くする前に harness 資産の不足を疑う

このポリシーで言う `harness` は次の 3 層で読む。

- interface: tool call / command / structured operation
- mechanism: memory / control / verification / fail-close
- scaling: multi-agent coordination / handoff / queue

外部 tool / pattern を使う場合も、まずどの層を強くするのかを示す。運用組込か作成補助かの区分は `spec-review-and-skill-policy.md` と project 側 boundary principle に従う。

## 4. 設計者と作業者の境界

このポリシーでは、`設計者` と `作業者` を次のように分ける。

- `設計者`
  - 問題を圧縮する
  - scope を固定する
  - 入出力と完了条件を定義する
  - 禁止事項と非対象を明確にする
  - 参照すべき source of truth を絞る
- `作業者`
  - 固定済みの境界の中で、読取り、一覧化、変換、機械的編集、検証を進める
  - 新しい設計判断や棚決めを勝手に増やさない

### 4.1 設計者が先に固めるもの

作業者へ渡す前に、設計者はできるだけ次を固定する。

- 対象ファイルまたは対象 shelf
- 対象外ファイル
- 判断軸
- 出力形式
- verify 方法
- rename / archive / DB write / status update の可否

これが固まっていないうちは、まだ delegation する段階ではない。

### 4.2 作業者に渡してよい条件

次の条件を満たすとき、作業は作業者へ渡してよい。

- 読む範囲が狭い
- 判断軸が固定済み
- 出力形式が固定済み
- 変更対象が限定されている
- 戻り値を設計者が大きく再解釈しなくてよい

例:

- 参照元 inventory の抽出
- rename map の下書き
- fixed batch の copy/update 候補作成
- 限定されたファイル群の read-only classification

### 4.3 作業者へ渡してはいけない条件

次の条件があるときは、設計者が自分で持つ。

- root SSOT や canonical shelf の境界が未確定
- rename / archive / status 更新が絡む
- source shelf と target shelf の役割分担が未確定
- 禁止事項の説明が長くなる
- 結果を設計者が大きく組み替え直す前提になっている

例:

- どの棚を正本にするかの決定
- 大量 rename 前の方針決定
- archive 候補と current keep の線引き
- dynamic control と static docs の責務分離

## 5. delegation の経済条件

delegation は「できるから渡す」のではなく、「渡したほうが早いから渡す」ときだけ行う。

次を比較する。

- `準備コスト`
  - 前提説明
  - 禁止事項整理
  - 参照先列挙
  - 出力形式指定
  - review / 巻き戻しコスト
- `回収価値`
  - 作業量
  - 反復量
  - 機械性
  - 返却物の再利用性

ルール:

- `準備コスト >= 回収価値` なら delegation しない
- `準備コスト < 回収価値` のときだけ delegation する

言い換えると、依頼文が長くなる時点で、その作業はまだ設計者の手元に置くべき可能性が高い。

### 5.1 並列 dispatch の条件

外部 workflow pattern から取り込む場合でも、並列 dispatch は次を満たすときだけ使う。

- 問題が 2 件以上あり、原因領域が独立している
- shared state、同一 write set、強い順序依存がない
- 各作業単位を self-contained に説明できる
- 回収時に root owner が統合 review できる

運用ルール:

- 1 agent / 1 domain を原則とする
- prompt は scope、constraints、expected output を固定する
- 関連失敗を無理に分割しない
- dispatch 後は summary review と全体 verify を必ず行う

次の場合は並列化しない。

- 1 つの修正が他の failure を解消しうる
- 同じ file / module / schema を複数 agent が触る
- 全体状態を見ないと原因が分からない

### 5.2 小粒 execution unit

複数 step の実装や再編では、作業単位をできるだけ小さく切る。

- 1 unit = 1 明確な行動
- 可能なら数分で verify まで回せる粒度にする
- exact file path、expected outcome、verify 方法を持たせる

ただし、次には機械的に適用しない。

- trivial fix
- inventory-only / report-only work
- exploratory debugging の初動
- files が強く結合していて分割すると逆に理解しづらい場合

## 6. additive / reversible を優先する

設計が固まっていない段階では、次のような additive / reversible な作業を優先する。

- read-only inventory
- classification table
- verification
- portable copy の追加
- source を残したままの common 化
- note / register / packet の追加

逆に、次は慎重に扱う。

- in-place rename
- archive 移動
- canonical file の役割変更
- DB write
- root entry の意味変更

## 7. root cause を隠さない

問題が構造にある場合、単なる patch ではなく root cause を見にいく。

ただし root cause fix が大きい場合でも、いきなり全面変更しない。まずは次を行う。

- inventory
- scope の切り分け
- reversible な unblocker
- 次 PR 単位の設計

## 8. 報告フォーマット

作業の途中や完了時には、次を短く明示する。

- 今何を見ているか
- 何が確定したか
- 何が未確定か
- 次に進める action

人間判断が必要になった場合は、decision packet 形式に従う。

## 9. Project rule との関係

project entry file や local runbook は薄く保つ。
entry file の代表例を出す場合も、template 全体で半既定に見えないよう最小限に留める。
再利用可能な workflow rule は common policy shelf に置く。

project-specific enforcement details、protected paths、database gates、approval roles は、それぞれの project governance file に残す。
