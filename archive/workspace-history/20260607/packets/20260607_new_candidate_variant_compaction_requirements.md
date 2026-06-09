# Requirements

## Goal

`veil-normalize.py` の text 出力で non-low-priority `new-candidate` の表記ゆれ行を compact にまとめ、候補確認の読み行数を減らす。

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
- reason / level / retention compact の再設計
- low-priority compact branch の再設計
- JSON 契約変更

## Acceptance

- non-low-priority `new-candidate` の `表記ゆれ` 行が compact になる
- `書き込み候補` は維持
- low-priority / existing-match / JSON unchanged

