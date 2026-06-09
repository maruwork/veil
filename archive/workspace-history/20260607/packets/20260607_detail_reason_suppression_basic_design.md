# Basic Design

## Intent

detail branch の理由文は長く、短い review の可読性を下げる。text では hint だけを残し、理由は JSON にだけ残す。

## Rendering

- retention あり
  - before
    - `選別/review/保留: selection_hint | selection_reason | shortlist_hint | retention_hint`
    - `判別/priority/level: classification_hint | classification_reason | priority_hint | suggested_level`
  - after
    - `選別/review/保留: selection_hint | shortlist_hint | retention_hint`
    - `判別/priority/level: classification_hint | priority_hint | suggested_level`
- retention なし
  - before
    - `選別/review/判別/priority/level: selection_hint | selection_reason | shortlist_hint | classification_hint | priority_hint | suggested_level`
  - after
    - `選別/review/判別/priority/level: selection_hint | shortlist_hint | classification_hint | priority_hint | suggested_level`

## Invariants

- JSON unchanged
- headline / variants / target contract unchanged
