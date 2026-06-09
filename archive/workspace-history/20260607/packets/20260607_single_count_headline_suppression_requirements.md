# single-count headline suppression requirements

## Goal

`veil-normalize.py` の non-low-priority `new-candidate` headline で、出現回数が `1` の時だけ `x1` を省く。

## Scope

- `veil-normalize.py` の non-low-priority headline
- `README.md`
- `docs/veil-design.md`
- `skills/codex/veil-capture/SKILL.md`
- `skills/claude-code/veil-capture.md`
- `index/project-current-work.md`
- execution report

## Out Of Scope

- `count > 1` の headline 変更
- JSON 契約変更
- low-priority branch 変更
- existing-match branch 変更

## Acceptance

- `count = 1` の headline は `normalized [level] | <target>` になる
- `count > 1` の headline は `x<count>` を維持する
- docs / skills / current companion が同契約へそろう
- compile / smoke / readback が通る
