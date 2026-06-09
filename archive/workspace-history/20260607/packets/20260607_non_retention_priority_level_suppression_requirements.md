# Requirements

## Theme

VEIL tuning wave 38: non-retention priority/level suppression

## Goal

`veil-normalize.py` の non-retention branch から、headline と重複する `priority` と `level` を detail line から外して、さらに短くする。

## In Scope

- non-retention branch の text renderer
- `README.md`
- `docs/veil-design.md`
- `skills/codex/veil-capture/SKILL.md`
- `skills/claude-code/veil-capture.md`
- `index/project-current-work.md`

## Out Of Scope

- JSON contract change
- retention branch change
- low-priority branch change
- existing-match change
- heuristic / lint / sync / schema change

## Acceptance

- non-retention branch line が `選別/review/判別: ... | ... | ...` になる
- `priority` と `level` は text detail line から消える
- surface が同じ契約にそろう
