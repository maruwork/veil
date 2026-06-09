# Basic Design

## 1. Decision

- `veil-normalize.py` に `保留処理レイヤー` を追加する
- 既存の `selection_hint` の下に、`保留寄り` の時だけ短い次 action を返す
- action は `今は見送る`, `後で再観察する`, `文脈不足で保留` の 3 つに絞る

## 2. Boundary

- runtime 変更対象:
  - `veil-normalize.py`
- 説明面変更対象:
  - `README.md`
  - `docs/veil-design.md`
  - 2 つの capture skill
  - `index/project-current-work.md`
- 変更しないもの:
  - `veil-lint.py`
  - `veil-sync.py`
  - schema / DB
  - markdown mirror generation

## 3. Data Contract

各 normalize result item に次を追加する。

- `retention_hint`
- `retention_reason`

期待値:

- `selection_hint != 保留寄り` の時:
  - `retention_hint` は空または未設定
- `selection_hint == 保留寄り` の時:
  - `retention_hint` は 3 値のいずれか
  - `retention_reason` は 1 行の説明

## 4. Heuristic Direction

- `今は見送る`
  - 一般動詞単体
  - 頻度 1
  - 曖昧語寄り
- `後で再観察する`
  - 説明語候補ではある
  - ただし頻度や文脈が足りない
- `文脈不足で保留`
  - 意味は強そうだが、現会話だけでは確定しにくい

## 5. Output Surface

text 出力では `保留寄り` の item にだけ:

- `保留処理: ...`
- `保留理由: ...`

を追加する。

## 6. Rejected Alternatives

- `保留寄り` をさらに 5 段階以上に増やす
  - rejected: 軽量化の目的に反する
- skill 側だけで保留運用を説明する
  - rejected: runtime 出力にも欲しい
- schema に保留状態を記録する
  - rejected: 今回は runtime guidance だけで足りる
