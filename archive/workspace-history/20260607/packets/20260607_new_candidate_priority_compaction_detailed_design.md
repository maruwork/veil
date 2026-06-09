# Detailed Design

## Rendering Contract

- non-low-priority `new-candidate` の `頻度目安` ラベルだけ compact
- low-priority compact branch は変更しない

## Compact Shape

- `priority: <hint>`

## Verification Conditions

- `summary` のような non-low-priority 候補で `priority: 次に見る` が出る
- `close` のような low-priority compact branch は維持
- existing-match branch unchanged
- JSON unchanged

