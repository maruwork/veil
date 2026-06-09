# Current Default Profile Migration Second Batch Execution Report

## 1. Batch Scope

- `a.md`
- `l.md`
- `t.md`
- `b.md`
- `h.md`

## 2. Batch Result

second batch `5` file はすべて section-aware 形式へ移行済み。

- migrated files: `5`
- migrated rules: `17`

## 3. Post-Batch Audit

- command:
  - `python veil-profile-audit.py --rules-dir C:\Users\f_tan\.veil\rules`
- summary:
  - `files=19`
  - `total=66`
  - `required=27`
  - `recommended=15`
  - `observe=24`
  - `legacy_flat=15 in 9 file(s)`

## 4. File Results

- `a.md: required=0, recommended=2, observe=2, legacy_flat=0`
- `l.md: required=0, recommended=1, observe=3, legacy_flat=0`
- `t.md: required=1, recommended=0, observe=2, legacy_flat=0`
- `b.md: required=0, recommended=1, observe=2, legacy_flat=0`
- `h.md: required=0, recommended=2, observe=1, legacy_flat=0`

## 5. Delta

- legacy flat files: `14 -> 9`
- required-heavy profile から、warning / observe を含む profile へさらに移行した

## 6. Remaining Legacy Flat Files

- `e.md`
- `f.md`
- `g.md`
- `m.md`
- `n.md`
- `o.md`
- `u.md`
- `v.md`
- `w.md`

## 7. Suggested Next Wave

残りはすべて小規模 file なので、次 wave では

1. `e/f/g`
2. `m/n/o`
3. `u/v/w`

のように意味近接ごとに 3 束へ分けて migration するのが自然である。
