# c.md Migration Execution Basic Design

## 1. Migration Principle

- file 全体を一括で軽くしない
- まず section を明示し、rule を意味の強さで再配置する
- `必須` は fail-close に残すべき語だけへ絞る
- `推奨` は統一価値はあるが違反即修正までは不要な語へ使う
- `観察` は低頻度・文脈依存・未成熟語へ使う

## 2. Evidence Principle

- repo 内 current canonical usage を優先して使う
- `README.md`、`docs/veil-design.md`、`skills/`、`index/` での hit を主要根拠とする
- common 側 usage は補助根拠に留める

## 3. Reclassification Rationale

### 必須

- `checkpoint`
  - progress / planning の骨格語で、common を含む現在運用で反復使用される
- `close verdict`
  - close 運用の中心語で、誤用時のノイズが大きい
- `current state`
  - current mainline canonical にすでに sample / rule 例として現れている
- `current surface`
  - governance / entry surface の中核概念である

### 推奨

- `common asset`
  - 統一価値はあるが、現在の VEIL 本線では fail-close 中心語ではない

### 観察

- `closeable`
- `common asset promotion`
- `comparison doc`
- `compress`
- `current order`
  - いずれも low-demand または文脈依存が強く、現段階で hard gate に残しすぎると過剰統制になる

## 4. Write Shape

target file shape は次とする。

```md
# c

## 必須

- checkpoint → チェックポイント
- close verdict → 完了判定
- current state → 今の状態
- current surface → 今の参照先

## 推奨

- common asset → 共通資産

## 観察

- closeable → 完了可能
- common asset promotion → 共通資産昇格
- comparison doc → 比較文書
- compress → 圧縮
- current order → 今の順番
```

## 5. Verification Principle

- migration 後に `c.md` readback を取る
- `veil-profile-audit.py` で `c.md` の legacy flat 解消を確認する
- 必要なら `veil-lint.py` の level 解釈は follow-up で spot check する
