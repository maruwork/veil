# Requirements

## Theme

VEIL tuning wave 36: detail reason suppression

## Goal

`veil-normalize.py` の non-low-priority `new-candidate` で、text 出力から長い理由文を外し、hint 中心の compact 表示へ寄せる。

## In Scope

- non-low-priority `new-candidate` text renderer
- `README.md`
- `docs/veil-design.md`
- `skills/codex/veil-capture/SKILL.md`
- `skills/claude-code/veil-capture.md`
- `index/project-current-work.md`

## Out Of Scope

- JSON contract change
- low-priority branch change
- existing-match change
- heuristic / lint / sync / schema change

## Acceptance

- retention あり branch の `selection_reason` / `classification_reason` が text 出力から消える
- retention なし branch の `selection_reason` が text 出力から消える
- hint 系 label は維持する
- surface が同じ契約にそろう
