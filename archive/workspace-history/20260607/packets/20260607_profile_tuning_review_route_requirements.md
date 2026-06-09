# Profile Tuning Review Route Requirements

## 1. Overview

### 目的

`current default profile` の `必須` / `推奨` / `観察` を見直しやすくするため、`veil-profile-audit.py` に rule-level review route を追加する。

### 背景

- current default profile migration は完了した
- 次の主題は `必須` が強すぎる語の tuning である
- file 単位 summary だけでは tuning しにくく、level ごとの rule 一覧が必要である

## 2. Scope

### In Scope

- `veil-profile-audit.py` に level filter を追加
- JSON / text の両方で rule-level list を返せるようにする
- README / 設計書 / current work を tuning route に追従させる

### Out of Scope

- 実際の rules 再調整
- 新しい support runtime 追加

## 3. Success Criteria

- `python veil-profile-audit.py --level 必須` で required rules の一覧が見える
- `python veil-profile-audit.py --level 観察 --json` で rule-level JSON が取れる
- summary-only 利用は壊さない
