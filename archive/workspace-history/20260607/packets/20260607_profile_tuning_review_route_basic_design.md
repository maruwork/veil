# Profile Tuning Review Route Basic Design

## 1. Design Principle

- 既存 `veil-profile-audit.py` を拡張し、root file を増やさない
- default behavior は維持する
- tuning で見たい時だけ level filter を明示する

## 2. CLI Design

- new option:
  - `--level 必須|推奨|観察`
- no `--level`
  - current summary behavior のまま
- with `--level`
  - matching rules list を payload に追加
  - text output では summary の後に rule 一覧を出す

## 3. Payload Design

- `rules`
  - `file`
  - `level`
  - `original`
  - `preferred`

## 4. Verification Design

- `python -m py_compile veil-profile-audit.py`
- `python veil-profile-audit.py --level 必須`
- `python veil-profile-audit.py --level 観察 --json`
