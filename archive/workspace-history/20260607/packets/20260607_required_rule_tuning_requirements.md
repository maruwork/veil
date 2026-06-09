# Required Rule Tuning Requirements

## 1. Overview

### 目的

current default profile の `必須` を、高影響語だけへさらに絞る。

### 背景

- migration 完了後の `必須` queue は `14` rule
- `veil-profile-audit.py --level 必須` で見ると、mainline exact hit が弱い語や internal governance 寄りの語が混ざっている
- VEIL の方針は「全部を hard gate にしない」であり、`必須` は高需要・高影響語へ絞るべきである

## 2. Scope

### In Scope

- current `必須` 14 rule の再判定
- `~/.veil/rules/` の level 調整
- tuning 後 audit

### Out of Scope

- 新規 rule 追加
- 訳語そのものの変更
- `推奨` / `観察` の相互調整

## 3. Tuning Decisions

### 必須に残す

- `current state`
- `normalization`
- `skill`
- `task`

### 推奨へ落とす

- `checkpoint`
- `close verdict`
- `current surface`
- `design`
- `design boundary`
- `goal`
- `pending`
- `readback`
- `source of truth`
- `sync surface`

## 4. Success Criteria

- `veil-profile-audit.py --level 必須` の queue が 4 rule になる
- `~/.veil/rules/` の section 構造は維持される
- tuning 後も `legacy_flat=0`

## 5. Stop Conditions

- user-facing hard gate から外すと明らかに困る語が見つかる
- 実 rules の current content が planned state と異なる
