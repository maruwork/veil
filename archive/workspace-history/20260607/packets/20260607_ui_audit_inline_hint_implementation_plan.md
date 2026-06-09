# VEIL UI audit inline hint 実装計画

Status: Draft
Date: 2026-06-07

## 1. 実装手順

1. render helper を追加する
2. row に inline hint を描画する
3. style を追加する
4. README / 設計書 / manual を更新する
5. syntax / live smoke を行う

## 2. 変更対象

- `ui/js/render.js`
- `ui/style.css`
- `README.md`
- `docs/veil-design.md`
- `docs/manual.html`

## 3. 完了確認

- `review` / `drop-candidate` の要点が hover なしで見える
- 既存の badge / tooltip / filter / sort が壊れていない
