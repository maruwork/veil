# Detailed Design

## Rendering Contract

- headline は wave 16 のまま維持
- non-low-priority `new-candidate` の対になる理由行だけ compact
- low-priority compact branch は変更しない

## Compact Shape

- `選別: <hint> | <reason>`
- `review: <hint> | <reason>`
- `判別: <hint> | <reason>`

## Verification Conditions

- `summary` のような non-low-priority 候補で compact reason lines が出る
- `close` のような low-priority compact branch は維持
- `existing-match` branch unchanged
- JSON unchanged

