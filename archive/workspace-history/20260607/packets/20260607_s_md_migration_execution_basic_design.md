# s.md Migration Execution Basic Design

## 1. Migration Principle

- `skill` のような current mainline 高需要語は `必須` に残す
- `source of truth` と `sync surface` のような正本 / 同期の中核語も `必須` に残す
- 統一価値はあるが hard gate 中心語ではないものは `推奨`
- 一般語、低頻度語、意味境界が揺れやすいものは `観察`

## 2. Evidence Principle

- mainline current canonical を優先
- common usage は補助根拠
- exact hit が少なくても、VEIL の正本 / 同期骨格に深く関わる語は `必須` に残す

## 3. Reclassification Rationale

### 必須

- `skill`
  - current canonical で明確に高需要
- `source of truth`
  - common policy に現れ、正本概念の中核
- `sync surface`
  - VEIL の sync 骨格に直接関わる

### 推奨

- `scoped canonical register`
  - 概念は有用だが hard gate 中心語ではない
- `spec doc`
  - 統一価値はあるが一般性が高い
- `split rule`
  - 構造説明には使うが文脈依存が残る

### 観察

- `side conversation`
- `stage`
- `state plane`
  - low-demand または意味境界が広く、現段階で fail-close に残すには重い

## 4. Write Shape

```md
# s

## 必須

- skill → スキル
- source of truth → 正本ソース
- sync surface → 同期面

## 推奨

- scoped canonical register → 範囲限定の正本台帳
- spec doc → 仕様文書
- split rule → 分離ルール

## 観察

- side conversation → 別会話
- stage → ステージ
- state plane → 状態平面
```

## 5. Verification Principle

- migration 後に `s.md` readback を取る
- `veil-profile-audit.py` で `s.md` の legacy flat 解消を確認する
