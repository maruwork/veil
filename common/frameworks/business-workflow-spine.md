# Business Workflow Spine

**目的**: ドメインが変わっても崩れない、業務ワークフローの機能軸を portable な形で定義する。
**位置づけ**: これは project-local role 名や status 名ではなく、`仕事をどう流すか` の共通 spine である。

## 1. 何を固定するか

ドメインが変わっても、業務ワークフローの核は次の 4 段から大きくは変わらない。

1. `設計`
2. `事前監査`
3. `実行`
4. `事後監査`

製品開発でも、品質管理でも、法務レビューでも、
流れる task の中身は変わるが、この機能軸はほぼ同じである。

## 2. 4 段の意味

### 2.1 設計

ここで固定するのは、`何をやるか` と `どこまでやれば完了か` である。

- 対象
- スコープ
- 完了条件
- 禁止事項
- 必要証跡
- 次段へ渡す条件

設計の役割は、実行者の自由度を無限にすることではない。
`実行可能な単位へ仕事を落とし、後段が監査できる形にすること` である。

### 2.2 事前監査

ここで固定するのは、`この task をそのまま進めてよいか` である。

- 設計が十分か
- 必要承認があるか
- リスク分類は妥当か
- 実行者に渡してよい粒度か
- Human Gate が必要か

事前監査は、実行後のダメ出しではない。
`間違った task を正しく実行してしまう事故` を防ぐ役割を持つ。

### 2.3 実行

ここで固定するのは、`設計と承認に従って実際に進めること` である。

- 実作業
- 中間生成物
- self-check
- テスト / 測定
- 証跡の束線

実行は「やった」だけでは閉じない。
後段が検証できる artifact を残して初めて work として成立する。

### 2.4 事後監査

ここで固定するのは、`本当に完了と言ってよいか` である。

- 完了条件を満たしたか
- 必要証跡が揃っているか
- 差し戻すべきか
- 再設計が必要か
- close claim できるか

事後監査は、単なる品質確認ではない。
`close / reroute / reopen / human judgment` を決める最終判定面である。

## 3. なぜ 4 段で切るか

この 4 段で切る理由は、役割名や業界用語に依存しないからである。

- ソフトウェア開発:
  - 設計 → 設計審査 → 実装 → 実装監査
- 品質管理:
  - 検査設計 → 検査計画レビュー → 検査実施 → 結果監査
- 業務改善:
  - 改善案設計 → 実施承認 → 実施 → 効果監査

つまり変わるのは `task の内容` であり、
変わりにくいのは `設計されたものを監査し、実行し、結果を再監査する` という spine である。

## 4. 最小 packet contract

この spine を運用に落とすなら、最低限次の packet が必要になる。

| packet | 役割 |
|---|---|
| `design packet` | 何をやるか、完了条件は何かを渡す |
| `pre-execution audit packet` | 実行してよいか、何が gate かを返す |
| `execution evidence packet` | 実行結果と証跡を束ねる |
| `post-execution verdict packet` | close / revision / redesign / escalate を返す |
| `resume packet` | 停止時の next action / next actor / resume condition を返す |

## 5. 停止の原則

この spine では、停止は default ではない。

- default は `進む`
- 止めるのは gate がある時だけ
- 止めたら `誰が / 何を / どの条件で再開するか` を返す

したがって、workflow の質は

- 正しく止められるか
- 不要に止めないか
- 止めた後に自然に再開できるか

の 3 点で評価する。

## 6. role 名との分離

この framework は role 名を固定しない。

role は project / domain ごとに local に割り当てる。

例:

| spine role | 典型的な役割 |
|---|---|
| `設計` | designer / planner / analyst |
| `事前監査` | reviewer / approver / gate owner |
| `実行` | implementer / operator / examiner |
| `事後監査` | auditor / verifier / quality owner |

重要なのは、`役割名` ではなく `機能責務` で読むことである。

## 7. project-local adaptation rule

各 project は、この spine を local role model に写してよい。

ただし次は混同しない。

1. generic spine
2. local role 名
3. local status model
4. local packet schema

generic spine は、`何段で仕事が流れるか` を固定する。
local rule は、`誰がやるか / 何と呼ぶか / どの status を使うか` を追加する。

## 8. Done の定義

この spine 上で `Done` と言えるのは、少なくとも次が揃った時だけである。

1. 設計がある
2. 事前監査 verdict がある
3. 実行 evidence がある
4. 事後監査 verdict がある
5. close できない場合の reroute / resume がある

どれかが欠けるなら、`実行した` ではあっても `閉じた` とは言わない。

<a id="agent-workflow-navigation-baseline"></a>
## 9. Agent Workflow Navigation Baseline

agent が `いつ / 何を読むか` を迷わないため、workflow spine とは別に次の read order を持つ。

1. repo / project entrypoint
2. current task surface
3. workflow navigation guide
4. governance / audit rule
5. role guide
6. execution detail が必要な時だけ execution board
7. local runbook / lessons / archive が必要な時だけ local shelf

event ごとに次を固定する。

- who reads
- why they read
- what files are required
- what is optional
- what completion / handoff looks like

この section は project 固有の role 名、step 名、path を固定しない。

<a id="idea-triad-workflow"></a>
## 10. Idea Triad Workflow

アイデア創出は `diverge -> converge -> sharpen` の 3 段に分ける。

| phase | purpose | output |
|---|---|---|
| `diverge` | アイデアを広げる | broad candidate set |
| `converge` | 候補を比較・圧縮する | shortlist |
| `sharpen` | 実行可能性・価値・リスクを具体化する | go/no-go ready candidate |

phase 間では最低限次を handoff する。

- diverge -> converge
  - theme
  - candidate count
  - top candidates
  - short reason notes
- converge -> sharpen
  - shortlisted ideas
  - ranking
  - selection reason
  - key constraints

原則:

- `diverge` は量を優先する
- `converge` は比較軸を固定して絞る
- `sharpen` は実行可能性、価値、リスク、意思決定条件を具体化する

<a id="decision-boundary-baseline"></a>
## 11. Data-Driven Decision Boundary

decision boundary では次を分ける。

- current truth として人が更新する rule source
- runtime 用に派生した DB / cache / generated artifact
- human judgment が必要な escalation point

最小 cycle:

1. 新しい状況が出る
2. 既存 rule を確認する
3. match すれば decision を返す
4. match せず重要なら human へ escalate する
5. reviewed decision を source rule set へ書き戻す
6. runtime store を再読込または再生成する

completion と言えるのは、少なくとも次が明示された時だけである。

- source rule set が current truth だと分かる
- escalation 条件がある
- writeback が定義されている
- runtime reload / projection が定義されている
