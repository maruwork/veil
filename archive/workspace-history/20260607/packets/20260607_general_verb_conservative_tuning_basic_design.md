# Basic Design

## 1. Decision

- `veil-normalize.py` に一般動詞 family 判定を追加する
- 判定対象は single-word lowercase 候補に絞る
- family 判定された語は、頻度だけで説明語候補へ上げない

## 2. Boundary

- runtime:
  - `veil-normalize.py`
- docs:
  - `README.md`
  - `docs/veil-design.md`
  - 2 つの capture skill
  - `index/project-current-work.md`
- unchanged:
  - `veil-lint.py`
  - `veil-sync.py`
  - DB / schema

## 3. Heuristic Direction

- base verb set を持つ
- `s / ed / ing` の軽い活用形を family とみなす
- family hit の single-word は、出現回数だけで説明語候補に寄せない
- selection / retention は保守側へ寄せる

## 4. Rejected Alternatives

- 品詞解析を入れる
  - rejected: 依存ゼロ方針に反する
- capture 側だけで制御する
  - rejected: normalize runtime 側の契約にも反映したい
