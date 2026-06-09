# VEIL audit status filter 実装計画

Status: Draft
Date: 2026-06-07

## 1. 実装手順

1. `veil-audit-db.py` に `--status` 引数を追加する
2. 絞り込み処理を入れる
3. text / json 出力へ filter 情報を反映する
4. README / 設計書 / manual に利用例を追加する
5. smoke を行う

## 2. 変更対象

- `veil-audit-db.py`
- `README.md`
- `docs/veil-design.md`
- `docs/manual.html`

## 3. 完了確認

- filter 無しの既存挙動が維持される
- `drop-candidate` / `review` の絞り込みが動く
- 文書が新しい CLI 例に追従している
