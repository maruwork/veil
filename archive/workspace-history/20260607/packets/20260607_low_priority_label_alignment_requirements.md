# Requirements

## Goal

`veil-normalize.py` の low-priority compact branch で残っている `書き込み候補` を `target` へそろえ、mainline detail branch と出力契約を揃える。

## Scope

- `veil-normalize.py`
- `README.md`
- `docs/veil-design.md`
- `skills/codex/veil-capture/SKILL.md`
- `skills/claude-code/veil-capture.md`
- `index/project-current-work.md`
- execution report

## Out Of Scope

- low-priority 判定条件の変更
- mainline detail branch の再設計
- JSON 契約変更

## Acceptance

- low-priority compact branch の最後の行が `target: <file>` になる
- non-low-priority branch unchanged
- existing-match unchanged
- JSON unchanged

