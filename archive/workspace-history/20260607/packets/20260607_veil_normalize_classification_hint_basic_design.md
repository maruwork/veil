# VEIL 正規化判別補助 基本設計

Status: Draft
Date: 2026-06-07

## 1. 目的

`veil-normalize.py` の出力を、頻度補助に加えて判別補助にも使えるようにする。

## 2. 境界

- 対象:
  - `veil-normalize.py`
  - `README.md`
  - `docs/veil-design.md`
  - `skills/codex/veil-capture/SKILL.md`
  - `skills/claude-code/veil-capture.md`
- 非対象:
  - UI 自動推定ロジック
  - runtime DB
  - `project 固有語` の完全自動判定

## 3. 主要設計

### 3.1 代表表記ベースで補助判定する

cluster ごとの代表表記を使って軽い補助判定を行う。

主な規則:

- パス区切り、拡張子、`key=value`、ALL_CAPS、ticket id 風は `識別子候補`
- camelCase や内部大文字は `固有名候補`
- 小文字中心の自然な語句は `説明語候補`
- 規則が交差する、またはどれにも強く当たらない時は `境界が曖昧な候補`

### 3.2 理由を返す

text / json ともに、短い理由を返す。

例:

- `パスまたは拡張子に見える`
- `key=value に見える`
- `内部大文字を含む`
- `小文字中心の一般語句に見える`
- `判定規則が交差する`

### 3.3 慎重側へ倒す

project 固有語は自動で決めない。判断に迷う時は `境界が曖昧な候補` を返す。

## 4. 却下する案

- DB の `cat` 推定と同じロジックをここへ複製する
  - 責務が重くなるため不採用
- project 固有語を単語辞書で自動判定する
  - 維持コストと誤判定が大きいため不採用
