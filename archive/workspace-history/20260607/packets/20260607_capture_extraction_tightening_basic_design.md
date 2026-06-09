# Basic Design

## 1. Decision

- capture runtime を増やさず、抽出契約を tightening する
- tighten するのは `候補抽出` 節だけ

## 2. Tightened Rules

- 単語より複合語を優先する
- 2回以上出るだけでは不十分
- さらに次のどれかを満たす候補を優先する
  - 状態語
  - 判断語
  - 構造語
  - 運用ラベル
  - 既存 rule に近い語
- 一般動詞単体は原則として候補へ送らない
- 一般動詞を扱うのは次の場合だけ
  - 複合語で意味が固まる
  - 同じ運用文脈で繰り返し出る

## 3. Report Impact

- 候補数を減らす
- normalize の `selection hint` と合わせて、少数候補へ絞りやすくする

## 4. Rejected Alternatives

- 品詞解析を入れる
  - rejected: 依存ゼロ方針に合わない
- 抽出件数上限だけで制御する
  - rejected: 原因でなく結果だけを絞る

