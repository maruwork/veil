# c.md Migration Execution Task Design

## 1. Parent Theme

- current default profile migration execution

## 2. Task Designs

### Task ID: T-A

- 目的
  - `c.md` の current 実体を再確認し、planned write が still valid か判定する
- 読む場所
  - `C:\Users\f_tan\.veil\rules\c.md`
  - `workspace/20260607_c_md_migration_execution_requirements.md`
  - `workspace/20260607_c_md_migration_execution_basic_design.md`
- 書く場所
  - なし
- やること
  - current file content の readback
  - rule line 数と header 形の確認
  - unexpected manual edits の有無確認
- 合格条件
  - rule は `10` 件で、legacy flat format のみ
- 停止条件
  - rule 数増減、comment 混在、section 済みなど planned shape からの逸脱
- 証拠
  - readback output

### Task ID: T-B

- 目的
  - `c.md` の再分類判断を file 単位で固定する
- 読む場所
  - `README.md`
  - `docs/veil-design.md`
  - `index/project-boundary-register.md`
  - `workspace/20260607_c_md_migration_execution_basic_design.md`
- 書く場所
  - `workspace/20260607_c_md_migration_execution_report.md`
- やること
  - 各 rule の level と短い理由を report に残す
- 合格条件
  - `10` rule 全件の level と rationale が report に残る
- 停止条件
  - file 単位で rationale が成立しない語がある
- 証拠
  - execution report draft

### Task ID: T-C

- 目的
  - real `c.md` を section-aware 形式へ移行する
- 読む場所
  - `C:\Users\f_tan\.veil\rules\c.md`
  - `workspace/20260607_c_md_migration_execution_basic_design.md`
- 書く場所
  - `C:\Users\f_tan\.veil\rules\c.md`
- やること
  - `# c` を保持
  - `## 必須 / ## 推奨 / ## 観察` を追加
  - rule を planned section へ再配置
- 合格条件
  - legacy flat line が消え、planned section shape になる
- 停止条件
  - write permission が得られない
  - current file が想定と異なる
- 証拠
  - post-write readback

### Task ID: T-D

- 目的
  - migration 成果を verify し、記録を残す
- 読む場所
  - `C:\Users\f_tan\.veil\rules\c.md`
  - `veil-profile-audit.py`
- 書く場所
  - `workspace/20260607_c_md_migration_execution_report.md`
- やること
  - post-write readback
  - profile audit 実行
  - `c.md` legacy flat 解消を report に残す
- 合格条件
  - audit 上 `c.md` の legacy flat が `0`
- 停止条件
  - audit result が post-write shape と矛盾する
- 証拠
  - audit output
