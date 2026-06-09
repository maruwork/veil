# VEIL UI bulk delete preview 基本設計

Status: Draft
Date: 2026-06-07

## 1. 設計方針

- confirm 文の組み立てだけを追加する
- 既存の `getDropCandidateIds()` を拡張して、名前配列も取る

## 2. 実装方針

### 2.1 helper

- `getDropCandidateItems()`
- `buildBulkDropPreview(items)`

### 2.2 locale

- confirm 文は preview 文字列を受け取れる形へ変更

## 3. 文書反映

- README
- docs/veil-design.md
- docs/manual.html

`件数確認に加えて対象語 preview が出る` とだけ記す。

## 4. 検証方針

- JS syntax
- 文字列生成の smoke
- 文書整合確認
