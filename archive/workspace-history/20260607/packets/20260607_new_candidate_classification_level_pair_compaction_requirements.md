# Requirements

## Goal

`veil-normalize.py` の non-low-priority `new-candidate` detail branch で分かれている `判別` と `priority/level` を 1 行へまとめ、分類面の読み行数をさらに減らす。

## Scope

- `veil-normalize.py`
- `README.md`
- `docs/veil-design.md`
- `skills/codex/veil-capture/SKILL.md`
- `skills/claude-code/veil-capture.md`
- `index/project-current-work.md`
- execution report

## Out Of Scope

- low-priority branch の再設計
- existing-match branch の変更
- JSON 契約変更

## Acceptance

- non-low-priority `new-candidate` の text 出力で `判別` と `priority/level` が 1 行にまとまる
- action 系の `選別/review` 系は現行維持
- low-priority branch unchanged
- existing-match unchanged
- JSON unchanged
