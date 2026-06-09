# Requirements

## Goal

VEIL を「土台実装はあるが運用ルール未確定の状態」から、「completion definition・未決・実装順が固定され、完了までの最短 route が current から一意に追える状態」へ進める。

## Scope

- `index/project-current-work.md`
- `README.md`
- `docs/veil-design.md`
- `workspace/20260607_candidate_rule_decision_sheet.md`
- completion planning packet 一式

## In Scope

- VEIL completion definition の固定
- completion に必要な phase 分解
- owner decision checkpoint の固定
- 実装順と verification route の固定
- current bundle の completion-oriented 切替

## Out Of Scope

- 新しい runtime 実装
- candidate threshold の新規確定
- `lint` / `sync` / `schema` の追加変更
- UI / helper DB 系の復帰

## Completion Definition

VEIL を completed と言えるのは、少なくとも次がそろった時だけとする。

1. mainline が `capture -> normalize -> sync -> lint` として current authority 上で閉じている
2. canonical route が SQLite で固定され、mirror / sync / lint / normalize の read-write route が一致している
3. candidate rule が user judgment で確定している
4. `capture` と `normalize` の responsibility boundary が固定されている
5. representative な end-to-end flow が verification できている
6. provisional heuristic が残る場合、その残りが completion blocker として current に明示されている

## Acceptance

- completion packet から `何が終わっていて、何が completion blocker か` が読める
- `README.md` と `docs/veil-design.md` に completion path が反映される
- `current work` が completion-oriented bundle に切り替わる
- owner decision checkpoint が completion path の必須 gate として固定される
