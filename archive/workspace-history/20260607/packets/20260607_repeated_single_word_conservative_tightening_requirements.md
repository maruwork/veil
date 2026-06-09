# Requirements

## Goal

single-word の一般語は、2 回出現しただけでは自動で `説明語候補 / 先に採る候補 / 推奨` へ上げすぎないようにする。

## Scope

- `veil-normalize.py` の single-word lowercase 判定
- `README.md`
- `docs/veil-design.md`
- `skills/codex/veil-capture/SKILL.md`
- `skills/claude-code/veil-capture.md`
- `index/project-current-work.md`

## Acceptance

- `request / requests` のような repeated single-word 一般語は 2 回出現だけでは `説明語候補` に自動昇格しない
- それに伴い `先に採る候補 / 推奨` から外れる
- code / README / design / skills / current companion が同契約で一致する
