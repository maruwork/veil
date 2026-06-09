# Basic Design

## Intent

low-priority branch は採用対象ではないため、1 行で十分に読む。

## Rendering

- before
  - `- [new-candidate] close | c.md`
  - `  level/保留処理: 観察 | 今は見送る`
- after
  - `- [new-candidate] close | c.md | 観察 | 今は見送る`

## Invariants

- JSON unchanged
- non-low-priority unchanged
- existing-match unchanged
