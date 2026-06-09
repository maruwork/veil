# Detailed Design

## Rendering Contract

- non-low-priority `new-candidate` で retention がある時だけ compact
- low-priority compact branch は変更しない

## Compact Shape

- `保留: <hint> | <reason>`

## Verification Conditions

- `verification` のような候補で `保留: 後で再観察する | ...` が出る
- `close` のような low-priority compact branch は維持
- `existing-match` branch unchanged
- JSON unchanged

