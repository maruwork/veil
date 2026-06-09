# Requirements

## Goal

VEIL 本体の製品設計書を完成させ、`capture` と `normalize` の責務分担、候補化ルール、end-to-end flow、verification route を 1 本で読める状態にする。

## Scope

- `docs/veil-product-design.md`
- `index/project-current-work.md`
- `README.md`
- `docs/veil-design.md`
- product design packet 一式

## In Scope

- product purpose と non-goal
- primary users と use case
- `capture` / `normalize` / `sync` / `lint` の責務分担
- candidate rule の current product decision
- owner override points
- representative end-to-end flow
- completion verification route
- authority surface の参照先更新

## Out Of Scope

- runtime code の追加変更
- SQLite schema の変更
- UI / helper DB 系の復帰
- domain profile 分岐の詳細設計

## Acceptance

- 製品設計書 1 本で VEIL 本体の設計が読める
- `capture` と `normalize` の責務分担が曖昧でない
- candidate rule が current product decision として読める
- owner が override できる点が明記されている
- end-to-end flow と verification route が明記されている
- `current / README / design` が新しい product design 文書を authority として指している
