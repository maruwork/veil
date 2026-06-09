# Required Rule Tuning Task Design

## 1. Task Designs

### Task ID: T-A

- 目的
  - required queue のうち demotion 対象を `推奨` へ落とす
- 読む場所
  - required rule tuning requirements/basic design
  - actual rules files
- 書く場所
  - `C:\Users\f_tan\.veil\rules\c.md`
  - `C:\Users\f_tan\.veil\rules\d.md`
  - `C:\Users\f_tan\.veil\rules\g.md`
  - `C:\Users\f_tan\.veil\rules\p.md`
  - `C:\Users\f_tan\.veil\rules\r.md`
  - `C:\Users\f_tan\.veil\rules\s.md`
- 合格条件
  - planned demotion が section 整合を壊さず反映される

### Task ID: T-B

- 目的
  - tuning 後の required queue を verify する
- 読む場所
  - tuned rules
  - `veil-profile-audit.py`
- 書く場所
  - `workspace/20260607_required_rule_tuning_execution_report.md`
- 合格条件
  - `--level 必須` queue が 4 rule
