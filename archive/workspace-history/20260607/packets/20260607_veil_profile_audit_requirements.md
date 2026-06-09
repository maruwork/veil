# VEIL Profile Audit Requirements

## 1. Overview

### 目的

`~/.veil/rules/` の current default profile を non-destructive に棚卸しし、`必須 / 推奨 / 観察` の分布、旧 flat rule、移行候補を見える化する。

### 背景

- VEIL は rule 3 層と section heading runtime を持った
- ただし current default profile 自体がどれだけ section 化されているか、どれだけ旧 flat rule が残っているかを簡単に見られない
- 実データを破壊せずに current profile を観察できる補助が必要

## 2. Scope

### In Scope

- root support script を 1 本追加する
- `~/.veil/rules/` または任意 rules dir を読み、file ごとの level 分布と legacy flat rule を報告する
- text / json 両出力を持つ
- README / design に最小導線を追加する

### Out of Scope

- rules の自動 migration
- rule の自動 level 再配置
- `veil-capture` の動作変更

## 3. Success Criteria

- `python veil-profile-audit.py` で rules 棚卸しができる
- legacy flat rule を含む file が分かる
- level ごとの件数が分かる
- current default profile 整理の入口として使える

## 4. Functional Requirements

1. rules dir を指定できること
2. file ごとに `必須 / 推奨 / 観察` 件数を出せること
3. section heading 前の legacy flat rule 件数を出せること
4. total summary を出せること
5. json 出力を持つこと

## 5. Non-Functional Requirements

- read-only
- 標準ライブラリのみ
- verify は sample rules で十分
