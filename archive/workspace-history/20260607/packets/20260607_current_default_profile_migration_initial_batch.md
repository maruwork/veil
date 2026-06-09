# Current Default Profile Migration Initial Batch

## 1. Batch Goal

real `~/.veil/rules/` の section-aware migration を始める時、最初に触る file を限定し、再配置判断軸を固定する。

## 2. First Batch

rule 数と legacy 密度から、初回 batch は次とする。

1. `c.md` `10`
2. `s.md` `9`
3. `d.md` `5`
4. `p.md` `5`
5. `r.md` `5`

この 5 file で全 `34` rule を占める。

## 3. Reclassification Rules

### 必須に残す

- 禁止語
- VEIL 基幹語
- 高需要で揺れると困る語
- 現在の closing report や設計説明で繰り返し使う語

### 推奨へ落とす

- 統一したいが、違反で即 fail-close までは不要な語
- 代替表現が自然に成立しやすい語

### 観察へ送る

- 低頻度語
- 文脈依存が強い語
- 意味がまだ固まっていない語

## 4. Execution Constraints

- migration 実行 wave では 1 file ずつ進める
- real rules 編集前に each file の readback を取る
- file 全体をいきなり `推奨` / `観察` 化しない
- まず `## 必須` を明示し、その後で必要分だけ降格する

## 5. Stop Conditions

- file 内の語の意味境界が強く曖昧
- 既存運用で fail-close に使っている語を軽率に降格しそうになる
- current session だけでは判断材料が足りない
