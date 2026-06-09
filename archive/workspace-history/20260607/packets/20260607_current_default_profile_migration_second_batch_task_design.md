# Current Default Profile Migration Second Batch Task Design

## 1. Parent Theme

- current default profile migration second batch

## 2. Task Designs

### Task ID: T-A

- 目的
  - second batch 5 file を planned shape へ移行する
- 読む場所
  - second batch requirements/basic design
  - each real rules file
- 書く場所
  - `a.md / l.md / t.md / b.md / h.md`
- 合格条件
  - 5 file すべてで legacy flat line が消える

### Task ID: T-B

- 目的
  - batch 成果を verify して記録する
- 読む場所
  - migrated files
  - `veil-profile-audit.py`
- 書く場所
  - `workspace/20260607_current_default_profile_migration_second_batch_execution_report.md`
- 合格条件
  - audit 上、5 file の legacy flat が `0`
