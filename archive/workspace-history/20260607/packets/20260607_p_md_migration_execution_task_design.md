# p.md Migration Execution Task Design

## 1. Task Designs

### Task ID: T-A

- 目的
  - `p.md` を section-aware 形式へ移行する
- 読む場所
  - `C:\Users\f_tan\.veil\rules\p.md`
  - `workspace/20260607_p_md_migration_execution_basic_design.md`
- 書く場所
  - `C:\Users\f_tan\.veil\rules\p.md`
- 合格条件
  - planned section shape になる

### Task ID: T-B

- 目的
  - migration 成果を verify する
- 読む場所
  - `C:\Users\f_tan\.veil\rules\p.md`
  - `veil-profile-audit.py`
- 書く場所
  - `workspace/20260607_p_md_migration_execution_report.md`
- 合格条件
  - audit 上 `p.md` の legacy flat が `0`
