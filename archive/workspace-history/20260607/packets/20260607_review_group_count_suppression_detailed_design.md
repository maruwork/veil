# review group count suppression detailed design

## Code Target

- `veil-normalize.py`

## Edit Detail

- current:
  - `print(f"{group_name} ({len(items)}件):")`
- target:
  - `print(f"{group_name}:")`

## Surface Follow-up

- `README.md`
  - review group header は group 名だけを見て、件数はその下の行数で把握することを追記する
- `docs/veil-design.md`
  - same contract
- `skills/codex/veil-capture/SKILL.md`
  - same contract
- `skills/claude-code/veil-capture.md`
  - same contract
- `index/project-current-work.md`
  - active bundle を新 bundle へ更新し、close 後に current position を書き戻す

## Verification

- `rtk python -B -m py_compile veil-normalize.py`
- text smoke で `短い review に残す:` / `短い review から外す寄り:` を確認する
- JSON smoke で JSON 契約 unchanged を確認する
- `rtk rg` で surface 契約がそろっていることを確認する
