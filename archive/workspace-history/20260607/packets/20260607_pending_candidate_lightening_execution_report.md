# Execution Report

## Theme

VEIL tuning wave 6: 保留候補運用の軽量化

## Result

- `veil-normalize.py` に `retention_hint` と `retention_reason` を追加した
- `selection_hint == 保留寄り` の item にだけ保留処理目安を返すようにした
- 保留処理名は `今は見送る / 後で再観察する / 文脈不足で保留` の 3 つに固定した
- `README.md`、`docs/veil-design.md`、2 つの capture skill、`index/project-current-work.md` を同契約へ更新した

## Evidence

- command:
  - `rtk python -m py_compile veil-normalize.py`
- command:
  - `rtk python veil-normalize.py --text "close\nverification\nclose-ish\nsummary\nsummary\nstatus=close" --json`
- command:
  - `rtk python veil-normalize.py --text "close\nverification\nclose-ish\nsummary\nsummary\nstatus=close"`
- command:
  - `rtk rg "保留処理|今は見送る|後で再観察する|文脈不足で保留|保留寄り" README.md docs/veil-design.md skills/codex/veil-capture/SKILL.md skills/claude-code/veil-capture.md index/project-current-work.md`

## Verification Summary

- JSON 出力:
  - `close` -> `保留寄り` + `今は見送る`
  - `verification` -> `保留寄り` + `後で再観察する`
  - `close-ish` -> `保留寄り` + `文脈不足で保留`
  - `summary` -> `先に採る候補` なので retention は付かない
  - `status=close` -> `外す寄り` なので retention は付かない
- text 出力:
  - `保留処理` と `保留理由` が `保留寄り` item にだけ出る
- surface alignment:
  - README / design / 2 skills / current companion が同じ 3 つの保留処理名を使う

## Scope Check

- changed:
  - `veil-normalize.py`
  - `README.md`
  - `docs/veil-design.md`
  - `skills/codex/veil-capture/SKILL.md`
  - `skills/claude-code/veil-capture.md`
  - `index/project-current-work.md`
- unchanged:
  - `veil-lint.py`
  - `veil-sync.py`
  - schema / DB
  - UI

## Completion Decision

- wave 6 completion condition:
  - PASS
