# Current Default Profile Migration Final Batch Requirements

## 1. Overview

### 目的

current default profile の final batch として `m.md / n.md / o.md / u.md / v.md / w.md` を section-aware 形式へ移行し、legacy flat をゼロにする。

### 背景

- third batch までで legacy flat files は `6`
- 残りはすべて 1-2 rule の小 file である
- `normalization` は VEIL core に直接関わる

## 2. Batch Decisions

### m.md

- `mutation` は `推奨`
- `MDファイル` は `観察`

### n.md

- `normalization` は `必須`
- `naturalness` は `観察`

### o.md

- `old reference` は `観察`

### u.md

- `uncommitted` は `観察`
- `untracked` は `観察`

### v.md

- `verification family` は `推奨`
- `validator` は `観察`

### w.md

- `writeback` は `推奨`

## 3. Success Criteria

- 6 file すべてが section-aware 形式になる
- `veil-profile-audit.py --rules-dir C:\Users\f_tan\.veil\rules` で `legacy_flat=0 in 0 file(s)` になる
