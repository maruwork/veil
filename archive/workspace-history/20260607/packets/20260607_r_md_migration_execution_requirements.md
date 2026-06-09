# r.md Migration Execution Requirements

## 1. Overview

### 目的

real `C:\Users\f_tan\.veil\rules\r.md` を、legacy flat rule から section-aware rule file へ移行する。

### 背景

- `r.md` は `5` rule を持つ
- `readback` は current progress / verification の中心語である
- `race condition` や `redundant` は一般技術語で、hard gate に残しすぎると広すぎる

## 2. Rule Decisions

- `readback` は `必須`
- `root entry` は `推奨`
- `runtime copy` は `推奨`
- `race condition` は `観察`
- `redundant` は `観察`

## 3. Success Criteria

- `r.md` に `## 必須 / ## 推奨 / ## 観察` の section が入る
- legacy flat line が `r.md` から消える
- `veil-profile-audit.py --rules-dir C:\Users\f_tan\.veil\rules` の text output で `r.md` の legacy flat が `0` になる
