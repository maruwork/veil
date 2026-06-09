# Detailed Design

## Rendering Contract

- low-priority ではない `new-candidate` だけ headline compact 対象
- headline は `normalized / level / count`
- 既存 detail 行は維持

## Compact Shape

- `- [new-candidate] normalized [level] x<count>`

## Verification Conditions

- `summary` のような non-low-priority 候補で headline compact が出る
- `close` のような low-priority compact branch は維持
- `existing-match` branch unchanged
- JSON unchanged

