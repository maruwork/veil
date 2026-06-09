# Requirements

## Theme

VEIL tuning wave 11: candidate-first ordering

## Goal

`veil-normalize.py` の text 出力で、各 group の中でも新規候補を先、existing-match を後に並べる。

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

1. 各 text group の中で `new-candidate` が先に来る
2. `existing-match` は後段へ回る
3. JSON 契約は維持する
4. docs / skills / current companion が candidate-first ordering を共有する
