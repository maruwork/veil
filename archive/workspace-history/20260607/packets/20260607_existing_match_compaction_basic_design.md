# Basic Design

## 1. Decision

- `veil-normalize.py` の text renderer だけで `existing-match` を compact 表示にする
- 新規候補の詳細ブロックは維持する

## 2. Compact Shape

- `- [existing-match] normalized`
- `  既存統合先: original -> preferred [level] (source_file)`
- `  表記ゆれ: ...`

## 3. Boundary

- text renderer:
  - change
- JSON:
  - unchanged

## 4. Rejected Alternatives

- existing-match を完全に隠す
  - rejected: 統合先確認の evidence が落ちる
- JSON も短縮する
  - rejected: caller 互換を壊す
