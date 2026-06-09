# Requirements

## Theme

VEIL tuning wave 34: low-priority headline target compaction

## Goal

`veil-normalize.py` の low-priority `new-candidate` を 3 行から 2 行へ圧縮し、短い review の後段をさらに読み飛ばしやすくする。

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

- low-priority branch の headline 末尾へ `| <target>` を寄せる
- low-priority branch の独立 `target:` 行が消える
- surface が同じ契約にそろう
