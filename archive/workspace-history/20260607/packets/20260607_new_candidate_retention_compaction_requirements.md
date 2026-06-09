# Requirements

## Goal

`veil-normalize.py` の text 出力で non-low-priority `new-candidate` の保留補足行を compact にまとめ、保留候補の読み行数を減らす。

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
- level 補足 compact の再設計
- low-priority compact branch の再設計
- JSON 契約変更

## Acceptance

- non-low-priority `new-candidate` の `保留処理` と `保留理由` が compact になる
- `表記ゆれ`、`level`、`書き込み候補` は維持
- low-priority / existing-match / JSON unchanged

