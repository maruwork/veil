# Current Default Profile Migration Planning Basic Design

## 1. Migration Principle

- 旧 flat rule はまず `## 必須` の下へ移す
- そこから `推奨` と `観察` へ落とせるものだけを再配置する
- いきなり全 file 一括移行しない

## 2. Ordering Principle

- rule 数の多い file から先に着手する
- current VEIL 基幹語や高需要語を含む file を優先する
- 1 wave で扱う file 数を絞る

## 3. Reclassification Principle

### 必須に残す

- 禁止語
- VEIL 基幹語
- 高需要で揺れると困る語

### 推奨へ落とす

- できれば寄せたいが hard gate までは不要な語

### 観察へ落とす

- 低頻度語
- 文脈依存語
- まだ判断を寝かせたい語

## 4. Initial Batch

- `c.md`
- `s.md`
- `d.md`
- `p.md`
- `r.md`
