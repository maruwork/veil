# Requirements

## Theme

VEIL tuning wave 37: retention branch single-line compaction

## Goal

`veil-normalize.py` の retention あり detail branch を 2 行から 1 行へ圧縮し、non-retention branch に近い読み味へ寄せる。

## In Scope

- retention あり non-low-priority `new-candidate` text renderer
- `README.md`
- `docs/veil-design.md`
- `skills/codex/veil-capture/SKILL.md`
- `skills/claude-code/veil-capture.md`
- `index/project-current-work.md`

## Out Of Scope

- JSON contract change
- low-priority branch change
- existing-match change
- non-retention branch change
- heuristic / lint / sync / schema change

## Acceptance

- retention あり branch が 1 行になる
- 独立の `判別/priority/level` 行が消える
- surface が同じ契約にそろう
