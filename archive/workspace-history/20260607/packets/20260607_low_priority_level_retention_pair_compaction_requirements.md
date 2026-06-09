# Requirements

## Goal

`veil-normalize.py` の low-priority branch で分かれている `level 提案` と `保留処理` を 1 行へまとめ、保守側の読み行数をさらに減らす。

## Scope

- `veil-normalize.py`
- `README.md`
- `docs/veil-design.md`
- `skills/codex/veil-capture/SKILL.md`
- `skills/claude-code/veil-capture.md`
- `index/project-current-work.md`
- execution report

## Out Of Scope

- non-low-priority branch の再設計
- existing-match branch の変更
- JSON 契約変更

## Acceptance

- low-priority branch の `level 提案` と `保留処理` が `level/保留処理: ... | ...` の 1 行になる
- low-priority branch の `target` 行は維持する
- non-low-priority branch unchanged
- existing-match unchanged
- JSON unchanged
