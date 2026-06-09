# c.md Migration Execution Requirements

## 1. Overview

### 目的

real `C:\Users\f_tan\.veil\rules\c.md` を、legacy flat rule から section-aware rule file へ移行する。

### 背景

- current default profile 全体は legacy flat のままである
- `c.md` は `10` rule を持ち、初回移行 batch の先頭 file である
- runtime は `## 必須 / ## 推奨 / ## 観察` を解釈できるが、実 profile 側は未移行である

## 2. Scope

### In Scope

- `c.md` の current readback
- `c.md` 内 `10` rule の再分類
- `c.md` の section-aware migration
- migration 後の readback
- migration 実行記録の workspace 反映

### Out of Scope

- `s.md` 以降の移行
- rule の新規追加
- 既存訳語の全面見直し
- runtime script の仕様変更

## 3. Rule Decisions

- `current state` は `必須`
- `checkpoint` は `必須`
- `close verdict` は `必須`
- `current surface` は `必須`
- `common asset` は `推奨`
- `common asset promotion` は `観察`
- `closeable` は `観察`
- `comparison doc` は `観察`
- `compress` は `観察`
- `current order` は `観察`

## 4. Success Criteria

- `c.md` に `## 必須 / ## 推奨 / ## 観察` の section が入る
- legacy flat line が `c.md` から消える
- 上記 Rule Decisions に従って各 rule が section 配置される
- `veil-profile-audit.py --rules-dir C:\Users\f_tan\.veil\rules` の text output で `c.md` の legacy flat が `0` になる

## 5. Stop Conditions

- current readback が計画時点と大きく異なる
- user home 側 rules 編集の承認が得られない
- 実 file に、今回の session では判断材料が足りない追加 rule / comment / 手修正が混在している
