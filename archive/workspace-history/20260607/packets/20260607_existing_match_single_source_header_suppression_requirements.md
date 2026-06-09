# Requirements

## Goal

`veil-normalize.py` の `existing-match` で、source file 配下が 1 件だけの時は独立 source header を出さず、行末へ source file を添えて compact にする。

## Scope

- `veil-normalize.py`
- `README.md`
- `docs/veil-design.md`
- `skills/codex/veil-capture/SKILL.md`
- `skills/claude-code/veil-capture.md`
- `index/project-current-work.md`
- execution report

## Out Of Scope

- multi-item source grouping の変更
- new-candidate branch の変更
- JSON 契約変更

## Acceptance

- `existing-match` が 1 件だけの source file では `source: ... (1件)` 行を出さない
- その場合は `existing-match` の行末へ `| source: <file>` を付ける
- 同一 source に複数件ある場合は現行の source header grouping を維持する
- JSON unchanged
