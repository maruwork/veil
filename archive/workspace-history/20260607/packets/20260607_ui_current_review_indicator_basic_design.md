# VEIL UI current review indicator 基本設計

Status: Draft
Date: 2026-06-07

## 1. 設計方針

- 新しい複雑な panel は作らず、既存フォーム上部と一覧 row の強調だけで済ませる
- current review は helper action でのみセットする

## 2. 実装方針

### 2.1 state

- `currentReviewId`
- `currentReviewOriginal`

### 2.2 UI

- index.html
  - add form の下に current review 表示エリア
- render.js
  - row に `vi-current-review`
- ui.js
  - `setCurrentReview(item)`
  - `renderCurrentReviewBanner()`

### 2.3 locale

- `currentReviewLabel`

## 3. 文書反映

- README
- docs/veil-design.md
- docs/manual.html

`要見直し helper で送った対象は一覧とフォームで見える` と記す。

## 4. 検証方針

- JS syntax
- surface 確認
- 文書整合確認
