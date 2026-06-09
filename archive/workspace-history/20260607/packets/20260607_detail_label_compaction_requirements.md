# detail label compaction requirements

## Goal

`veil-normalize.py` の detail line label を短縮し、`選別/保留/判別` と `選別/判別` をより軽い表記へ寄せる。

## Scope

- `veil-normalize.py` の non-low-priority detail line label
- `README.md`
- `docs/veil-design.md`
- `skills/codex/veil-capture/SKILL.md`
- `skills/claude-code/veil-capture.md`
- `index/project-current-work.md`
- execution report

## Out Of Scope

- detail line の値や順序の変更
- low-priority branch の変更
- JSON 契約変更
- existing-match branch の変更

## Acceptance

- retention あり line が短い label に変わる
- retention なし line も短い label に変わる
- 値の並び順は維持される
- docs / skills / current companion が同契約へそろう
- compile / smoke / readback が通る
