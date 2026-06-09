# Requirements

## Goal

`veil-normalize.py` の text 出力で non-low-priority `new-candidate` の level 補足行を compact にまとめ、review-first 出力の補足行をさらに減らす。

## Scope

- `veil-normalize.py`
- `README.md`
- `docs/veil-design.md`
- `skills/codex/veil-capture/SKILL.md`
- `skills/claude-code/veil-capture.md`
- `index/project-current-work.md`
- execution report

## Out Of Scope

- headline compact の再設計
- reason compact の再設計
- low-priority compact branch の再設計
- JSON 契約変更

## Acceptance

- non-low-priority `new-candidate` の `level 提案理由` が compact になる
- `表記ゆれ` と `書き込み候補` は維持
- low-priority / existing-match / JSON unchanged

