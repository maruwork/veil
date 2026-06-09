# existing-match single source suffix compaction detailed design

## Code Target

- `veil-normalize.py`

## Edit Detail

- current:
  - `line += f" | source: {source_file}"`
- target:
  - `line += f" | {source_file}"`

## Surface Follow-up

- `README.md`
  - 1 件 source は行末 `| t.md` のような file suffix を見ると記す
- `docs/veil-design.md`
  - same contract
- capture skill 2 面
  - same contract
- `index/project-current-work.md`
  - active bundle と close writeback を更新する

## Verification

- `rtk python -B -m py_compile veil-normalize.py`
- text smoke で `| t.md` を確認する
- JSON smoke で JSON unchanged を確認する
- `rtk rg` で surface 契約を確認する
