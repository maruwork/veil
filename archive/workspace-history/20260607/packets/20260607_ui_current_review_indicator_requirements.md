# VEIL UI current review indicator 要件

Status: Draft
Date: 2026-06-07

## 1. 目的

`要見直し` helper でフォームへ送った review item がどれかを UI 上で明示し、編集中に対象を見失わないようにする。

## 2. 背景

- 現在は `要見直し` button で先頭 review item をフォームへ送れる
- しかしフォームへ入った後、その item が一覧のどれかはすぐには分からない
- review を数件続けて直す時、今どれを触っているかが見える方が安全

## 3. 今回の範囲

- current review item の state を持つ
- 語彙一覧で current review row を強調する
- 追加フォームの近くにも短い current review 表示を出す
- README / 設計書 / manual に反映する

## 4. 今回の範囲外

- review queue の進む / 戻る UI
- 自動保存
- 一般の手動追加 item まで current 表示すること

## 5. 機能要件

### 5.1 state

- current review item の id / original を保持する
- `focusNextReview()` で更新する
- 通常の `fillAddForm()` だけでは review current を上書きしない

### 5.2 一覧表示

- current review row に強調 class を付ける
- badge か border で分かるようにする

### 5.3 フォーム表示

- `現在の要見直し: {original}` の短い表示
- current review が無い時は非表示

## 6. 非機能要件

- 表示は軽く、既存レイアウトを壊さない
- helper 由来の current 表示であることを保つ

## 7. 完了条件

- review helper で送った対象が一覧とフォーム両方で分かる
