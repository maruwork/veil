# VEIL UI audit visibility 要件

Status: Draft
Date: 2026-06-07

## 1. 目的

helper DB の棚卸し結果を Web UI 上でも見えるようにし、`drop-candidate` と `review` を CLI に戻らず確認しやすくする。

## 2. 背景

- `veil-audit-db.py` は CLI で `keep / review / drop-candidate`、行動指針、見直し焦点を返せる
- しかし UI で語彙を削除・上書き更新する前に、同じ画面で監査結果を見られない
- 実運用では「監査してから UI で削除・更新」が自然なので、表示面の接続が欲しい

## 3. 今回の範囲

- 監査ロジックを script / app で再利用できる形に整理する
- `app.py` に current `vocab.db` の audit 結果 API を追加する
- UI の語彙一覧に audit status と軽い要約を表示する
- UI に audit status 絞り込みと件数サマリを追加する
- README / 設計書 / manual に UI audit visibility を追記する

## 4. 今回の範囲外

- UI からの audit 実行ボタン追加
- `vocab.db` の自動 cleanup
- `~/.veil/rules/` との自動同期

## 5. 機能要件

### 5.1 app API

- `GET /vocab/audit`
- current `vocab.db` を監査して JSON を返す
- `status` query による絞り込みを受けられる

### 5.2 UI 表示

- 各語彙行に audit status badge を出す
- `review` / `drop-candidate` は理由や次アクションが tooltip で見える
- 上部に `keep / review / drop-candidate` の件数サマリを出す
- status filter で一覧を絞れる

### 5.3 再利用

- `veil-audit-db.py` と `app.py` が別実装でずれないようにする

## 6. 非機能要件

- 既存の UI 変換機能を壊さない
- 監査 API は非破壊である
- 表示は helper DB の補助であり、authority と誤認させない

## 7. 完了条件

- UI 一覧で audit status が見える
- `review` / `drop-candidate` に絞って見られる
- CLI と UI の監査結果が同じ基準になる
