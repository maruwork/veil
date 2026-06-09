# detail label compaction detailed design

## Code Target

- `veil-normalize.py`

## Edit Detail

- current:
  - `選別/保留/判別: A | B | C`
  - `選別/判別: A | C`
- target:
  - `review: A | B | C`
  - `review: A | C`

## Surface Follow-up

- `README.md`
  - detail line は `review:` の後ろの値を読むと記す
- `docs/veil-design.md`
  - same contract
- capture skill 2 面
  - same contract
- `index/project-current-work.md`
  - active bundle と close writeback を更新する

## Verification

- `rtk python -B -m py_compile veil-normalize.py`
- text smoke で `review:` を確認する
- JSON smoke で values unchanged を確認する
- `rtk rg` で surface 契約を確認する
