# Basic Design

## Intent

low-priority `new-candidate` は `normalized` と `level/保留処理` だけ見ればよいので、`target` は headline に寄せる。

## Rendering

- before
  - `- [new-candidate] close`
  - `  level/保留処理: 観察 | 今は見送る`
  - `  target: c.md`
- after
  - `- [new-candidate] close | c.md`
  - `  level/保留処理: 観察 | 今は見送る`

## Invariants

- JSON unchanged
- non-low-priority unchanged
- existing-match unchanged
