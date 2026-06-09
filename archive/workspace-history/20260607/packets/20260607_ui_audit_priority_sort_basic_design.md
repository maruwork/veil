# VEIL UI audit priority sort 基本設計

Status: Draft
Date: 2026-06-07

## 1. 設計方針

- 既存の sort ボタンを拡張し、新しい UI 部品は増やさない
- audit 情報は `auditMap` を使って描画時に並び替える

## 2. 実装方針

### 2.1 state

- `sortBy` に `audit` を追加

### 2.2 render

- audit sort priority map:
  - `drop-candidate`: 0
  - `review`: 1
  - `keep`: 2
  - none: 3

- sort rule:
  - priority asc
  - `use_count` asc
  - `id` asc

### 2.3 UI text

- locale に `sortAudit`
- sort toggle は `freq -> id -> audit -> freq`

## 3. 文書反映

- README
  - UI の棚卸し導線に `棚卸し優先` sort を追記
- docs/veil-design.md
  - audit visibility の説明へ追加
- docs/manual.html
  - 語彙一覧の使い方に追加

## 4. 検証方針

- JS syntax check
- 仮 audit summary の live smoke
- 文書整合確認
