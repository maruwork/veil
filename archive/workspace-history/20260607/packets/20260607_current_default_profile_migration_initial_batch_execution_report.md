# Current Default Profile Migration Initial Batch Execution Report

## 1. Batch Scope

- `c.md`
- `s.md`
- `d.md`
- `p.md`
- `r.md`

## 2. Batch Result

初回バッチ `5` file はすべて section-aware 形式へ移行済み。

- migrated files: `5`
- migrated rules: `34`

## 3. Post-Batch Audit

- command:
  - `python veil-profile-audit.py --rules-dir C:\Users\f_tan\.veil\rules`
- summary:
  - `files=19`
  - `total=66`
  - `required=43`
  - `recommended=9`
  - `observe=14`
  - `legacy_flat=32 in 14 file(s)`

## 4. File Results

- `c.md: required=4, recommended=1, observe=5, legacy_flat=0`
- `s.md: required=3, recommended=3, observe=3, legacy_flat=0`
- `d.md: required=2, recommended=2, observe=1, legacy_flat=0`
- `p.md: required=1, recommended=1, observe=3, legacy_flat=0`
- `r.md: required=1, recommended=2, observe=2, legacy_flat=0`

## 5. Delta

- legacy flat files: `19 -> 14`
- required-heavy profile から、rule 3 層が実データへ入り始めた

## 6. Next Wave

次は残り file のうち、件数と影響度から次を候補とする。

1. `a.md`
2. `l.md`
3. `t.md`
4. `b.md`
5. `h.md`

小規模 file を同じ手順で順次 migration し、legacy flat をさらに減らす。
