# Profile Tuning Review Route Task Design

## 1. Task Designs

### Task ID: T-A

- 目的
  - `veil-profile-audit.py` に level-aware review route を追加する
- 読む場所
  - `veil-profile-audit.py`
  - tuning review route basic design
- 書く場所
  - `veil-profile-audit.py`
- 合格条件
  - `--level` 指定時に rule list が返る

### Task ID: T-B

- 目的
  - docs と current companion を tuning route に追従させる
- 読む場所
  - `README.md`
  - `docs/veil-design.md`
  - `index/project-current-work.md`
- 書く場所
  - same files
- 合格条件
  - tuning review の使い方が current canonical で読める

### Task ID: T-C

- 目的
  - verify と記録を残す
- 読む場所
  - `veil-profile-audit.py`
- 書く場所
  - execution report
- 合格条件
  - py_compile と smoke が通る
