# Requirements

## Goal

`veil-normalize.py` の non-low-priority `new-candidate` detail branch で分かれている `priority` と `level` を 1 行へまとめ、review 時の読み行数をさらに減らす。

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

- non-low-priority `new-candidate` の text 出力で `priority` と `level` が 1 行にまとまる
- low-priority branch unchanged
- existing-match unchanged
- JSON unchanged
