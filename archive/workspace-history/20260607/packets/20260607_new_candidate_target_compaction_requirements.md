# Requirements

## Goal

`veil-normalize.py` の text 出力で non-low-priority `new-candidate` の書き込み候補行を compact にまとめ、候補確認の読み行数を減らす。

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
- reason / level / retention / variant compact の再設計
- low-priority compact branch の再設計
- JSON 契約変更

## Acceptance

- non-low-priority `new-candidate` の `書き込み候補` 行が compact になる
- low-priority / existing-match / JSON unchanged

