# Basic Design

## Intent

retention branch の `priority` と `level` も headline と役割が重なるため、detail から外す。

## Rendering

- before
  - `選別/保留/判別/priority/level: selection_hint | retention_hint | classification_hint | priority_hint | suggested_level`
- after
  - `選別/保留/判別: selection_hint | retention_hint | classification_hint`

## Invariants

- JSON unchanged
- headline unchanged
- non-retention branch unchanged
