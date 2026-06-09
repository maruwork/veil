# VEIL audit action guidance 実装計画

Status: Draft
Date: 2026-06-07

## 1. 実装手順

1. `veil-audit-db.py` の判定出力に行動指針を追加する
2. text 出力へ `次アクション` を追加する
3. README / 設計書 / manual に status ごとの手動処理導線を追加する
4. smoke を行う

## 2. 変更対象

- `veil-audit-db.py`
- `README.md`
- `docs/veil-design.md`
- `docs/manual.html`

## 3. 完了確認

- `drop-candidate` に削除検討が出る
- `review` に見直し焦点が出る
- 文書が UI の既存操作へ接続している
