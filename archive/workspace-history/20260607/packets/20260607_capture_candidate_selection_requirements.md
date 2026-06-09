# Requirements

## Theme

VEIL tuning wave 4: capture candidate selection narrowing

## Goal

`veil-normalize.py` の結果に、capture 時に最初に見るべき候補の絞り込み目安を追加する。

## Scope In

- `veil-normalize.py`
- `README.md`
- `docs/veil-design.md`
- `skills/codex/veil-capture/SKILL.md`
- `skills/claude-code/veil-capture.md`
- `index/project-current-work.md`

## Scope Out

- lint runtime
- schema change
- capture 本体ロジックの大幅再設計
- UI

## Problem

- 現状の normalize は cluster ごとの情報は十分あるが、capture 時に `どれから見るか` を一目で切りにくい
- 毎回すべての候補を同じ重みで見ると運用が重い

## Required Outcome

1. normalize result に候補選別の短い目安が入る
2. `先に採る候補 / 保留寄り / 外す寄り` の 3 区分で見られる
3. 既存の classification と level suggestion は維持される

## Acceptance

- A1: normalize result item に selection hint が入る
- A2: text 出力で selection hint が見える
- A3: skills/docs が `selection hint を見て上位だけ採る` と読める

