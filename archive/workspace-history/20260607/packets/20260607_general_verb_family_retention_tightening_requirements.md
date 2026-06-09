# Requirements

## Goal

single-word の一般動詞 family 候補は、複数回出てもまず `今は見送る` を優先し、short review から外しやすくする。

## Scope

- `veil-normalize.py` の retention / shortlist 判定
- `README.md`
- `docs/veil-design.md`
- `skills/codex/veil-capture/SKILL.md`
- `skills/claude-code/veil-capture.md`
- `index/project-current-work.md`

## Acceptance

- `update / updates` のような general verb family single-word は複数回でも `今は見送る`
- それに伴って `短い review から外す寄り` へ落ちる
- code / README / design / skills / current companion が同契約で一致する
