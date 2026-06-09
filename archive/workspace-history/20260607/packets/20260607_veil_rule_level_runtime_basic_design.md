# VEIL Rule Level Runtime Basic Design

## 1. Architecture

### Current

- rule line は一律 `- original → preferred`
- `veil-lint.py` は hit を全部 violation 扱いする
- `veil-normalize.py` は rule level を持たない

### Target

- rule file は section heading を持てる
- parser は current section を保持する
- `veil-lint.py` は `必須 / 推奨 / 観察` で動作を分ける
- `veil-normalize.py` は existing match に level を付ける

## 2. Rule Format Design

### Physical Format

```md
# c

## 必須
- current state → 今の状態

## 推奨
- current issue → 現在の課題

## 観察
- close path → 完了経路
```

### Compatibility

- section heading が出るまでの rule line は `必須` 扱い
- line format は current parser と同じ `- original → preferred`

### Rejected Option

- line suffix で `| 必須` を足す
  - parser は書けるが、既存行の見た目が崩れやすい
  - section でまとめて読める利点がない

## 3. Lint Runtime Design

### Result Buckets

- `violations`
  - `必須` rule hit
- `warnings`
  - `推奨` rule hit
- `ignored`
  - `観察` rule は lint failure に使わない

### Exit Code Policy

- `0`
  - clean
  - warning only
  - skip
- `1`
  - required violation あり
- `2`
  - usage / read error

### Text Output

- `CLEAN`
- `WARN`
- `NG`
- `SKIP`

## 4. Normalize Runtime Design

- existing rule match に `level` を持たせる
- new candidate に existing level がない場合、current wave では auto-level 提案まではしない

## 5. Interface Notes

### JSON

- `veil-lint.py`
  - `status`
  - `violations`
  - `warnings`
  - `conflicts`
- `veil-normalize.py`
  - existing match に `level`

### Conflict Handling

- same normalized key で level まで違う場合は conflict として warn する

## 6. Documentation Follow-through

- `README.md`
  - rule file 例
  - warning / violation の読み方
- `docs/veil-design.md`
  - rule physical format
  - lint semantics

## 7. Deferred Questions

- `観察` rule を将来 `normalize` だけに隔離するか
- capture report に level 提案を出すか
