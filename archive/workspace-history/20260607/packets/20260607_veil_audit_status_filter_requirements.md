# VEIL audit status filter 要件

Status: Draft
Date: 2026-06-07

## 1. 目的

`veil-audit-db.py` の監査結果から、`review` や `drop-candidate` だけをすぐ見られるようにし、既存 helper DB の棚卸しをやりやすくする。

## 2. 背景

- 現在の `veil-audit-db.py` は全件を text / json で出せる
- しかし実運用では、まず `drop-candidate`、次に `review` を見たい場面が多い
- 全件出力だけだと件数が増えた時に棚卸ししづらい

## 3. 今回の範囲

- `veil-audit-db.py` に status 絞り込み引数を追加する
- text / json の両方で絞り込み後の結果を返す
- README / 設計書 / manual に絞り込み例を追記する

## 4. 今回の範囲外

- DB の自動 cleanup
- UI からの status filter 実行
- `keep / review / drop-candidate` 判定ロジック自体の大改修

## 5. 機能要件

### 5.1 引数

- `--status keep`
- `--status review`
- `--status drop-candidate`

複数回指定できる形にする。

### 5.2 出力

- 指定が無い時は従来どおり全件
- 指定がある時はその status だけ返す
- text 出力では集計も絞り込み後の件数を示す
- json 出力では filter 条件も返す

### 5.3 エラー

- 不正な status は argparse で弾く

## 6. 非機能要件

- 非破壊性は維持する
- 既存の無引数挙動を壊さない
- 文書では「drop-candidate を先に見る」「次に review を見る」の運用導線を短く示す

## 7. 完了条件

- `python veil-audit-db.py --status drop-candidate`
- `python veil-audit-db.py --status review --json`

が意図どおり動く。
