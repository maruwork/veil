# low-priority level suppression detailed design

## Code Target

- `veil-normalize.py`

## Edit Detail

- current:
  - `- [new-candidate] close | c.md | 観察 | 今は見送る`
- target:
  - `- [new-candidate] close | c.md | 今は見送る`

## Surface Follow-up

- `README.md`
  - low-priority line は `normalized | target | 保留処理` と記す
- `docs/veil-design.md`
  - same contract
- capture skill 2 面
  - same contract
- `index/project-current-work.md`
  - active bundle と close writeback を更新する

## Verification

- `rtk python -B -m py_compile veil-normalize.py`
- text smoke で `| 今は見送る` だけになることを確認する
- JSON smoke で `suggested_level` unchanged を確認する
- `rtk rg` で surface 契約を確認する
