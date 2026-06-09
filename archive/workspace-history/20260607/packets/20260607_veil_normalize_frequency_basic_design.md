# VEIL 正規化頻度補助 基本設計

Status: Draft
Date: 2026-06-07

## 1. 目的

`veil-normalize.py` を、単なる揺れ統合表示から、段階導入の採用順判断を補助する道具へ拡張する。

## 2. 境界

- 対象:
  - `veil-normalize.py`
  - `README.md`
  - `docs/veil-design.md`
  - `skills/codex/veil-capture/SKILL.md`
  - `skills/claude-code/veil-capture.md`
- 非対象:
  - UI runtime
  - `veil-lint.py`
  - rules file 実データ

## 3. 主要設計

### 3.1 重複を消す場所を遅らせる

現状は入力行の段階で重複を消している。これをやめ、候補一覧は重複込みで保持する。

そのうえで、cluster 時に

- normalized key ごとの合計出現回数
- variant ごとの出現回数

を集計する。

### 3.2 頻度目安を返す

頻度だけに基づく軽い目安を返す。

- 3回以上: `先に見る`
- 2回: `次に見る`
- 1回: `保留候補`

これは困り度を決めるものではなく、採用順の最初の足場として使う。

### 3.3 出力の見せ方

text 出力:

- status
- normalized key
- 合計出現回数
- 頻度目安
- variant ごとの回数
- 既存統合先または書き込み候補

json 出力:

- `occurrence_count`
- `priority_hint`
- `variant_counts`

を各 result に含める。

## 4. 却下する案

- 困り度まで自動判定する
  - 文脈依存が大きく、今回の範囲を超えるため不採用
- 新しい別スクリプトを作る
  - まずは `veil-normalize.py` の責務拡張で足りるため不採用
