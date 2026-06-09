# VEIL UI bulk delete preview 要件

Status: Draft
Date: 2026-06-07

## 1. 目的

`削除候補` 一括削除の confirm に対象語の先頭数件を出し、削除前の見通しを上げる。

## 2. 背景

- 現在の一括削除は件数だけで confirm している
- helper DB 専用とはいえ、何が消えるかが少しでも見えた方が安全
- backend の削除範囲や非破壊性の境界はすでに決まっているため、今回は UI confirm だけの改善で足りる

## 3. 今回の範囲

- confirm 文に対象語の先頭数件を含める
- 件数が多い時は `他 n 件` を出す
- README / manual / design に短く追記する

## 4. 今回の範囲外

- backend API の変更
- preview modal の追加
- 削除対象の選択変更

## 5. 機能要件

### 5.1 preview 対象

- `drop-candidate` の current 対象語
- 表示件数は 3 件程度

### 5.2 confirm 文

- 件数
- 先頭数件の語
- 残件数があれば `他 n 件`

## 6. 非機能要件

- confirm が長すぎない
- 既存の削除 flow を壊さない

## 7. 完了条件

- 一括削除 confirm で対象語 preview が見える
