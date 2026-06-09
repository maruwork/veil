# Execution Report

## Summary

- `veil-normalize.py` の `new-candidate` detail line を `variants/target:` から `variants:` へ短縮した
- README / design / skills を同じ `variants:` 契約へそろえた
- current companion を新 bundle の close 状態へ更新した

## Verification

- `rtk python -B -m py_compile veil-normalize.py`
- `rtk python veil-normalize.py --text "risk-reports\nrisk report\nsummary\nsummary\nverification\nclose"`
- `rtk python veil-normalize.py --text "risk-reports\nrisk report\nsummary\nsummary\nverification\nclose" --json`
- `rtk rg -n "variants/target:|variants: .*\\| .*|VEIL-TUNING-047|review: <selection hint>|review: ... \\| ...|single-variant" README.md docs/veil-design.md skills/codex/veil-capture/SKILL.md skills/claude-code/veil-capture.md veil-normalize.py index/project-current-work.md`

## Result

- multi-variant の `new-candidate` は `variants: risk report x1, risk-reports x1 | r.md` で出る
- `variants/target:` は current code / README / design / skills から消えた
- JSON 契約は維持した
