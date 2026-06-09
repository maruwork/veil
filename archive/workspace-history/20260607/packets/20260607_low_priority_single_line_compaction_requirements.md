# Requirements

## Theme

VEIL tuning wave 35: low-priority single-line compaction

## Goal

`veil-normalize.py` の low-priority `new-candidate` を 2 行から 1 行へ圧縮し、後段 review をさらに読み飛ばしやすくする。

## In Scope

- low-priority branch の text renderer
- `README.md`
- `docs/veil-design.md`
- `skills/codex/veil-capture/SKILL.md`
- `skills/claude-code/veil-capture.md`
- `index/project-current-work.md`

## Out Of Scope

- JSON contract change
- non-low-priority branch change
- existing-match change
- normalize heuristic / lint / sync / schema change

## Acceptance

- low-priority branch が `normalized | target | level | 保留処理` の 1 行になる
- 独立の `level/保留処理` 行が消える
- surface が同じ契約にそろう
