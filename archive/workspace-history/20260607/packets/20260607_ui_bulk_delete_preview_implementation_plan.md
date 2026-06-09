# VEIL UI bulk delete preview 実装計画

Status: Draft
Date: 2026-06-07

## 1. 実装手順

1. UI helper を追加する
2. locale の confirm 文を preview 対応にする
3. 一括削除 confirm を差し替える
4. 文書を更新する
5. syntax / smoke を行う

## 2. 変更対象

- `ui/locales.js`
- `ui/js/ui.js`
- `README.md`
- `docs/veil-design.md`
- `docs/manual.html`

## 3. 完了確認

- confirm に対象語 preview が出る
- 削除実行は従来どおり動く
