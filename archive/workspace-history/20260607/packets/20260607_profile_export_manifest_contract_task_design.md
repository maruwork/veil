# Profile Export Manifest Contract Task Design

## 1. Task Designs

### Task ID: T-A

- 目的
  - export manifest に branch metadata を追加する
- 読む場所
  - `veil-profile-export.py`
  - manifest contract basic design
- 書く場所
  - `veil-profile-export.py`
- 合格条件
  - metadata options が manifest に出る

### Task ID: T-B

- 目的
  - docs と smoke を追従させる
- 読む場所
  - `README.md`
  - `docs/veil-design.md`
- 書く場所
  - same files
- 合格条件
  - export example と manifest readback が current behavior に一致する
