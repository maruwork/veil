# Requirements

## Theme

VEIL tuning wave 5: capture extraction tightening

## Goal

`veil-capture` の候補抽出基準を少し厳しくし、一般動詞や一時的な言い回しを拾いすぎないようにする。

## Scope In

- `skills/codex/veil-capture/SKILL.md`
- `skills/claude-code/veil-capture.md`
- `README.md`
- `docs/veil-design.md`
- `index/project-current-work.md`

## Scope Out

- lint runtime
- normalize runtime
- schema change
- UI

## Problem

- 現状の抽出基準は「2回以上」「複合語優先」まであるが、一般動詞やその場限りの言い回しがまだ候補に残りやすい
- 候補が増えすぎると capture の運用が重くなる

## Required Outcome

1. 一般動詞単体は基本的に保守的に扱う
2. 候補は `状態 / 判断 / 構造 / 運用ラベル` を優先する
3. `close` のような広すぎる一般動詞は、複合語か repeated context が強い時だけ見る

## Acceptance

- A1: skill の候補抽出基準が tightened される
- A2: README / design が tightened rule を説明する
- A3: current companion が wave 5 進行へ更新される

