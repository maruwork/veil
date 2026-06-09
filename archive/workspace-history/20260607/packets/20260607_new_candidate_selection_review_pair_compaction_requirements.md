# Requirements

## Goal

`veil-normalize.py` の non-low-priority `new-candidate` detail branch で分かれている `選別` と `review` を 1 行へまとめ、review 時の読み行数をさらに減らす。

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

- non-low-priority `new-candidate` の text 出力で `選別` と `review` が 1 行にまとまる
- `判別` は独立行のまま残る
- low-priority branch unchanged
- existing-match unchanged
- JSON unchanged
