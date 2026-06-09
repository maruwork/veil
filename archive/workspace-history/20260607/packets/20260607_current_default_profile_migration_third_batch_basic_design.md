# Current Default Profile Migration Third Batch Basic Design

## 1. Rationale

- `goal` は common 骨格で高需要な中核語なので `必須`
- `external authority` と `file taxonomy` は governance 上の統一価値が高いので `推奨`
- `falsy` と `graceful fallback` は一般技術語寄りで、現段階では `観察`

## 2. File Shapes

### e.md

```md
# e

## 推奨

- external authority → 外部正本
```

### f.md

```md
# f

## 推奨

- file taxonomy → ファイル分類表

## 観察

- falsy → 偽値
```

### g.md

```md
# g

## 必須

- goal → ゴール

## 観察

- graceful fallback → 適切な代替処理
```
