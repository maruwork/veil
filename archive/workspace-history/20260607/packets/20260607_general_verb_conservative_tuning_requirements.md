# Requirements

## Theme

VEIL tuning wave 7: 一般動詞の追加保守 tuning

## Goal

`veil-normalize.py` が single-word の一般動詞とその軽い活用形を、今より保守的に扱うようにする。

## Scope In

- `veil-normalize.py`
- `README.md`
- `docs/veil-design.md`
- `skills/codex/veil-capture/SKILL.md`
- `skills/claude-code/veil-capture.md`
- `index/project-current-work.md`

## Scope Out

- schema change
- SQLite canonical route の再設計
- lint runtime の変更
- UI
- capture 全体ロジックの再設計

## Problem

- 現状でも `close` のような一般動詞単体は保守寄りだが、軽い活用形や近縁形の扱いがまだ弱い
- 頻度が上がるだけで single-word 動詞が説明語候補へ寄る余地があり、保守側へ倒し切れていない
- capture 側では一般動詞単体を抑える契約を入れているので、normalize 側も同じ方向にそろえる必要がある

## Required Outcome

1. 一般動詞単体とその軽い活用形を保守的に扱う
2. 頻度だけでは説明語候補へ上げない語群が増える
3. docs / skills / current companion がその保守契約を共有する

## Acceptance

- A1: `close / closed / closing / updates` のような一般動詞系が保守寄りに返る
- A2: text / JSON の出力契約は壊れない
- A3: README / design / skills / current companion が追加保守 tuning を読める

## Risks

- 保守側に倒しすぎると、本来は説明語として採りたい語まで抑える
- 活用形判定を増やしすぎると heuristic が重くなる
