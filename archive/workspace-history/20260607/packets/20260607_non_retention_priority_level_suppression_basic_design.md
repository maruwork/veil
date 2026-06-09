# Basic Design

## Intent

non-retention branch の `priority` と `level` は headline の `[level] x<count>` と役割が重なるので、detail から外す。

## Rendering

- before
  - `選別/review/判別/priority/level: selection_hint | shortlist_hint | classification_hint | priority_hint | suggested_level`
- after
  - `選別/review/判別: selection_hint | shortlist_hint | classification_hint`

## Invariants

- JSON unchanged
- retention branch unchanged
- headline unchanged
