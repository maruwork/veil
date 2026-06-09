# VEIL UI drop-candidate bulk delete 要件

Status: Draft
Date: 2026-06-07

## 1. 目的

`drop-candidate` を helper DB から 1 件ずつ削除する手間を減らし、確認付きの一括削除導線を UI に追加する。

## 2. 背景

- 現在は `drop-candidate` を見つけやすくなったが、削除は各行の `×` ボタンだけ
- helper DB の棚卸しでは `drop-candidate` をまとめて掃除したい場面がある
- ただし正本ではないとはいえ削除は実データ操作なので、確認なし自動削除にはしない

## 3. 今回の範囲

- backend に複数 id の一括削除 endpoint を追加する
- UI に `削除候補を一括削除` の確認付き導線を追加する
- 対象は current audit で `drop-candidate` の語だけ
- README / 設計書 / manual に反映する

## 4. 今回の範囲外

- `review` の一括更新
- `~/.veil/rules/` への反映
- 確認なし自動削除

## 5. 機能要件

### 5.1 backend

- `POST /vocab/delete-batch`
- request:
  - `ids: number[]`
- response:
  - `ok`
  - `deleted_count`

### 5.2 UI

- 語彙一覧の action に一括削除ボタンを追加する
- 対象件数が 0 の時は無効化する
- click 時に件数付き confirm を出す
- 実行後は `loadVocab()` で監査情報も再読込する

### 5.3 対象集合

- `auditMap` の `status === drop-candidate`
- 現在の `catFilter` や `search` に依存せず、helper DB 全体の `drop-candidate` を対象とする

## 6. 非機能要件

- 削除対象の scope を confirm で明示する
- helper DB のみの操作であり、正本を触らないことを保つ

## 7. 完了条件

- UI から `drop-candidate` を一括削除できる
- confirm が出る
- 実行後に一覧と監査サマリが更新される
