# Basic Design

## 1. Decision

- report の節構造は維持する
  - `採用:`
  - `保留:`
  - `同期:`
  - `返答前検査:`
- ただし行の情報量は絞る

## 2. New Report Shape

### 2.1 採用

基本形:

- `- [level] term → 候補1`

候補2 / 候補3 が本当に必要な時だけ:

- `- [level] term → 候補1 | 補助候補: 候補2, 候補3`

### 2.2 保留

- 保留がある時だけ節を出す
- 基本形:
  - `- term`

### 2.3 同期

- 成功:
  - `- sync 完了`
- 未実行 / 停止:
  - 理由だけ短く 1 行

### 2.4 返答前検査

- 基本固定:
  - `- main task の日本語文章は別途 lint 対象`

## 3. Rejected Alternatives

- JSON 的な詳細 report にする
  - rejected: 日常運用では重い
- 候補2 / 候補3 を常時落とす
  - rejected: 迷いが残る場面では補助候補が必要

