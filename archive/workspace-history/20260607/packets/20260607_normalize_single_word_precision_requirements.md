# Requirements

## Theme

VEIL tuning wave 2: normalize single-word precision

## Goal

`veil-normalize.py` の単語候補判定を少しだけ改善し、単語だから即 `境界が曖昧` へ落ちるケースを減らす。

## Scope In

- `veil-normalize.py`
- `README.md`
- `docs/veil-design.md`
- `index/project-current-work.md`

## Scope Out

- normalize 全面再設計
- capture report 再設計
- lint runtime
- profile tuning

## Problem

- 現状の `classify_candidate_hint()` は lowercase 単語を強く `曖昧` へ倒す
- technical writing では単語単位の一般語も多く、保守的すぎると候補精度が落ちる

## Required Outcome

1. 名詞化された一般語らしい単語は `説明語候補` へ寄る
2. 同じ lowercase 単語が複数回出る場合は説明語側へ寄る
3. 既存の識別子 / 固有名の保守性は崩さない

## Acceptance

- A1: single-word lowercase candidate の一部が `説明語候補` へ改善される
- A2: `summary` のような単語は過剰に hard gate 提案されない
- A3: `status=close`、path、mixed-case の既存判定は維持される

