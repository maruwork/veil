# d.md Migration Execution Basic Design

## 1. Migration Principle

- `design` 骨格語だけは `必須` に残す
- その周辺語は hard gate で縛りすぎず `推奨` または `観察` へ落とす

## 2. Evidence Principle

- current canonical と common 骨格の両方で現れる `design` を最優先根拠とする
- exact hit の弱い語は 1 段保守的に落とす

## 3. Reclassification Rationale

### 必須

- `design`
  - current canonical と common 骨格で継続使用される中心語
- `design boundary`
  - 設計境界の概念は task-design 粒度の運用で重要

### 推奨

- `decision memo`
  - 統一価値はあるが hard gate 中心語ではない
- `dedup`
  - 技術作業語として有用だが fail-close までは不要

### 観察

- `document quality`
  - 文脈依存が強く、自然言い換え幅が残る

## 4. Write Shape

```md
# d

## 必須

- design → 設計
- design boundary → 設計境界

## 推奨

- decision memo → 判断メモ
- dedup → 重複排除

## 観察

- document quality → 文書品質
```
