# Current Default Profile Migration Final Batch Task Design

## 1. Task Designs

### Task ID: T-A

- 目的
  - `m/n/o/u/v/w` を section-aware 形式へ移行する
- 読む場所
  - final batch requirements/basic design
  - each real rules file
- 書く場所
  - `m.md / n.md / o.md / u.md / v.md / w.md`
- 合格条件
  - 6 file すべてで legacy flat line が消える

### Task ID: T-B

- 目的
  - batch 成果を verify して記録する
- 読む場所
  - migrated files
  - `veil-profile-audit.py`
- 書く場所
  - `workspace/20260607_current_default_profile_migration_final_batch_execution_report.md`
- 合格条件
  - audit 上 `legacy_flat=0 in 0 file(s)`
