# VEIL UI audit priority sort 実装計画

Status: Draft
Date: 2026-06-07

## 1. 実装手順

1. state と locale に audit sort mode を追加する
2. sort toggle を 3 モード巡回にする
3. renderList に audit priority sort を追加する
4. README / 設計書 / manual を更新する
5. syntax / live smoke を行う

## 2. 変更対象

- `ui/js/state.js`
- `ui/locales.js`
- `ui/js/ui.js`
- `ui/js/render.js`
- `README.md`
- `docs/veil-design.md`
- `docs/manual.html`

## 3. 完了確認

- `棚卸し優先` sort が動く
- audit filter と併用しても崩れない
- 文書が新しい並び替えに追従している
