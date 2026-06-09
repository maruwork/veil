# Basic Design

## Intent

retention あり branch は hint-only になったので、もう 2 行に分ける必要が薄い。1 行へ寄せて review をさらに速くする。

## Rendering

- before
  - `選別/review/保留: selection_hint | shortlist_hint | retention_hint`
  - `判別/priority/level: classification_hint | priority_hint | suggested_level`
- after
  - `選別/review/保留/判別/priority/level: selection_hint | shortlist_hint | retention_hint | classification_hint | priority_hint | suggested_level`

## Invariants

- JSON unchanged
- headline / variants / target contract unchanged
- non-retention branch unchanged
