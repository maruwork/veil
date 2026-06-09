# VEIL UI drop-candidate bulk delete 基本設計

Status: Draft
Date: 2026-06-07

## 1. 設計方針

- 既存の per-row delete を残したまま、helper DB 掃除だけを早くする補助導線を足す
- 削除対象の判定は既存 `auditMap` を使う

## 2. 実装方針

### 2.1 backend

- `delete_vocab_batch(ids)`
- `POST /vocab/delete-batch`
- `ids` が空なら no-op

### 2.2 UI

- header action に bulk delete button を追加
- helper:
  - `getDropCandidateIds()`
  - `bulkDeleteDropCandidates()`
- button label は件数込みにする
- 件数 0 の時は disabled

### 2.3 locale

- ボタン文言
- confirm 文言
- 実行完了 toast

## 3. 文書反映

- README
  - UI で `drop-candidate` 一括削除ができること
- docs/veil-design.md
  - `/vocab/delete-batch` を API 一覧に追加
- docs/manual.html
  - 語彙一覧 action と確認つき一括削除を追加

## 4. 検証方針

- py_compile
- JS syntax
- 仮 DB に対して batch delete smoke
- 文書整合確認
