# Current Default Profile Audit Execution Requirements

## 1. Overview

### 目的

real `~/.veil/rules/` を read-only で棚卸しし、current default profile の level 分布、legacy flat rule 残存、次に整理すべき論点を確定する。

### 背景

- `veil-profile-audit.py` は実装済み
- ただし current default profile 自体の実データ監査はまだ行っていない
- 次に profile 整理へ進むには、実データの現在地を artifact として固定する必要がある

## 2. Scope

### In Scope

- `~/.veil/rules/` を read-only で監査する
- 監査結果を workspace artifact に落とす
- 次 wave の整理対象を抽出する

### Out of Scope

- `~/.veil/rules/` の直接編集
- 自動 migration
- runtime script 変更

## 3. Success Criteria

- current default profile の summary が取れている
- legacy flat file の有無が分かる
- 次 wave の整理対象が列挙されている
