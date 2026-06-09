# Detailed Design

## Touch Point

- `veil-normalize.py`
  - `print_text_result`
  - low-priority compact branch only

## Change

- `print(f\"- [{item['status']}] {item['normalized']}\")`
  - to
  - `print(f\"- [{item['status']}] {item['normalized']} | {item['target_file']}\")`
- remove low-priority branch `target:` line

## Surface Writeback

- docs and skills describe low-priority branch as 2 lines
