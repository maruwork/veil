# Current Default Profile Migration Third Batch Requirements

## 1. Overview

### 目的

current default profile の third batch として `e.md / f.md / g.md` を section-aware 形式へ移行する。

### 背景

- second batch までで legacy flat files は `9`
- `e/f/g` は `1 + 2 + 2 = 5` rule の小束であり、意味判定も比較的安定している

## 2. Batch Decisions

### e.md

- `external authority` は `推奨`

### f.md

- `file taxonomy` は `推奨`
- `falsy` は `観察`

### g.md

- `goal` は `必須`
- `graceful fallback` は `観察`

## 3. Success Criteria

- `e.md / f.md / g.md` が section-aware 形式になる
- 3 file の legacy flat が `0`
