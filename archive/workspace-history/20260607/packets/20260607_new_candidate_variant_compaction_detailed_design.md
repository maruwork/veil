# Detailed Design

## Rendering Contract

- non-low-priority `new-candidate` の `表記ゆれ` ラベルだけ compact
- low-priority compact branch は変更しない
- existing-match branch は変更しない

## Compact Shape

- `variants: <variant xN, ...>`

## Verification Conditions

- `summary` のような non-low-priority 候補で `variants: summary x2` が出る
- `close` のような low-priority compact branch は維持
- existing-match branch unchanged
- JSON unchanged

