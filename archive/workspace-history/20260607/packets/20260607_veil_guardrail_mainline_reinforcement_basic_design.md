# VEIL Guardrail Mainline Reinforcement Basic Design

## 1. Architecture

### Current Mainline

`capture -> normalize -> sync -> lint`

現状の mainline 自体は見えているが、次の弱さが残っている。

- `capture` が optional helper に見えやすい
- `lint` が verify tool ではあっても required gate としては弱い
- rule に厳格度の差がないため、全面統制へ流れやすい
- 業界別転用時の差し替え面が文書化されていない

### Target Mainline

`close trigger -> capture -> normalize -> rules update -> sync -> pre-response lint -> report`

- `close trigger`
  - 会話区切り、task close、返答 close を mainline entry にする
- `capture`
  - 問題語を拾う
- `normalize`
  - 揺れを寄せ、既存 rule と統合候補を出す
- `rules update`
  - high-demand / high-impact 語だけを正本へ反映する
- `sync`
  - AI が読む面へ参照明記する
- `pre-response lint`
  - 最終 prose が required rule に従っているかを見る
- `report`
  - 採用語、保留語、warning、未検証面を閉じ報告する

## 2. Control Model

### Strictness Layers

#### Layer A: 必須

- 対象:
  - 禁止語
  - VEIL 基幹語
  - high-demand で揺れると困る語
- 扱い:
  - lint violation は修正必須
  - fail-close 対象

#### Layer B: 推奨

- 対象:
  - できれば寄せたい語
  - まだ fail-close までは不要な統一候補
- 扱い:
  - warning のみ
  - report に残す

#### Layer C: 観察

- 対象:
  - 低頻度語
  - 文脈依存語
  - 未確定の project 固有語
- 扱い:
  - capture / normalize / frequency 集計のみ
  - 正本採用を急がない

### Why This Model

VEIL の価値は guardrail にあるが、全語彙を hard gate にすると自然文生成を壊す。よって「フローは強く縛る、語彙は高影響範囲だけ強く縛る」の 2 段構えを採る。

## 3. Core and Profile Separation

### VEIL Core

- `veil-capture`
- `veil-normalize.py`
- `veil-sync.py`
- `veil-lint.py`
- mainline flow
- rule レベル骨格
- 判別順骨格

### Domain Profile

- 業界別 rules
- 禁止語集合
- high-demand 語集合
- 定義語方針
- 固有名を残す基準
- lint strictness の既定値

### Recommended Direction

VEIL は `core + current default profile` の形で説明する。current default profile は technical writing 向けとし、regulated profile などは follow-up wave で扱う。

## 4. Classification Design

### Current Pain

語の種類が未分離だと、固有名を残すべきか、一般語として訳すべきか、業務ラベルとして定義すべきか、禁止語として落とすべきかが混ざる。

### Target Classification Flow

1. 固有名として残すか
2. 一般語として訳すか
3. 業務ラベル / 定義語として固定するか
4. 禁止語として落とすか
5. どれにも切れなければ保留する

### Exclusions

次は統制対象外または弱統制とする。

- コード識別子
- ファイル名
- path
- CLI option
- schema key
- その他の機械処理語

## 5. Operations Design

### Capture Trigger

- task close
- 会話区切り
- 長めの説明文を返す前の最終整理

### Lint Trigger

- 最終日本語 prose を返す直前
- 変更報告、設計説明、完了報告などの user-facing prose

### Fail-Close Boundary

- `必須` 違反のみ fail-close
- `推奨` は warning
- `観察` は lint failure に使わない

## 6. Documentation Design

次の canonical 面で同じ主語にそろえる。

- `AGENTS.md`
- `README.md`
- `docs/veil-design.md`
- `skills/codex/veil-capture/SKILL.md`
- `skills/claude-code/veil-capture.md`

揃えるべき文脈は次。

- VEIL は technical writing guardrail
- mainline は `capture -> normalize -> sync -> lint`
- `capture` は閉じ処理
- `lint` は返答前 gate
- rule は `必須 / 推奨 / 観察`
- core と profile を分ける

## 7. Deferred Design Questions

- rule file に level をどう表現するか
- `推奨` と `観察` を `veil-lint.py` にどう出すか
- profile を `~/.veil/` 配下でどう切るか
- default profile の seed 語集合をどこで管理するか
