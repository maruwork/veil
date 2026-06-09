# Detailed Design

## 1. Rendering Contract

- low priority new-candidate:
  - compact branch
- high priority new-candidate:
  - detail branch

## 2. Compact Shape

- `- [new-candidate] normalized`
- `  level 提案: 観察`
- `  保留処理: 今は見送る`
- `  書き込み候補: ...`

## 3. Verification Conditions

- `close`, `closed`, `updates` は compact
- `summary`, `verification` は detail
- JSON unchanged
