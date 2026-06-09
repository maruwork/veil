# VEIL UI audit inline hint 基本設計

Status: Draft
Date: 2026-06-07

## 1. 設計方針

- 既存 row を大きく組み替えず、2 行目だけ追加する
- hint は監査バッジの補足であって、主ラベルではない

## 2. 実装方針

### 2.1 render

- helper `auditInlineHint(audit)` を追加する
- `review`
  - `review_focus` の先頭 2 件を ` / ` 連結
- `drop-candidate`
  - `suggested_action` または `review_focus` の先頭 1 件

### 2.2 layout

- `.vi` を `flex-wrap: wrap` にする
- hint 要素は `flex-basis: 100%`
- 見た目は小さく、低コントラスト

### 2.3 docs

- README
  - UI で inline hint が見えること
- docs/veil-design.md
  - audit visibility の箇条書きに追加
- docs/manual.html
  - 棚卸し対象の行には見直し焦点が薄く出ると明記

## 3. 検証方針

- JS syntax check
- live smoke で HTML surface 確認
- 文書整合確認
