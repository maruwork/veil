# Execution Report

## Summary

- `veil-normalize.py` の single-occurrence lowercase phrase 自動昇格を tighten した
- `request map` / `risk report` のような phrase は 1回だけでは `説明語候補` に上がらないようにした
- repeated phrase は従来どおり昇格余地を維持した

## Verification

- `rtk python -B -m py_compile veil-normalize.py`
- `rtk python veil-normalize.py --text "request map\nrisk report\nstate transition\nworkflow state\nrequest map\nrequest map"`
- `rtk python veil-normalize.py --text "request map\nrisk report\nstate transition\nworkflow state\nrequest map\nrequest map" --json`
- `rtk rg -n "single-occurrence の lowercase phrase|1回だけでは|小文字中心の一般語句だが、1回だけではまだ用途が広い|VEIL-TUNING-051|request map" README.md docs/veil-design.md skills/codex/veil-capture/SKILL.md skills/claude-code/veil-capture.md veil-normalize.py index/project-current-work.md`

## Result

- `risk report`、`state transition`、`workflow state` は `境界が曖昧な候補` に落ちた
- `request map` は 3回出現時だけ `説明語候補 / 先に採る候補 / 必須` に上がった
- JSON 契約は維持した
