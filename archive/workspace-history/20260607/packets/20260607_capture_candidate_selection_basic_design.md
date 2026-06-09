# Basic Design

## 1. Decision

- `veil-normalize.py` に selection layer を追加する
- 既存の `classification_hint`, `priority_hint`, `suggested_level` を使って軽量に決める

## 2. Selection Buckets

- `先に採る候補`
  - 説明語候補
  - `priority_hint` が `先に見る` または `次に見る`
  - `suggested_level` が `必須` または `推奨`
- `保留寄り`
  - 観察スタート
  - ただし識別子/固有名ではない
- `外す寄り`
  - 識別子候補
  - 固有名候補

## 3. Output Contract

各 result item に次を追加する。

- `selection_hint`
- `selection_reason`

text 出力にも:

- `選別目安: ...`
- `選別理由: ...`

## 4. Rejected Alternatives

- shortlist 件数を固定する
  - rejected: 文脈で変わる
- capture skill 側でだけ説明する
  - rejected: runtime 出力にも欲しい

