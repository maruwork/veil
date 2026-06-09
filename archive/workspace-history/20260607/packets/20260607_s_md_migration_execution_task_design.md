# s.md Migration Execution Task Design

## 1. Parent Theme

- current default profile migration execution

## 2. Task Designs

### Task ID: T-A

- 目的
  - `s.md` の current 実体を再確認する
- 読む場所
  - `C:\Users\f_tan\.veil\rules\s.md`
  - `workspace/20260607_s_md_migration_execution_requirements.md`
  - `workspace/20260607_s_md_migration_execution_basic_design.md`
- 書く場所
  - なし
- やること
  - current file content の readback
  - rule line 数と header 形の確認
- 合格条件
  - rule は `9` 件で、legacy flat format のみ
- 停止条件
  - planned shape からの逸脱
- 証拠
  - readback output

### Task ID: T-B

- 目的
  - `s.md` の再分類判断を file 単位で固定する
- 読む場所
  - `README.md`
  - `docs/veil-design.md`
  - `AGENTS.md`
  - `index/project-boundary-register.md`
- 書く場所
  - `workspace/20260607_s_md_migration_execution_report.md`
- やること
  - 各 rule の level と短い理由を report に残す
- 合格条件
  - `9` rule 全件の level と rationale が report に残る
- 停止条件
  - rationale が成立しない語がある
- 証拠
  - execution report draft

### Task ID: T-C

- 目的
  - real `s.md` を section-aware 形式へ移行する
- 読む場所
  - `C:\Users\f_tan\.veil\rules\s.md`
  - `workspace/20260607_s_md_migration_execution_basic_design.md`
- 書く場所
  - `C:\Users\f_tan\.veil\rules\s.md`
- やること
  - `# s` を保持
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
  - `C:\Users\f_tan\.veil\rules\s.md`
  - `veil-profile-audit.py`
- 書く場所
  - `workspace/20260607_s_md_migration_execution_report.md`
- やること
  - post-write readback
  - profile audit 実行
  - `s.md` legacy flat 解消を report に残す
- 合格条件
  - audit 上 `s.md` の legacy flat が `0`
- 停止条件
  - audit result が post-write shape と矛盾する
- 証拠
  - audit output
