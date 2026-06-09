# VEIL UI review queue helper 実装計画

Status: Draft
Date: 2026-06-07

## 1. 実装手順

1. helper button を HTML / locale に追加する
2. review item 選定 helper を UI に追加する
3. render で button count と disabled を更新する
4. 文書を更新する
5. syntax / surface 確認を行う

## 2. 変更対象

- `ui/index.html`
- `ui/locales.js`
- `ui/js/render.js`
- `ui/js/ui.js`
- `README.md`
- `docs/veil-design.md`
- `docs/manual.html`

## 3. 完了確認

- `要見直し` button が件数付きで出る
- click で review item がフォームに入る
- 更新せずに preview だけできる
