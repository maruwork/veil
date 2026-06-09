# UI current review 対象変更解除 要件

## 1. 背景

- `要見直し` button で review 候補を編集フォームへ送れる。
- ただし、その後に別の語を手入力したり、未変換語から新しい語を起こしたりすると、`現在の要見直し` 表示が残って誤解を生みやすい。

## 2. 今回の対象

- 編集フォームの対象が current review から別の語へ移った時点で、current review 表示を解除する。
- 次の経路を対象にする。
  - `orig` 入力欄の手入力
  - 未変換語 click
  - quick add からのフォーム流し込み

## 3. 対象外

- review queue の選定順変更
- 保存後に次の review 候補へ自動で送る機能
- server / DB 変更

## 4. 完了条件

- current review 中に `orig` 入力欄が別の語へ変わったら帯と row highlight を外す。
- 未変換語 / quick add で別語をフォームへ入れた場合も同様に外す。
- `要見直し` button 自体の動作は壊さない。
- 文書説明が実装と一致する。
