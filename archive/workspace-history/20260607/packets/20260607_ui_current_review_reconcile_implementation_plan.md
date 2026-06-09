# UI current review 再同期 実装計画

## 1. 実装

- `ui/js/ui.js`
  - current review を解除する helper を追加する。
  - `auditMap` / `vocab` を見て current review を再評価する helper を追加する。
- `ui/js/api.js`
  - `loadVocab()` の最後で current review 再同期 helper を呼ぶ。

## 2. 文書

- `README.md`
- `docs/veil-design.md`
- `docs/manual.html`

## 3. 検証

- `node --check ui/js/ui.js`
- `node --check ui/js/api.js`
- `rg` で `現在の要見直し` と再同期説明を確認する。
