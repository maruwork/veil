# VEIL UI audit inline hint 要件

Status: Draft
Date: 2026-06-07

## 1. 目的

UI の語彙一覧で、`review` と `drop-candidate` の行に見直し焦点を常時薄く表示し、hover しなくても棚卸し対象の要点が分かるようにする。

## 2. 背景

- 現在の UI では監査バッジと tooltip がある
- しかし `review_focus` や `suggested_action` は hover しないと読めない
- 棚卸し時は一覧を流し見して判断したいので、行内に短い要点がある方が自然

## 3. 今回の範囲

- `review` と `drop-candidate` に inline hint を追加する
- `keep` は現状どおり簡潔に保つ
- README / 設計書 / manual に反映する

## 4. 今回の範囲外

- audit 判定ロジックの変更
- 新しい filter や sort の追加
- tooltip の廃止

## 5. 機能要件

### 5.1 review

- `review_focus` の先頭側 1-2 件を薄く表示する

### 5.2 drop-candidate

- `suggested_action` または削除検討の要点を薄く表示する

### 5.3 keep

- inline hint は出さない

## 6. 非機能要件

- 一覧の視認性を壊さない
- hint は主情報より弱く見せる
- tooltip は補助として残す

## 7. 完了条件

- `review` / `drop-candidate` 行に inline hint が出る
- `keep` 行は従来どおり軽い表示のまま
