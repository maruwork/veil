# VEIL UI current review indicator 実装計画

Status: Draft
Date: 2026-06-07

## 1. 実装手順

1. state を追加する
2. current review banner を HTML / locale / ui.js に追加する
3. row highlight を render / css に追加する
4. 文書を更新する
5. syntax / surface 確認を行う

## 2. 変更対象

- `ui/js/state.js`
- `ui/index.html`
- `ui/locales.js`
- `ui/js/ui.js`
- `ui/js/render.js`
- `ui/style.css`
- `README.md`
- `docs/veil-design.md`
- `docs/manual.html`

## 3. 完了確認

- current review item が一覧とフォームで見える
- helper 以外の操作を壊さない
