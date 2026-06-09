# Decision-to-Implementation Consistency Review

設計判断、要件、実装、運用手順のあいだにズレがないかを確認する portable baseline framework。

この framework は
`project-progression-rule.md`
のうち、主に

- `局所進捗を前進と数えない`
- `完了と書かれていることと本当に完了していることを分ける`
- `ズレ検出`
- `補正対象面の特定`

を、整合性 review の面で具体化する。

ここで扱う `truth boundary drift` は、context 面そのものの正本を再定義するものではない。
`current / history / artifact / cache` の正規境界そのものは
`../policies/context-management-policy.md`
を正本とし、この framework では

- その境界が review 時点で崩れているか
- 崩れているなら何を直せば整合が回復するか

を分類して後続修正へ渡す。

## 1. Purpose

- 設計判断と実装実態が一致しているかを確認する
- `完了と書かれている` と `本当に完了している` のズレを早期に検出する
- 追加実装より先に、説明・実装・運用の不整合を露出させる

## 2. Minimum Inputs

- decision record or design spec
- current implementation surface
- current operational route or runbook
- current validation or test surface

## 3. Review Questions

1. decision / design に書かれている主張は、実装側に存在するか
2. 実装は存在するが、説明や runbook が古くなっていないか
3. current truth と history / artifact / cache が混線していないか
4. owner, trigger, input, output, completion condition が一致しているか
5. `完了` と書かれていても、未処理 residue や hidden blocker が残っていないか

## 4. Output Contract

少なくとも次を出力する。

- 一致している項目
- 不一致の項目
- 不一致の種別
  - missing implementation
  - stale documentation
  - stale operation note
  - truth boundary drift
  - false-complete claim
- 修正先
  - code
  - design/spec
  - runbook/manual
  - register/canon

## 5. Classification

| result | meaning |
|---|---|
| `aligned` | decision / design / implementation / operation が一致している |
| `doc-drift` | 実装はあるが説明面が古い |
| `implementation-gap` | 説明や完了主張に対して実装が足りない |
| `truth-boundary-drift` | current / history / artifact / cache の境界が崩れている |
| `false-complete` | 実際には未完なのに完了扱いされている |

## 6. Handoff Rule

- 不一致を見つけたら、まず `どこを直せば current truth が回復するか` を決める
- 説明面だけで回復するものと、実装変更が必要なものを分ける
- false-complete は close verdict を取り消してでも修正する

## 7. Completion Condition

この review は次を満たしたときに完了とみなす。

- 不一致が current canon で分類済み
- 直すべき面が一意
- false-complete claim が残っていない
- 後続が `何を直せば一致が回復するか` を迷わず読める

<a id="flow-integrity-review-framework"></a>
## 8. Flow Integrity Review

複数 step の flow では、個別 file が存在しても `つながりが切れている` 状態を別に点検する。

最低限確認すること:

- 開始点から終了点までの単一 flow が定義されているか
- 各 step の owner / input / output 契約が明確か
- human judgment と auto continue の境界が分かれているか
- 通知、記録、承認、更新が次 step へ渡っているか
- `参照だけある / 仕様だけある / 実装だけある` 状態になっていないか

review sequence:

1. flow boundary を固定する
2. step ごとの契約を記録する
3. 連結状態を確認する
4. 異常時の分岐を確認する
5. 発見事項を `整合性修正 / 新規実装` と `根本修正 / 表面修正` に分類する

最低限残す evidence:

- 実施時刻
- `PASS / WARNING / FAIL`
- 確認した file / command / screen / DB result
- 所感
- 次 action
