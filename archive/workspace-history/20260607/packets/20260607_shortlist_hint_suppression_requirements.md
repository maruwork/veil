# Requirements

## Theme

VEIL tuning wave 39: shortlist hint suppression

## Goal

`veil-normalize.py` の detail line から `shortlist_hint` を外し、group header と重複する情報を減らす。

## In Scope

- retention branch text detail line
- non-retention branch text detail line
- `README.md`
- `docs/veil-design.md`
- `skills/codex/veil-capture/SKILL.md`
- `skills/claude-code/veil-capture.md`
- `index/project-current-work.md`

## Out Of Scope

- JSON contract change
- headline change
- low-priority branch change
- existing-match change
- heuristic / lint / sync / schema change

## Acceptance

- retention branch から `review hint` が消える
- non-retention branch から `review hint` が消える
- group header を見れば十分という契約にそろう
