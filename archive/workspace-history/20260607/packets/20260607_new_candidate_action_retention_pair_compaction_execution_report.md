# Execution Report

## Bundle

- id
  - `VEIL-TUNING-023`
- theme
  - `new-candidate action/retention pair compaction`

## What Changed

- `veil-normalize.py` の non-low-priority `new-candidate` detail branch で retention がある時だけ `選別/review` と `保留` を 1 行へ統合
- retention がない時は `選別/review` 単独形を維持
- `判別` は独立行のまま維持
- `README.md`、`docs/veil-design.md`、2 つの capture skill を新ラベルへ追従
- `index/project-current-work.md` を wave 27 close 状態へ更新

## Verification

- `rtk python -m py_compile veil-normalize.py`
- text smoke で `verification` が `選別/review/保留: 保留寄り | 急いで採らず、文脈と困り度を見てから判断する | 短い review に残す | 後で再観察する` になることを確認
- text smoke で `判別` 独立行が維持されることを確認
- text smoke で low-priority `close` branch unchanged を確認
- `rtk python veil-normalize.py --text "summary\nsummary\nverification\nclose" --json`
- `rtk rg -n "選別/review/保留:" README.md docs/veil-design.md skills/codex/veil-capture/SKILL.md skills/claude-code/veil-capture.md`

## Result

- retention がある non-low-priority `new-candidate` の読み行数を 1 行削減
- retention がない候補の行数は増やさず維持
- `判別` の独立性を維持
- low-priority branch unchanged
- existing-match unchanged
- JSON unchanged
