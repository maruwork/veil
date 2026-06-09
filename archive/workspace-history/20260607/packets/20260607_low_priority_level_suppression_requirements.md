# low-priority level suppression requirements

## Goal

`veil-normalize.py` の low-priority `new-candidate` 行から固定表示になっている level を外し、`normalized | target | 保留処理` へ縮約する。

## Scope

- `veil-normalize.py` の low-priority compact line
- `README.md`
- `docs/veil-design.md`
- `skills/codex/veil-capture/SKILL.md`
- `skills/claude-code/veil-capture.md`
- `index/project-current-work.md`
- execution report

## Out Of Scope

- low-priority 判定条件変更
- JSON 契約変更
- non-low-priority branch 変更
- existing-match branch 変更

## Acceptance

- low-priority 行が `normalized | target | 今は見送る` の形になる
- JSON では `suggested_level` を維持する
- docs / skills / current companion が同契約へそろう
- compile / smoke / readback が通る
