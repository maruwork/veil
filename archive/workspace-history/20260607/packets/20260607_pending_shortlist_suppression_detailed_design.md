# Detailed Design

## 1. Runtime Contract

`veil-normalize.py --json` の各 item に次を返す。

- `shortlist_hint`
- `shortlist_reason`

text 出力にも:

- `review 目安`
- `review 理由`

を追加する。

## 2. Decision Rules

### 2.1 `短い review から外す寄り`

条件:

- `selection_hint == 外す寄り`
- または `retention_hint == 今は見送る`

意図:

- 今回の短い採用検討一覧には含めない

### 2.2 `短い review に残す`

条件:

- `先に採る候補`
- または `retention_hint == 後で再観察する`
- または `retention_hint == 文脈不足で保留`

意図:

- 今回の review 対象として残す

## 3. Verification Conditions

- `close / closed / closing / updates` が `短い review から外す寄り`
- `verification` が `短い review に残す`
- `summary` が `短い review に残す`
