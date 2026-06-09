# UI current review 再同期 要件

## 1. 背景

- `要見直し` button で先頭候補を編集フォームへ送れるようになった。
- ただし、保存・削除・一括削除・監査再読込のあとも `現在の要見直し` 帯と row highlight が残る余地がある。
- 棚卸し導線では「今どの review 候補を見ているか」が分かるだけでなく、もう review ではない候補を自然に外せる必要がある。

## 2. 今回の対象

- UI 上の current review 表示を監査結果と再同期する。
- 次の操作後に current review を見直す。
  - 単件保存
  - 単件削除
  - `削除候補` 一括削除
  - `loadVocab()` による再読込

## 3. 対象外

- review queue の順位規則そのものの変更
- `要見直し` button の選定基準変更
- server API の追加
- helper DB の監査基準変更

## 4. 完了条件

- current review item が再読込後も `review` のままなら帯と highlight を維持する。
- current review item が消えた、または `review` ではなくなった場合は帯と highlight を外す。
- 単件保存・単件削除・一括削除後に stale な current review 表示が残らない。
- README / 設計書 / manual の説明が実装と一致する。
