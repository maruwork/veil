# Basic Design

## Intent

detail branch では `target: ...` を使っているが、low-priority branch だけ `書き込み候補` が残っている。意味を変えず label を統一する。

## Chosen Shape

- low-priority branch:
  - `target: c.md`

## Non-Goals

- low-priority compact branch の4行構成変更
- target 情報の削除
- JSON compact 化

