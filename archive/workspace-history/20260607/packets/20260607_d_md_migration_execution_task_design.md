# d.md Migration Execution Task Design

## 1. Parent Theme

- current default profile migration execution

## 2. Task Designs

### Task ID: T-A

- 目的
  - `d.md` の current 実体を再確認する
- 読む場所
  - `C:\Users\f_tan\.veil\rules\d.md`
  - `workspace/20260607_d_md_migration_execution_requirements.md`
  - `workspace/20260607_d_md_migration_execution_basic_design.md`
- 合格条件
  - rule は `5` 件で、legacy flat format のみ

### Task ID: T-B

- 目的
  - `d.md` の再分類判断を file 単位で固定する
- 読む場所
  - `README.md`
  - `docs/veil-design.md`
  - `common/frameworks/project-progression-rule.md`
- 書く場所
  - `workspace/20260607_d_md_migration_execution_report.md`
- 合格条件
  - `5` rule 全件の level と rationale が report に残る

### Task ID: T-C

- 目的
  - real `d.md` を section-aware 形式へ移行する
- 読む場所
  - `C:\Users\f_tan\.veil\rules\d.md`
  - `workspace/20260607_d_md_migration_execution_basic_design.md`
- 書く場所
  - `C:\Users\f_tan\.veil\rules\d.md`
- 合格条件
  - legacy flat line が消え、planned section shape になる

### Task ID: T-D

- 目的
  - migration 成果を verify し、記録を残す
- 読む場所
  - `C:\Users\f_tan\.veil\rules\d.md`
  - `veil-profile-audit.py`
- 書く場所
  - `workspace/20260607_d_md_migration_execution_report.md`
- 合格条件
  - audit 上 `d.md` の legacy flat が `0`
