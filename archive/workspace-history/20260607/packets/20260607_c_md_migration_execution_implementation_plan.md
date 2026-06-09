# c.md Migration Execution Implementation Plan

## 1. Tasks

1. `c.md` の current readback を取り、計画との差分有無を確認する
2. `c.md` の再分類案を execution record に固定する
3. real `c.md` を section-aware 形式へ更新する
4. migration 後 readback と profile audit で結果を確認する
5. execution result を workspace report に記録する

## 2. Files

### Read

- `workspace/20260607_current_default_profile_migration_initial_batch.md`
- `workspace/20260607_c_md_migration_execution_requirements.md`
- `workspace/20260607_c_md_migration_execution_basic_design.md`
- `C:\Users\f_tan\.veil\rules\c.md`
- `README.md`
- `docs/veil-design.md`
- `index/project-boundary-register.md`

### Write

- `C:\Users\f_tan\.veil\rules\c.md`
- `workspace/20260607_c_md_migration_execution_report.md`

## 3. Verification

- readback before write
- readback after write
- `python veil-profile-audit.py --rules-dir C:\Users\f_tan\.veil\rules`

## 4. Stop Rule

- current readback が計画内容と一致しない場合は write しない
- classification 追加判断が必要な語が見つかった場合は `c.md` だけでも止める
