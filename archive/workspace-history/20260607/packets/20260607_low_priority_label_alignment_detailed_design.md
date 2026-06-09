# Detailed Design

## Rendering Contract

- low-priority compact branch の最後の行だけ label を揃える
- non-low-priority branch は変更しない

## Compact Shape

- `target: <file>`

## Verification Conditions

- `close` のような low-priority 候補で `target: c.md` が出る
- `summary` のような non-low-priority 候補は unchanged
- JSON unchanged

