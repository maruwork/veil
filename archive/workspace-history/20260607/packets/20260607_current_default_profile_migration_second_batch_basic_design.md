# Current Default Profile Migration Second Batch Basic Design

## 1. Migration Principle

- second batch は exact hit が弱い語が多いため、`必須` は最小限にする
- high-demand が明確な `task` だけを `必須`
- それ以外は統一価値の有無で `推奨 / 観察` を切る

## 2. Rationale

- `audit`, `allowlist`, `live proof`, `bounded work`, `hardening`, `healthcheck` は用語統一価値はある
- ただし current mainline で fail-close 主語とまでは言いにくいので `推奨` に留める
- `analysis`, `latest result`, `local reference`, `tracked row`, `hidden premise` などは一般性または文脈依存が強いため `観察`

## 3. File Shapes

### a.md

```md
# a

## 推奨

- allowlist → 許可リスト
- audit → 監査

## 観察

- active disposition → 現役配置
- analysis → 分析
```

### l.md

```md
# l

## 推奨

- live proof → 実行証拠

## 観察

- latest close detail → 最新の完了詳細
- latest result → 最新の結果
- local reference → ローカルの参照
```

### t.md

```md
# t

## 必須

- task → タスク

## 観察

- tool portability → ツールポータビリティ
- tracked row → 追跡行
```

### b.md

```md
# b

## 推奨

- bounded work → 制限付き作業

## 観察

- bounded fix → 制限付きフィックス
- bounded goal → 制限付きゴール
```

### h.md

```md
# h

## 推奨

- hardening → 堅牢化
- healthcheck → 正常確認

## 観察

- hidden premise → 裏
```
