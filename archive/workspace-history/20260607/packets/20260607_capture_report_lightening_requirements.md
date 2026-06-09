# Requirements

## Theme

VEIL tuning wave 3: capture report lightening

## Goal

`veil-capture` の完了報告を、必要な情報は維持したまま、毎回の読解負荷が低い形へ軽量化する。

## Scope In

- `skills/codex/veil-capture/SKILL.md`
- `skills/claude-code/veil-capture.md`
- `README.md`
- `docs/veil-design.md`
- `index/project-current-work.md`

## Scope Out

- capture runtime のロジック変更
- normalize / lint runtime
- UI

## Problem

- 現行 report は level-aware で正しいが、候補2 / 候補3 まで前面に出ると重い
- 日常運用では `採用 / 保留 / 同期 / 返答前検査` が速く見えれば十分なことが多い

## Required Outcome

1. 採用行は候補1を主表示にする
2. 候補2 / 候補3 は必要時だけ補助表示に落とす
3. 保留 / 同期 / 返答前検査 は短い固定形式にそろえる

## Acceptance

- A1: skills に軽量 report contract が入る
- A2: README の出力例が軽量版に変わる
- A3: design/current が新 contract を説明する

