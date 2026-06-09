# VEIL UI audit priority sort 要件

Status: Draft
Date: 2026-06-07

## 1. 目的

UI の語彙一覧で、`drop-candidate` と `review` を先に見つけやすくするため、棚卸し優先の並び替えを追加する。

## 2. 背景

- 現在の語彙一覧は `頻度` と `登録順` でしか並び替えられない
- 監査バッジと status filter はあるが、`all` のまま一覧を見る時に棚卸し対象が埋もれやすい
- helper DB の見直しでは、問題のある語を先に出す並びがあると自然

## 3. 今回の範囲

- UI に `棚卸し優先` sort を追加する
- 並び順は `drop-candidate -> review -> keep -> 監査なし`
- 同一 status 内では `use_count` の低いもの、次に登録順で安定表示する
- README / 設計書 / manual に反映する

## 4. 今回の範囲外

- audit 判定ロジックの変更
- UI 上の新しい filter 追加
- CLI の sort 機能追加

## 5. 機能要件

### 5.1 sort mode

- `freq`
- `id`
- `audit`

の 3 モードにする。

### 5.2 audit sort の規則

- `drop-candidate`
- `review`
- `keep`
- audit 情報なし

の順にする。

同一 status 内では:

- `use_count` 昇順
- `id` 昇順

### 5.3 UI 表示

- sort ボタンの表示文言が mode に追従する

## 6. 非機能要件

- 既存の `freq` / `id` 運用を壊さない
- audit filter と組み合わせても破綻しない

## 7. 完了条件

- sort ボタンで `頻度 -> 登録順 -> 棚卸し優先` を巡回できる
- `all` 一覧でも棚卸し対象が先頭側へ寄る
