# Current Default Profile Audit Report

## 1. Execution

- date: 2026-06-07
- command:
  - `python veil-profile-audit.py`
  - `python veil-profile-audit.py --json`
- target:
  - `C:\Users\f_tan\.veil\rules`
- mode:
  - read-only

## 2. Summary

- files: `19`
- total rules: `66`
- required: `66`
- recommended: `0`
- observe: `0`
- legacy flat rules: `66`
- legacy flat files: `19`

要点:

- current default profile は、まだ `## 必須 / ## 推奨 / ## 観察` へ 1 件も移行していない
- 全 rule が heading のない legacy flat rule である
- runtime 上は backward compatibility により全部 `必須` 扱いになる

## 3. File Distribution

- `c.md`: `10`
- `s.md`: `9`
- `d.md`: `5`
- `p.md`: `5`
- `r.md`: `5`
- `a.md`: `4`
- `l.md`: `4`
- `b.md`: `3`
- `h.md`: `3`
- `t.md`: `3`
- `f.md`: `2`
- `g.md`: `2`
- `m.md`: `2`
- `n.md`: `2`
- `u.md`: `2`
- `v.md`: `2`
- `e.md`: `1`
- `o.md`: `1`
- `w.md`: `1`

## 4. Findings

1. current default profile は全面 legacy flat で、section-aware profile へ未移行
2. `推奨` と `観察` は実データ上では 0 件
3. current runtime の fail-close は、現状では 66 rule 全件に対して `必須` として効く
4. current default profile の整理なしに `推奨` / `観察` の運用効果は十分に出ない

## 5. Implications

- VEIL の mainline runtime は整った
- ただし current default profile は旧 format のままで、運用上は「全部 required」の状態に近い
- 次にやるべきなのは runtime 追加ではなく、rules の migration planning である

## 6. Recommended Next Wave

### Wave Name

- current default profile migration planning

### Scope

- `~/.veil/rules/` を直接自動編集しない
- file ごとに
  - `legacy flat -> 必須 section`
  - `推奨` へ落とす候補
  - `観察` へ落とす候補
  - そのまま `必須` に残す候補
  を棚卸しする

### Suggested Order

1. rule 数の多い file から始める
   - `c.md`
   - `s.md`
   - `d.md`
   - `p.md`
   - `r.md`
2. 旧 flat rule を `## 必須` の下へ移す migration 手順を定義する
3. その上で `推奨` / `観察` 候補を手動で再配置する

## 7. Evidence Notes

- text output summary:
  - `PROFILE: files=19, total=66, required=66, recommended=0, observe=0, legacy_flat=66 in 19 file(s)`
- sample legacy-heavy files:
  - `c.md`
  - `s.md`
  - `d.md`
  - `p.md`
  - `r.md`
