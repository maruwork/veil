# VEIL vocab.db 監査補助 要件

Status: Draft
Date: 2026-06-07

## 1. 目的

既存 `vocab.db` がある時に、非破壊で「残す」「見直す」「外す候補」を監査できる補助を追加する。

## 2. 背景

- 現在の repo には `vocab.db` が存在しないため、実掃除はできない
- しかし今後 user 環境に既存 `vocab.db` がある場合、旧 seed や曖昧語を監査する手段が必要
- helper DB は正本ではないが、UI 運用のノイズを減らすには見直し補助が有効

## 3. 今回の範囲

- `vocab.db` を読むだけの監査スクリプトを追加する
- 監査結果として、少なくとも `keep / review / drop-candidate` を返す
- text / json 出力を持つ
- README / 設計書 / manual に補助の位置づけを追記する

## 4. 今回の範囲外

- `vocab.db` の自動書き換え
- `~/.veil/rules/` への自動反映
- `app.py` の UI から直接 cleanup 実行

## 5. 機能要件

### 5.1 監査対象

- 既存の `vocab.db`
- 既定 path は repo 直下
- 任意 path の上書き指定もできる

### 5.2 監査観点

少なくとも次の観点で判定材料を返す。

- seed 現行集合と一致するか
- use_count
- cat
- 原語の判別補助
- 候補1の有無

### 5.3 出力区分

- `keep`
  - 現行 seed に含まれる、または use_count が高い、または説明語として安定
- `review`
  - use_count が低い、境界が曖昧、単語単体、cat と判別補助がずれる
- `drop-candidate`
  - 未使用で、旧 seed 由来または曖昧で、helper DB の初期集合としては残す価値が薄い

### 5.4 非破壊

- DB は絶対に更新しない
- 監査結果は標準出力に出すだけにする

## 6. 非機能要件

- helper DB の監査であり、正本判定とは混同しない
- 日本語説明を優先する

## 7. 完了条件

- `vocab.db` がある時に監査結果を text / json で取れる
- `vocab.db` が無い時は分かりやすく `skip` できる
