# Requirements

## Theme

VEIL tuning wave 12: existing-match source summary

## Goal

`veil-normalize.py` の text 出力で、existing-match を source-aware に短く流せるようにする。

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

1. existing-match が source file を含む compact 要約としてまとまる
2. new-candidate 詳細は維持する
3. JSON 契約は維持する
4. docs / skills / current companion が source-aware summary 契約を共有する
