# Execution Report

## Summary

- `veil-normalize.py` の `existing-match` grouped branch で、source file が 1 種類だけの時は独立 file header を suppress した
- 単一 source group は各 item 行末 `| c.md` のような source suffix だけで読めるようにした
- README / design / skills / current companion を同契約へ更新した

## Verification

- `rtk python -B -m py_compile veil-normalize.py`
- `rtk python veil-normalize.py --text "current states\ncommon-assets\ncommon asset"`
- `rtk python veil-normalize.py --text "current states\ncommon-assets\ncommon asset\nrequest-maps\nrequest map"`
- `rtk python veil-normalize.py --text "current states\ntasks\ncommon-assets\ncommon asset"`
- `rtk python veil-normalize.py --text "current states\ntasks\ncommon-assets\ncommon asset" --json`
- `rtk rg -n "c\\.md:|source file が 1 種類だけ|source file が複数種類|VEIL-TUNING-048|existing-match.*file header" README.md docs/veil-design.md skills/codex/veil-capture/SKILL.md skills/claude-code/veil-capture.md veil-normalize.py index/project-current-work.md`

## Result

- single-group existing-match では `c.md:` header が消え、各 item 行末の `| c.md` で source を読む
- 複数 source がある時は grouped header を維持しつつ、単発 source item は suffix のまま読める
- JSON 契約は維持した
