# Detailed Design

## Rendering Contract

- non-low-priority `new-candidate` の `書き込み候補` ラベルだけ compact
- low-priority compact branch は変更しない

## Compact Shape

- `target: <file>`

## Verification Conditions

- `summary` のような non-low-priority 候補で `target: s.md` が出る
- `close` のような low-priority compact branch は維持
- existing-match branch unchanged
- JSON unchanged

