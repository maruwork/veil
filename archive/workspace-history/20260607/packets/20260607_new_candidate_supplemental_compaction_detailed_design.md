# Detailed Design

## Rendering Contract

- non-low-priority `new-candidate` の `level 提案理由` を compact
- headline は wave 16 のまま維持
- reason compact は wave 17 のまま維持

## Compact Shape

- `level: <level> | <reason>`

## Verification Conditions

- `summary` のような non-low-priority 候補で `level: 推奨 | ...` が出る
- `close` のような low-priority compact branch は維持
- `existing-match` branch unchanged
- JSON unchanged

