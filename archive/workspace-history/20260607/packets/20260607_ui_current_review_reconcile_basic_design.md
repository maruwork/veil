# UI current review 再同期 基本設計

## 1. 方針

- current review は `id` と `original` を UI state に持ったままにする。
- ただし authority は常に最新の `auditMap` と `vocab` に置く。
- `loadVocab()` 完了後に current review を再評価し、維持か解除かを決める。

## 2. 再同期規則

1. current review が未設定なら何もしない。
2. `vocab` から current review id を探す。
3. 見つからない場合は current review を解除する。
4. `auditMap[id]` が存在しない、または `status !== review` の場合は解除する。
5. 維持する場合は `original` を最新値へ更新する。

## 3. 操作後の挙動

- `upsertVocab()` 完了後
  - `loadVocab()` の再同期規則に任せる。
- `deleteVocab()` / `deleteVocabBatch()` 完了後
  - 同上。
- `focusNextReview()`
  - 従来どおり先頭 review item を current review に設定する。

## 4. 文書反映

- `現在編集中の review 候補も分かる` だけでなく、
  - 保存や削除で review ではなくなったら自動で外れる
  ことを README / 設計書 / manual に追記する。
