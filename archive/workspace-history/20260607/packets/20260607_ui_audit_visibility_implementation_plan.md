# VEIL UI audit visibility 実装計画

Status: Draft
Date: 2026-06-07

## 1. 実装手順

1. `veil-audit-core.py` を追加する
2. `veil-audit-db.py` を shared helper 使用へ寄せる
3. `app.py` に `/vocab/audit` を追加する
4. `ui/` に audit badge / summary / filter を追加する
5. README / 設計書 / manual を更新する
6. smoke を行う

## 2. 変更対象

- `veil-audit-core.py`
- `veil-audit-db.py`
- `app.py`
- `ui/index.html`
- `ui/style.css`
- `ui/locales.js`
- `ui/js/state.js`
- `ui/js/api.js`
- `ui/js/render.js`
- `ui/main.js`
- `README.md`
- `docs/veil-design.md`
- `docs/manual.html`

## 3. 完了確認

- CLI と UI の audit 基準が共通
- UI 一覧で `review` / `drop-candidate` を見つけやすい
- 既存の変換・登録・削除導線が壊れていない
