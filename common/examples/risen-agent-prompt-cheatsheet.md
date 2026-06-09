# RISEN agent prompt cheatsheet

RISEN を使って agent instruction を組む時の最小チートシート。

## RISEN

- `Role`
- `Instructions`
- `Steps`
- `Expectation`
- `Narrowing`

## Minimal Template

```text
# Role
あなたは[役割名]です。[責任を1〜2行で書く]

# Instructions
[この agent が完了すべきコアタスクを1〜2文で書く]

# Steps
1. [ステップ1]: [実行内容]
2. [ステップ2]: [前提: ①の出力を引用してから開始] [実行内容]
3. [ステップ3]: [前提: ②の出力を引用してから開始] [実行内容]

# Expectation
- 必須フィールド1: [説明]
- 必須フィールド2: [説明]

# Narrowing
- [禁止事項1]
- [禁止事項2]
- 各ステップは前ステップの出力を引用してから開始すること
```

## Quick Rules

- `Expectation` を次 agent への入力契約として書く
- `Steps` は 3〜7 に収める
- 前ステップ引用を明示してスキップを防ぐ
- `Narrowing` は客観的・検証可能に書く
- `注意して` のような曖昧語を禁止する

## Good Output Example

- recommended_option
- evidence
- unresolved_risks
- next_action

## Use Boundary

このチートシートは agent instruction の汎用例であり、特定 repo の task id や path は含めない。
