# d.md Migration Execution Requirements

## 1. Overview

### 目的

real `C:\Users\f_tan\.veil\rules\d.md` を、legacy flat rule から section-aware rule file へ移行する。

### 背景

- `c.md` と `s.md` の移行は完了した
- `d.md` は `5` rule を持ち、初回移行 batch の 3 本目である
- `design` 系は common と current canonical の両方で主語になりやすい

## 2. Scope

### In Scope

- `d.md` の current readback
- `d.md` 内 `5` rule の再分類
- `d.md` の section-aware migration
- migration 後の readback
- migration 実行記録の workspace 反映

### Out of Scope

- `p.md` 以降の移行
- rule の新規追加
- runtime script の仕様変更

## 3. Rule Decisions

- `design` は `必須`
- `design boundary` は `必須`
- `decision memo` は `推奨`
- `dedup` は `推奨`
- `document quality` は `観察`

## 4. Success Criteria

- `d.md` に `## 必須 / ## 推奨 / ## 観察` の section が入る
- legacy flat line が `d.md` から消える
- 上記 Rule Decisions に従って各 rule が section 配置される
- `veil-profile-audit.py --rules-dir C:\Users\f_tan\.veil\rules` の text output で `d.md` の legacy flat が `0` になる

## 5. Stop Conditions

- current readback が計画時点と大きく異なる
- file 内に今回の判断材料では処理しにくい追加 line / comment がある
