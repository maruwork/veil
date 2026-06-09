# Requirements

## Theme

VEIL tuning wave 9: review-first output compaction

## Goal

`veil-normalize.py` の text 出力で、`短い review に残す` 候補を先にまとめて読めるようにする。

## Scope In

- `veil-normalize.py`
- `README.md`
- `docs/veil-design.md`
- `skills/codex/veil-capture/SKILL.md`
- `skills/claude-code/veil-capture.md`
- `index/project-current-work.md`

## Scope Out

- JSON contract change
- schema change
- lint runtime
- UI

## Required Outcome

1. text 出力が `短い review に残す` を先頭に出す
2. `短い review から外す寄り` は後段へまとまる
3. JSON 契約は維持する
4. docs / skills / current companion が compact review-first を共有する

## Acceptance

- A1: text 出力に 2 つの grouping が出る
- A2: `summary` や `verification` が前段に来る
- A3: `close` や `status=close` が後段に来る
- A4: JSON output は構造不変
