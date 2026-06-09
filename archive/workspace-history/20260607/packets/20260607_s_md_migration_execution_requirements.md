# s.md Migration Execution Requirements

## 1. Overview

### 目的

real `C:\Users\f_tan\.veil\rules\s.md` を、legacy flat rule から section-aware rule file へ移行する。

### 背景

- `c.md` の移行は完了した
- `s.md` は `9` rule を持ち、初回移行 batch の 2 本目である
- `skill` は current canonical で明確に高需要
- `source of truth` と `sync surface` は VEIL / common 運用の中核概念である

## 2. Scope

### In Scope

- `s.md` の current readback
- `s.md` 内 `9` rule の再分類
- `s.md` の section-aware migration
- migration 後の readback
- migration 実行記録の workspace 反映

### Out of Scope

- `d.md` 以降の移行
- rule の新規追加
- runtime script の仕様変更

## 3. Rule Decisions

- `skill` は `必須`
- `source of truth` は `必須`
- `sync surface` は `必須`
- `scoped canonical register` は `推奨`
- `spec doc` は `推奨`
- `split rule` は `推奨`
- `side conversation` は `観察`
- `stage` は `観察`
- `state plane` は `観察`

## 4. Success Criteria

- `s.md` に `## 必須 / ## 推奨 / ## 観察` の section が入る
- legacy flat line が `s.md` から消える
- 上記 Rule Decisions に従って各 rule が section 配置される
- `veil-profile-audit.py --rules-dir C:\Users\f_tan\.veil\rules` の text output で `s.md` の legacy flat が `0` になる

## 5. Stop Conditions

- current readback が計画時点と大きく異なる
- user home 側 rules 編集の承認が使えない
- file 内に今回の判断材料では処理しにくい追加 line / comment がある
