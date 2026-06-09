# Basic Design

## 1. Decision

- existing-match compact branch に source label の見やすさを足す
- group 内では new-candidate detail -> existing-match source-aware summary の順を維持する

## 2. Shape

- `- [existing-match] normalized`
- `  既存統合先: original -> preferred [level]`
- `  source: c.md`
- `  表記ゆれ: ...`

## 3. Boundary

- text renderer:
  - change
- JSON:
  - unchanged
