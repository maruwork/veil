# Requirements

## Theme

VEIL tuning wave 41: existing-match source count suppression

## Goal

`veil-normalize.py` の `existing-match` source header から `(N件)` を外し、source file 名だけを見る契約へ寄せる。

## In Scope

- `existing-match` grouped source header
- `README.md`
- `docs/veil-design.md`
- `skills/codex/veil-capture/SKILL.md`
- `skills/claude-code/veil-capture.md`
- `index/project-current-work.md`

## Out Of Scope

- JSON contract change
- item line change
- new-candidate branch change
- heuristic / lint / sync / schema change

## Acceptance

- grouped source header が `source: <file>` になる
- `(N件)` が出なくなる
- surface が同じ契約にそろう
