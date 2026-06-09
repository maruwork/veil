# UI current review 対象変更解除 実装計画

## 1. 実装

- `ui/js/ui.js`
  - current review 対象変更判定 helper を追加する。
  - `fillAddForm()` で current review を解除する。
- `ui/main.js`
  - `orig` input listener に current review 判定を追加する。

## 2. 文書

- `README.md`
- `docs/veil-design.md`
- `docs/manual.html`

## 3. 検証

- `node --check ui/js/ui.js`
- `node --check ui/main.js`
- `rg` で説明文を確認する。
