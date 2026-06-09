# Requirements

## Theme

VEIL tuning wave 8: 保留候補 shortlist suppression

## Goal

`今は見送る` の候補を、capture 時の短い review 対象から外しやすくする。

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

- `保留寄り` の候補が増えると、`今は見送る` べき語まで毎回 review 対象として目に入る
- すでに `保留処理` はあるが、capture 時に「短い候補一覧から外してよいか」が直接は出ない
- 人が見る面は file ではなく一覧であるべきなので、low-value pending を先に薄くしたい

## Required Outcome

1. `今は見送る` 候補に shortlist 抑制の短い目安が付く
2. `後で再観察する` や `文脈不足で保留` は short review に残せる
3. docs / skills / current companion がその扱いを共有する

## Acceptance

- A1: normalize result item に shortlist hint が入る
- A2: `今は見送る` 候補は `短い review から外す寄り` と読める
- A3: README / design / skills / current companion が同じ扱い順を持つ
