# Basic Design

## 1. Decision

- `veil-normalize.py` に shortlist レイヤーを追加する
- `selection_hint` と `retention_hint` の上に、`短い review に残すか` の目安を返す

## 2. Buckets

- `短い review に残す`
  - `先に採る候補`
  - `保留寄り` でも `後で再観察する`
  - `保留寄り` でも `文脈不足で保留`
- `短い review から外す寄り`
  - `保留寄り` かつ `今は見送る`
  - `外す寄り`

## 3. Contract

各 item に追加:

- `shortlist_hint`
- `shortlist_reason`

## 4. Rejected Alternatives

- 結果自体を隠す
  - rejected: 透明性を落とす
- skill 側でだけ説明する
  - rejected: runtime 出力にも持たせたい
