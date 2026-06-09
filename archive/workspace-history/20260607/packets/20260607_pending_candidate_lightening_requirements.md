# Requirements

## Theme

VEIL tuning wave 6: 保留候補運用の軽量化

## Goal

`veil-normalize.py` と capture 運用で、`保留寄り` の候補を人がすぐ処理できる形に整理する。

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
- lint runtime の判定変更
- UI
- rule level 契約の変更

## Problem

- 現状の `保留寄り` は `今すぐ採らない` ことまでは見えるが、その後にどう扱うかが短く出ない
- capture 実行時に `保留` を読む負荷がまだ高く、`一旦見送る` と `後で再観察する` の区別が弱い
- `rules/*.md` を直接見ずに運用したいのに、保留候補の扱いだけは判断手順が頭の中に残っている

## Required Outcome

1. `保留寄り` 候補に、短い処理目安が出る
2. `今は見送る / 後で再観察する / 文脈が足りない` のように、保留内の扱いが分かる
3. capture skill と canonical docs が、その短い処理目安を読める
4. 既存の `classification_hint`, `suggested_level`, `selection_hint` は壊さない

## Acceptance

- A1: normalize result item に保留処理目安が入る
- A2: text 出力で保留処理目安が読める
- A3: skills/docs が `保留寄り` の短い扱い順を共有する
- A4: current companion が wave 6 の completion condition を正確に持つ

## Assumptions

- current mainline は SQLite canonical / markdown mirror のまま維持する
- `保留寄り` の tightening は runtime の軽量 heuristic で十分で、DB schema 変更は不要

## Risks

- 保留分類を増やしすぎると、逆に output が重くなる
- `外す寄り` と `保留寄り` の境界が曖昧だと運用が揺れる
- docs だけ先行すると runtime 契約とずれる
