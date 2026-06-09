# Requirements

## Theme

VEIL tuning wave 40: retention priority/level suppression

## Goal

`veil-normalize.py` の retention branch から、headline と重複する `priority` と `level` を detail line から外してさらに短くする。

## In Scope

- retention branch の text renderer
- `README.md`
- `docs/veil-design.md`
- `skills/codex/veil-capture/SKILL.md`
- `skills/claude-code/veil-capture.md`
- `index/project-current-work.md`

## Out Of Scope

- JSON contract change
- non-retention branch change
- low-priority branch change
- existing-match change
- heuristic / lint / sync / schema change

## Acceptance

- retention branch line が `選別/保留/判別: ... | ... | ...` になる
- `priority` と `level` は retention detail line から消える
- surface が同じ契約にそろう
