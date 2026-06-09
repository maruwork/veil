# Current Default Profile Migration Third Batch Task Design

## 1. Task Designs

### Task ID: T-A

- 目的
  - `e/f/g` を section-aware 形式へ移行する
- 読む場所
  - third batch requirements/basic design
  - each real rules file
- 書く場所
  - `e.md / f.md / g.md`
- 合格条件
  - 3 file すべてで legacy flat line が消える

### Task ID: T-B

- 目的
  - batch 成果を verify して記録する
- 読む場所
  - migrated files
  - `veil-profile-audit.py`
- 書く場所
  - `workspace/20260607_current_default_profile_migration_third_batch_execution_report.md`
- 合格条件
  - audit 上、3 file の legacy flat が `0`
