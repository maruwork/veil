# Requirements

## Goal

`existing-match` に source group が 1 つしかない時は独立 file header を出さず、item 行末の file suffix だけで読めるようにする。

## Scope

- `veil-normalize.py` の `existing-match` text 出力
- `README.md`
- `docs/veil-design.md`
- `skills/codex/veil-capture/SKILL.md`
- `skills/claude-code/veil-capture.md`
- `index/project-current-work.md`

## Acceptance

- source group が 1 つだけの `existing-match` は `c.md:` header を出さない
- 各 existing-match item は行末 `| c.md` で source を読める
- 複数 source group の時だけ独立 file header を維持する
