# p.md Migration Execution Requirements

## 1. Overview

### 目的

real `C:\Users\f_tan\.veil\rules\p.md` を、legacy flat rule から section-aware rule file へ移行する。

### 背景

- `p.md` は `5` rule を持つ
- `path` は機械処理語と概念語が衝突しやすく、hard gate に残しすぎると逆効果
- `pending` は current 運用で高需要な保留語である

## 2. Rule Decisions

- `pending` は `必須`
- `people first` は `推奨`
- `path` は `観察`
- `pipeline` は `観察`
- `portability split` は `観察`

## 3. Success Criteria

- `p.md` に `## 必須 / ## 推奨 / ## 観察` の section が入る
- legacy flat line が `p.md` から消える
- `veil-profile-audit.py --rules-dir C:\Users\f_tan\.veil\rules` の text output で `p.md` の legacy flat が `0` になる
