# source label path compaction detailed design

## Code Target

- `veil-normalize.py`

## Edit Detail

- current:
  - `参照ルール: C:\\Users\\f_tan/.veil\\rules`
- target example:
  - `参照ルール: rules`
- current db example:
  - full db path
- target db example:
  - db file basename

## Surface Follow-up

- `README.md`
  - text 出力先頭は source 名だけを見ると記す
- `docs/veil-design.md`
  - same contract
- capture skill 2 面
  - same contract
- `index/project-current-work.md`
  - active bundle と close writeback を更新する

## Verification

- `rtk python -B -m py_compile veil-normalize.py`
- text smoke で `参照ルール: rules` を確認する
- JSON smoke で `source` unchanged を確認する
- `rtk rg` で surface 契約を確認する
