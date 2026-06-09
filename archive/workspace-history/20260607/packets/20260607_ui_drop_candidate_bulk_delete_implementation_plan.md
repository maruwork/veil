# VEIL UI drop-candidate bulk delete 実装計画

Status: Draft
Date: 2026-06-07

## 1. 実装手順

1. backend に batch delete を追加する
2. UI に bulk delete button と helper を追加する
3. locale と style を整える
4. README / 設計書 / manual を更新する
5. smoke を行う

## 2. 変更対象

- `app.py`
- `ui/index.html`
- `ui/locales.js`
- `ui/style.css`
- `ui/js/api.js`
- `ui/js/render.js`
- `ui/js/ui.js`
- `README.md`
- `docs/veil-design.md`
- `docs/manual.html`

## 3. 完了確認

- `drop-candidate` 件数が button に出る
- confirm 後に batch delete が動く
- 一覧と audit summary が更新される
