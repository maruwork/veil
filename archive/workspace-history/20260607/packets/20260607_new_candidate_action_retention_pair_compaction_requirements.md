# Requirements

## Goal

`veil-normalize.py` の non-low-priority `new-candidate` detail branch で分かれている `選別/review` と `保留` を 1 行へまとめ、保持判断の流れをさらに短く読む。

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

- non-low-priority `new-candidate` の text 出力で retention がある場合、`選別/review` と `保留` が 1 行にまとまる
- retention がない場合は `選別/review` 単独のまま読める
- `判別` は独立行のまま残る
- low-priority branch unchanged
- existing-match unchanged
- JSON unchanged
