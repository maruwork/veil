# VEIL vocab.db 監査補助 基本設計

Status: Draft
Date: 2026-06-07

## 1. 目的

helper DB を壊さずに現状把握できるようにし、cleanup を安全に進めやすくする。

## 2. 境界

- 対象:
  - 新規 root script `veil-audit-db.py`
  - `README.md`
  - `docs/veil-design.md`
  - `docs/manual.html`
- 非対象:
  - DB 更新
  - `app.py`
  - `~/.veil/rules/`

## 3. 主要設計

### 3.1 現行 seed 集合を基準に使う

`app.py` の現行 `SEEDS` の original 一覧を基準集合として再利用する。

### 3.2 軽い監査規則

監査区分は次で決める。

- `keep`
  - current seed に含まれる
  - または `use_count >= 3`
- `review`
  - `use_count` が低い
  - 単語単体
  - cat と判別補助がずれる
  - 候補1なし
- `drop-candidate`
  - `use_count == 0`
  - current seed に含まれない
  - 判別補助が `境界が曖昧な候補` または `識別子候補`
  - 候補1が空、または helper 初期集合として弱い

### 3.3 判別補助の再利用

可能な範囲で `veil-normalize.py` と同方向の判別補助を使う。
今回は script 間 import で十分。

## 4. 却下する案

- 監査と同時に DB を掃除する
  - 破壊的で早すぎるため不採用
- UI 内に監査ロジックを直接埋める
  - まずは CLI 補助で十分
