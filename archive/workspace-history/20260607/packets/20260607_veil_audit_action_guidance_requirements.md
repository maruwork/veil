# VEIL audit action guidance 要件

Status: Draft
Date: 2026-06-07

## 1. 目的

`veil-audit-db.py` の監査結果に、helper DB を見直す時の次アクションを添えて、人が迷わず棚卸しできるようにする。

## 2. 背景

- 現在の監査結果は `keep / review / drop-candidate` と理由までは返せる
- しかし実際に何をすればよいかは文脈依存で、特に `review` の扱いがぶれやすい
- helper DB は正本ではないため、自動 cleanup ではなく、人の判断を支える軽い行動指針が合う

## 3. 今回の範囲

- `veil-audit-db.py` の各結果に `suggested_action` を追加する
- 必要なら `review_focus` を追加し、何を見直すか短く返す
- README / 設計書 / manual に、status ごとの手動処理順を追記する

## 4. 今回の範囲外

- DB の自動更新
- UI 上での audit 実行
- review 判定ロジック全体の再設計

## 5. 機能要件

### 5.1 suggested_action

- `keep`
  - そのまま維持
- `review`
  - 候補1、カテゴリ、用途を見直す
- `drop-candidate`
  - helper DB からの削除を検討する

### 5.2 review_focus

少なくとも次の焦点を返せるようにする。

- 候補1が空
- `cat` と判別補助がずれる
- 単語単体で意味が広い
- 境界が曖昧
- `project 固有語` なので手動判断

### 5.3 出力面

- text 出力で `次アクション` を表示する
- json 出力で `suggested_action` と `review_focus` を含める

## 6. 非機能要件

- 非破壊性を崩さない
- 「提案」であって authority ではないことを保つ
- 文書では UI の既存 delete / upsert 導線にだけ接続する

## 7. 完了条件

- `veil-audit-db.py` の text / json 出力に行動指針が入る
- README / 設計書 / manual で status ごとの扱い方が分かる
