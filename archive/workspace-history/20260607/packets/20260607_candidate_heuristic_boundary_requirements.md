# Requirements

## Goal

`normalize` と `capture` まわりに積み上がった候補化細則を、正本ルールではなく未承認 heuristic として境界づける。

## Scope

- `index/project-current-work.md`
- `README.md`
- `docs/veil-design.md`

## In Scope

- approved foundation と provisional heuristic の区別明記
- current bundle の切替
- `normalize tuning close` 後の次判断を user confirmation 前提へ戻すこと

## Out Of Scope

- runtime behavior の巻き戻し
- 新しい candidate threshold の追加
- `lint` / `sync` / `schema` の変更
- `skills/` の新規 tightening

## Acceptance

- `current work` で active bundle が heuristic boundary に切り替わっている
- `README.md` で single-word / phrase の細かい threshold が未承認 heuristic だと読める
- `docs/veil-design.md` で same category の細則が governance rule ではなく provisional だと読める
- approved foundation として残すものが current から読める
