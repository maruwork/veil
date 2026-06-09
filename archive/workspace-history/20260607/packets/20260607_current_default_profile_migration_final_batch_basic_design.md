# Current Default Profile Migration Final Batch Basic Design

## 1. Rationale

- `normalization` は `veil-normalize.py` の core authority に直接関わるため `必須`
- `mutation`, `verification family`, `writeback` は common / governance 骨格への接続があるため `推奨`
- 残りは文脈依存または一般語寄りなので `観察`

## 2. File Shapes

### m.md

```md
# m

## 推奨

- mutation → 変更

## 観察

- MDファイル → Markdownファイル
```

### n.md

```md
# n

## 必須

- normalization → 正規化

## 観察

- naturalness → 自然さ
```

### o.md

```md
# o

## 観察

- old reference → 古い参照
```

### u.md

```md
# u

## 観察

- uncommitted → 未コミット
- untracked → 未追跡
```

### v.md

```md
# v

## 推奨

- verification family → 検証系

## 観察

- validator → バリデータ
```

### w.md

```md
# w

## 推奨

- writeback → 書き戻し
```
