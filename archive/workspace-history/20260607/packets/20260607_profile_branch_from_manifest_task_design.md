# Profile Branch From Manifest Task Design

## 1. Task Designs

### Task ID: T-A

- 目的
  - export pack manifest から派生 export を起こせるようにする
- 読む場所
  - `veil-profile-export.py`
  - manifest branch basic design
- 書く場所
  - `veil-profile-export.py`
- 合格条件
  - `--base-manifest` 指定時に branch pack を作れる

### Task ID: T-B

- 目的
  - canonical docs に branch recipe を反映する
- 読む場所
  - `README.md`
  - `docs/veil-design.md`
- 書く場所
  - same files
- 合格条件
  - branch recipe が current canonical で読める

### Task ID: T-C

- 目的
  - branch smoke と report を残す
- 読む場所
  - branch manifest
- 書く場所
  - execution report
- 合格条件
  - `medical-guardrail` sample manifest が作れる
