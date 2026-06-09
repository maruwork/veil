# existing-match single source suffix compaction execution report

## Summary

- bundle id:
  - `VEIL-TUNING-040`
- execution date:
  - `2026-06-07`
- result:
  - `complete`

## Scope

- single-source `existing-match` 行末を `| source: t.md` から `| t.md` へ短縮する
- `README.md`、`docs/veil-design.md`、capture skill 2 面、`index/project-current-work.md` を同契約へそろえる

## Changes

- `veil-normalize.py`
  - single-source existing-match suffix を `| t.md` のような file suffix に変更した
- `README.md`
  - 1 件 source は file suffix を見る契約へ更新した
- `docs/veil-design.md`
  - single-source suffix の label 非表示を反映した
- `skills/codex/veil-capture/SKILL.md`
  - 1 件 source は `| t.md` のような file suffix を読むことを反映した
- `skills/claude-code/veil-capture.md`
  - 1 件 source は `| t.md` のような file suffix を読むことを反映した

## Verification

- `rtk python -B -m py_compile veil-normalize.py`
  - pass
- text smoke
  - `- task -> タスク [必須] | t.md`
  - grouped source header `c.md:` unchanged
- JSON smoke
  - pass
  - JSON contract unchanged

## Outcome

- single-source existing-match suffix から `source:` label を除去した
- grouped source header `c.md:` は維持した
- docs / skills / current companion を同一契約へそろえた

## Next

- `capture 候補絞り込みの追加縮約`
- または `existing-match` 側の残る冗長行整理
