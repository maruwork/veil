# VEIL UI review queue helper 要件

Status: Draft
Date: 2026-06-07

## 1. 目的

`review` 対象を 1 件ずつ探して手入力する手間を減らすため、要見直し語を編集フォームへ送る補助導線を追加する。

## 2. 背景

- `drop-candidate` は一括削除まで整ってきた
- 一方 `review` は一覧で見つけやすくなっただけで、編集フォームへ持っていく導線がまだ弱い
- まずは安全側として、既存値を入れた編集フォームへ送るだけの helper が自然

## 3. 今回の範囲

- UI に `要見直し` helper button を追加する
- button は current review 件数を表示する
- click 時に最優先 review item を編集フォームへ入れる
- README / 設計書 / manual に反映する

## 4. 今回の範囲外

- review の一括更新
- 自動候補決定
- 複数 review の連続ナビゲーション UI

## 5. 機能要件

### 5.1 対象選定

- current `auditMap` の `status === review`
- 優先順は audit sort と同じく
  - `use_count` 昇順
  - `id` 昇順

### 5.2 button

- `要見直し n`
- 件数 0 の時は disabled

### 5.3 click 動作

- 先頭 review item をフォームへセット
- `orig`, `pref1`, `pref2`, `pref3`, `cat` を既存値で埋める
- `pref1` に focus
- helper が何をセットしたか短い通知を出す

## 6. 非機能要件

- データは更新しない
- 既存の手動追加フォームを壊さない
- helper DB の補助に留める

## 7. 完了条件

- UI から最優先 review item をすぐ編集フォームへ送れる
- count と disabled 状態が件数に追従する
