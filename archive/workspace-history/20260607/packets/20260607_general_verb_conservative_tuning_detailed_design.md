# Detailed Design

## 1. Runtime Contract

- JSON key は増やさない
- 既存の
  - `classification_hint`
  - `selection_hint`
  - `retention_hint`
  を保ったまま、判定だけを保守側へ寄せる

## 2. Verb Family Rule

### 2.1 Base Set

- `close`
- `fix`
- `check`
- `update`
- `move`
- `start`
- `stop`
- `change`
- `build`
- `make`
- `use`

### 2.2 Inflection Handling

single-word lowercase 候補に対して次を吸収する。

- base
- `s`
- `es`
- `ed`
- `ing`

## 3. Decision Effect

- verb family hit の single-word は `説明語候補` へ寄せない
- 既定では `境界が曖昧な候補` または同等の保守分類へ寄せる
- `selection_hint` は `保留寄り` を維持する
- `retention_hint` は基本的に `今は見送る` を優先する

## 4. Verification Conditions

- `close`, `closed`, `closing`, `updates` が保守側へ出る
- `verification`, `summary` の既存挙動は壊れない
- docs / skills / current companion が追加保守 tuning を説明する
