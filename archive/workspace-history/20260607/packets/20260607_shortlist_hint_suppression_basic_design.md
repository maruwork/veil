# Basic Design

## Intent

`短い review に残す / 短い review から外す寄り` は group header ですでに見えているため、detail line で繰り返さない。

## Rendering

- retention branch
  - before
    - `選別/review/保留/判別/priority/level: selection_hint | shortlist_hint | retention_hint | classification_hint | priority_hint | suggested_level`
  - after
    - `選別/保留/判別/priority/level: selection_hint | retention_hint | classification_hint | priority_hint | suggested_level`
- non-retention branch
  - before
    - `選別/review/判別: selection_hint | shortlist_hint | classification_hint`
  - after
    - `選別/判別: selection_hint | classification_hint`

## Invariants

- JSON unchanged
- group header unchanged
