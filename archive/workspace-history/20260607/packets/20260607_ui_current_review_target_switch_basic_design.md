# UI current review 対象変更解除 基本設計

## 1. 方針

- current review は「いま review 候補として見ている語」に限定する。
- フォームの `orig` が current review の `original` から外れたら current review を解除する。

## 2. 規則

1. current review 未設定なら何もしない。
2. `orig` 入力の trim 結果が空でも、current review original と異なれば解除する。
3. `fillAddForm(word)` は review 候補ではない新規編集入口なので、current review を先に解除してから値を流す。
4. `focusNextReview()` は従来どおり current review を設定してから review item を流す。

## 3. 実装点

- `ui/js/ui.js`
  - `orig` 入力値と current review original の差を見て解除する helper を追加する。
  - `fillAddForm()` の先頭で current review を解除する。
- `ui/main.js`
  - 既存 `orig` input listener から上記 helper を呼ぶ。

## 4. 文書反映

- `要見直し` の current review 表示は、別の語の編集に移ったら自動で外れることを README / 設計書 / manual に追記する。
