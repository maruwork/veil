# Execution Report

## Summary

- `veil-normalize.py` の `existing-match` variant label を `| variants: ...` へ短縮した
- `README.md` に残っていた旧 detail label 文言を `review:` 契約へ修正した
- design / skills / current companion を current 契約へそろえた

## Verification

- `rtk python -B -m py_compile veil-normalize.py`
- `rtk python veil-normalize.py --text "current states\ncommon-assets\nsummary\nsummary\nverification\nclose\nworkflow"`
- `rtk python veil-normalize.py --text "current states\ncommon-assets\nsummary\nsummary\nverification\nclose\nworkflow" --json`
- `rtk python veil-normalize.py --text "common-assets\ncommon asset"`
- `rtk python veil-normalize.py --text "common-assets\ncommon asset" --json`
- `rtk rg -n "選別/保留/判別|選別/判別|表記ゆれ:|\\| variants:|active bundle id:|VEIL-TUNING-046" README.md docs/veil-design.md skills/codex/veil-capture/SKILL.md skills/claude-code/veil-capture.md veil-normalize.py index/project-current-work.md`

## Result

- `existing-match` の variant 表示は `| variants: ...` で出る
- README の旧 detail label 文言は消えた
- code / README / design / skills / current companion は current 契約で一致した
