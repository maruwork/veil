# Requirements

## Goal

`veil-normalize.py` の non-low-priority `new-candidate` detail branch で、retention がない候補に限って `選別/review` と `判別/priority/level` を 1 行へまとめ、detail 行数をさらに減らす。

## Scope

- `veil-normalize.py`
- `README.md`
- `docs/veil-design.md`
- `skills/codex/veil-capture/SKILL.md`
- `skills/claude-code/veil-capture.md`
- `index/project-current-work.md`
- execution report

## Out Of Scope

- retention がある候補の detail branch 再設計
- low-priority branch の再設計
- existing-match branch の変更
- JSON 契約変更

## Acceptance

- retention がない non-low-priority `new-candidate` は `選別/review/判別/priority/level: ...` の 1 行になる
- retention がある候補は現行の `選別/review/保留` と `判別/priority/level` の 2 行を維持する
- low-priority branch unchanged
- existing-match unchanged
- JSON unchanged
