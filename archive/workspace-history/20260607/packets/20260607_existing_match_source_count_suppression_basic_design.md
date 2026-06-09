# Basic Design

## Intent

`existing-match` の grouped source は header 配下の行数で把握できるため、件数表示を繰り返さない。

## Rendering

- before
  - `source: c.md (2件)`
- after
  - `source: c.md`

## Invariants

- single-source suffix behavior unchanged
- item lines unchanged
- JSON unchanged
