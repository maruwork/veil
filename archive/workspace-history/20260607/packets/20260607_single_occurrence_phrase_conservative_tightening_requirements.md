# Requirements

## Goal

single-occurrence の lowercase phrase は、自動で `説明語候補` へ上げすぎず、まず保守側に残す。

## Scope

- `veil-normalize.py` の lowercase phrase 判定
- `README.md`
- `docs/veil-design.md`
- `skills/codex/veil-capture/SKILL.md`
- `skills/claude-code/veil-capture.md`
- `index/project-current-work.md`

## Acceptance

- `request map` や `risk report` のような single-occurrence lowercase phrase は自動で `説明語候補` にならない
- repeated phrase や noun-like 語は既存の昇格余地を維持する
- code / README / design / skills / current companion が同契約で一致する
