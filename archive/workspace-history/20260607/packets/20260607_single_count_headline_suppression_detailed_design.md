# single-count headline suppression detailed design

## Code Target

- `veil-normalize.py`

## Edit Detail

- current:
  - `verification [観察] x1 | v.md`
- target:
  - `verification [観察] | v.md`
- keep:
  - `summary [推奨] x2`

## Surface Follow-up

- `README.md`
  - count は 2 回以上の時だけ headline で読むと記す
- `docs/veil-design.md`
  - same contract
- capture skill 2 面
  - same contract
- `index/project-current-work.md`
  - active bundle と close writeback を更新する

## Verification

- `rtk python -B -m py_compile veil-normalize.py`
- text smoke で `x1` 省略と `x2` 維持を確認する
- JSON smoke で `occurrence_count` unchanged を確認する
- `rtk rg` で surface 契約を確認する
