# Current Default Profile Migration Final Batch Execution Report

## 1. Batch Scope

- `m.md`
- `n.md`
- `o.md`
- `u.md`
- `v.md`
- `w.md`

## 2. Batch Result

final batch `6` file はすべて section-aware 形式へ移行済み。

- migrated files: `6`
- migrated rules: `10`

## 3. Post-Batch Audit

- command:
  - `python veil-profile-audit.py --rules-dir C:\Users\f_tan\.veil\rules`
- summary:
  - `files=19`
  - `total=66`
  - `required=14`
  - `recommended=20`
  - `observe=32`
  - `legacy_flat=0 in 0 file(s)`

## 4. File Results

- `m.md: required=0, recommended=1, observe=1, legacy_flat=0`
- `n.md: required=1, recommended=0, observe=1, legacy_flat=0`
- `o.md: required=0, recommended=0, observe=1, legacy_flat=0`
- `u.md: required=0, recommended=0, observe=2, legacy_flat=0`
- `v.md: required=0, recommended=1, observe=1, legacy_flat=0`
- `w.md: required=0, recommended=1, observe=0, legacy_flat=0`

## 5. Result

- current default profile の全 file が section-aware 形式へ移行済み
- legacy flat rule は全消去
