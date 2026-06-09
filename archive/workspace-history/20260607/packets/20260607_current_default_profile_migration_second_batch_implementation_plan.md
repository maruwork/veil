# Current Default Profile Migration Second Batch Implementation Plan

## 1. Tasks

1. 5 file の current readback を確認する
2. second batch decision に従って section-aware 形式へ更新する
3. post-write readback を取る
4. profile audit で batch 結果を確認する
5. batch execution report を残す

## 2. Files

### Read

- `workspace/20260607_current_default_profile_migration_second_batch_requirements.md`
- `workspace/20260607_current_default_profile_migration_second_batch_basic_design.md`
- `C:\Users\f_tan\.veil\rules\a.md`
- `C:\Users\f_tan\.veil\rules\l.md`
- `C:\Users\f_tan\.veil\rules\t.md`
- `C:\Users\f_tan\.veil\rules\b.md`
- `C:\Users\f_tan\.veil\rules\h.md`

### Write

- each real rules file above
- `workspace/20260607_current_default_profile_migration_second_batch_execution_report.md`

## 3. Verification

- per-file readback
- `python veil-profile-audit.py --rules-dir C:\Users\f_tan\.veil\rules`
