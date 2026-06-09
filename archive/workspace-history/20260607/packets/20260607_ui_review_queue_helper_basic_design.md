# VEIL UI review queue helper 基本設計

Status: Draft
Date: 2026-06-07

## 1. 設計方針

- 新しい棚や modal は増やさず、既存 action row と追加フォームをつなぐ
- review item の選定は既存 audit 情報だけで行う

## 2. 実装方針

### 2.1 helper

- `getReviewItems()`
- `getNextReviewItem()`
- `fillReviewForm(item)`
- `focusNextReview()`

### 2.2 UI

- vocab action row に review button を追加
- render の summary 更新時に button count / disabled を反映

### 2.3 locale

- button label
- button title
- 完了通知

## 3. 文書反映

- README
- docs/veil-design.md
- docs/manual.html

`要見直し` button で編集フォームへ送れることを短く追記する。

## 4. 検証方針

- JS syntax
- 文字列 surface 確認
- live HTML surface 確認
