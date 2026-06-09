# Detailed Design

## Touch Point

- `veil-normalize.py`
  - `print_text_result`
  - non-low-priority `new-candidate` branch only

## Change

- text renderer から `selection_reason` と `classification_reason` を外す
- data structure は変更しない

## Surface Writeback

- docs and skills describe text output as hint-only
