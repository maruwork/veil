# Detailed Design

## Authoritative Completion Path

1. foundation の有効成果を current に固定する
2. `workspace/20260607_candidate_rule_decision_sheet.md` を owner decision checkpoint として固定する
3. decision 完了後にだけ runtime / skill / docs の rule alignment bundle を切る
4. representative flow verification bundle を切る
5. completion audit を行う

## Completion Blockers

- candidate rule の未確定
- `capture` と `normalize` の厳格化責務の未確定
- end-to-end verification evidence の未作成

## Deliverables

- completion packet 6 本
- current work completion bundle
- README completion path paragraph
- design completion phase paragraph

## Verification Route

- `rtk rg` で completion / blocker / phase / decision checkpoint を readback
- `current work` で read order が成立していること
- `README.md` と `docs/veil-design.md` で same completion path が読めること
