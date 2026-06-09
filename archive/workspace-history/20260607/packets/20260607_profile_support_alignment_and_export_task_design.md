# Profile Support Alignment And Export Task Design

## 1. Parent Theme

- profile support alignment and domain profile export

## 2. Task Designs

### Task ID: T-A

- 目的
  - `veil-profile-audit.py` と `veil-profile-export.py` の shelf を governance 上で固定する
- 読む場所
  - `AGENTS.md`
  - `index/project-file-taxonomy.md`
  - `index/project-boundary-register.md`
  - `index/project-template-adoption-packet.md`
- 書く場所
  - same files
- 合格条件
  - mainline と support runtime が混線せず、root 許可一覧にも反映される

### Task ID: T-B

- 目的
  - `veil-profile-export.py` を実装する
- 読む場所
  - `veil-profile-audit.py`
  - basic design
- 書く場所
  - `veil-profile-export.py`
- 合格条件
  - source rules を mutate せず output dir に profile pack を作れる

### Task ID: T-C

- 目的
  - canonical docs に export 導線を反映する
- 読む場所
  - `README.md`
  - `docs/veil-design.md`
  - `AGENTS.md`
- 書く場所
  - same files
- 合格条件
  - default profile export の位置づけが current canonical で読める

### Task ID: T-D

- 目的
  - verify と execution record を残す
- 読む場所
  - `veil-profile-export.py`
- 書く場所
  - execution report
- 合格条件
  - py_compile と export smoke が通る
