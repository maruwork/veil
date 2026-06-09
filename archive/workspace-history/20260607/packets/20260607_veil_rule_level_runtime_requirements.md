# VEIL Rule Level Runtime Requirements

## 1. Overview

### 目的

VEIL の `必須 / 推奨 / 観察` を文書上の方針ではなく runtime semantics として実装する。

この wave では特に次を行う。

- `~/.veil/rules/*.md` に rule level を physical に持てるようにする
- `veil-lint.py` が level ごとに fail / warning / ignore を切り替えられるようにする
- `veil-normalize.py` が既存 rule の level を読めるようにする

### 背景

- current canonical docs では rule 3 層を定義済み
- ただし current runtime は `- original → preferred` を一律 violation として扱う
- このままだと `推奨` と `観察` が設計だけで、実装が伴っていない

### 参考 / 根拠

- `README.md`
- `docs/veil-design.md`
- `AGENTS.md`
- `veil-lint.py`
- `veil-normalize.py`
- `workspace/20260607_veil_guardrail_mainline_reinforcement_requirements.md`
- `workspace/20260607_veil_guardrail_mainline_reinforcement_basic_design.md`
- `workspace/20260607_veil_guardrail_mainline_reinforcement_task_design.md`

## 2. Scope

### In Scope

- rule file に `必須 / 推奨 / 観察` section を持てるようにする
- heading 単位で rule level を解釈する parser を `veil-lint.py` と `veil-normalize.py` に入れる
- `veil-lint.py` の status を `clean / warning / violation / skip` で返せるようにする
- `必須` は non-zero exit、`推奨` は zero exit warning、`観察` は lint failure から除外する
- canonical docs を実装に追従させる

### Out of Scope

- `veil-sync.py` の動作変更
- `veil-capture` の自動 level 決定実装
- domain profile 切り替え機構
- `~/.veil/rules/` 実データの自動 migration

### Assumptions and Constraints

- backward compatibility のため、heading のない既存 rule line は `必須` 扱いにする
- rule line format の基本は引き続き `- original → preferred`
- section heading は markdown heading として書ける形にする

## 3. Success Criteria

- `~/.veil/rules/*.md` で `## 必須`, `## 推奨`, `## 観察` を書ける
- `veil-lint.py` が `必須` だけ non-zero exit にする
- `veil-lint.py` が `推奨` を warning として分離表示する
- `veil-normalize.py` が existing match の level を返せる
- `README.md` と `docs/veil-design.md` の rule format 例が実装と一致する

## 4. Functional Requirements

1. parser は markdown heading から現在 level を切り替えられること
2. parser は heading のない rule line を `必須` 扱いできること
3. `veil-lint.py` は `必須` violation を `violations`、`推奨` hit を `warnings` に分けること
4. `veil-lint.py` は `観察` rule を lint failure 対象にしないこと
5. JSON 出力は level と status を持つこと
6. text 出力は `CLEAN / WARN / NG / SKIP` を区別できること
7. `veil-normalize.py` は existing rule level を結果に含めること

## 5. Non-Functional Requirements

- additive な変更であること
- 標準ライブラリのみ
- rule 実データを自動破壊しないこと
- verify は `py_compile` と small smoke で終えられること

## 6. Risks

- heading typo を parser が level heading と認識しない
- `推奨` warning の text output が増えて読みづらくなる
- 既存 rule が多い場合、全部 `必須` 扱いになるため warning への緩和は手作業で必要

## 7. Deferred Follow-up

- `veil-capture` の level 候補自動提案
- `観察` 専用の別棚や profile layout
- `rule owner` や approval lifecycle の導入
