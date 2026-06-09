# Requirements

## Theme

VEIL precision / usability tuning wave 1: lint fix guidance

## Goal

`veil-lint.py` の違反出力を、単に原語残存を示すだけでなく、どの語を何へ直せばよいかがすぐ分かる形へ改善する。

## Scope In

- `veil-lint.py`
- `README.md`
- `docs/veil-design.md`
- `index/project-current-work.md`

## Scope Out

- normalize 判別精度の改善
- capture report の再設計
- profile tuning
- UI

## Problem

- 現状の `veil-lint.py` は違反語と推奨語を返すが、修正単位が弱く、直し方が一目で分かりにくい
- 返答前 gate としては、検出精度だけでなく修正しやすさが重要

## Required Outcome

1. violation / warning ごとに `何を何へ直すか` が一目で分かる
2. JSON でも text でも同じ guidance が返る
3. 既存の exit code 契約は壊さない

## Acceptance

- A1: lint result item に fix guidance が入る
- A2: text 出力で `match -> preferred` が見える
- A3: json 出力で hit 単位の suggestion が見える
- A4: violation / warning / clean / skip の既存契約は維持される

