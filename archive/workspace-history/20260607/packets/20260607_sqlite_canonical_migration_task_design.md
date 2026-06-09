# SQLite Canonical Migration Task Design

## 1. Parent Theme

- SQLite canonical migration

## 2. Task Designs

### Task ID: T-A

1. `Task ID`
   - `T-A`
2. `親テーマ`
   - SQLite canonical migration
3. `親チェックポイント`
   - `CP-1 success subject 固定`
4. `目的`
   - SQLite canonical migration を current 主題として packet と current work に固定する
5. `このタスクが必要な理由`
   - current 主題が branch-first の残骸に戻ると以後の packet が別主語になるため
6. `着手条件`
   - decision note と current work が読める
7. `入力`
   - `workspace/20260607_sqlite_canonical_migration_decision_note.md`
   - `index/project-current-work.md`
8. `読んでよい場所`
   - `common/`
   - `workspace/20260607_sqlite_canonical_migration_*.md`
   - `index/project-current-work.md`
9. `書いてよい場所`
   - `workspace/20260607_sqlite_canonical_migration_requirements.md`
   - `index/project-current-work.md`
10. `触ってはいけない場所`
   - runtime files
   - `~/.veil/rules/`
   - UI / archive
11. `やること`
   - current bundle の success subject、scope、next action を SQLite canonical migration に一致させる
12. `期待する出力`
   - packet と current work の主語整合
13. `合格条件`
   - `index/project-current-work.md` の `next action` が SQLite Stage 1 入口を指す
14. `失敗条件`
   - branch-first / UI / helper DB の話題が current 主題として残る
15. `停止条件`
   - current work と decision note が衝突する
16. `差し戻し条件`
   - success subject が複数 capability にまたがる
17. `人判断へ上げる条件`
   - owner が SQLite canonical 自体を再考する場合
18. `証拠`
   - updated `index/project-current-work.md`
19. `結果の記録先`
   - `index/project-current-work.md`
20. `最終判定者`
   - owner

### Task ID: T-B

1. `Task ID`
   - `T-B`
2. `親テーマ`
   - SQLite canonical migration
3. `親チェックポイント`
   - `CP-2 canonical/generated boundary 固定`
4. `目的`
   - SQLite と Markdown の責務境界を architecture と data contract で固定する
5. `このタスクが必要な理由`
   - ここが曖昧だと二重 authority のまま切替が進むため
6. `着手条件`
   - requirements が success subject と scope を固定済み
7. `入力`
   - requirements packet
   - current design understanding
8. `読んでよい場所`
   - `workspace/20260607_sqlite_canonical_migration_requirements.md`
   - `README.md`
   - `docs/veil-design.md`
9. `書いてよい場所`
   - `workspace/20260607_sqlite_canonical_migration_basic_design.md`
10. `触ってはいけない場所`
   - runtime files
   - real rules dir
11. `やること`
   - canonical store、generated role、tool routing、option comparison、data table を書く
12. `期待する出力`
   - SQLite canonical boundary が一意に読める basic design
13. `合格条件`
   - `SQLite = canonical`、`Markdown = generated artifact`、`tool routing` が同時に読める
14. `失敗条件`
   - Markdown が canonical とも generated とも読める文言が残る
15. `停止条件`
   - DB path、generator route、unique 制約の未決が task を壊す水準まで増える
16. `差し戻し条件`
   - basic design が requirements と別主語になる
17. `人判断へ上げる条件`
   - DB path や canonical shape に owner 判断が必要
18. `証拠`
   - updated basic design packet
19. `結果の記録先`
   - `workspace/20260607_sqlite_canonical_migration_basic_design.md`
20. `最終判定者`
   - owner

### Task ID: T-C

1. `Task ID`
   - `T-C`
2. `親テーマ`
   - SQLite canonical migration
3. `親チェックポイント`
   - `CP-3 stage 順固定`
4. `目的`
   - Stage 1-4 の切替順と依存順を implementation plan に固定する
5. `このタスクが必要な理由`
   - 一括切替や逆順切替を防ぐため
6. `着手条件`
   - basic design で routing が定義済み
7. `入力`
   - requirements packet
   - basic design packet
8. `読んでよい場所`
   - SQLite migration packet 群
   - `common/templates/implementation-plan-template.md`
9. `書いてよい場所`
   - `workspace/20260607_sqlite_canonical_migration_implementation_plan.md`
10. `触ってはいけない場所`
   - runtime files
   - generated or real rules outputs
11. `やること`
   - packet minimum fields、decision record、preconditions、files、acceptance mapping、verification、checkpoints、work order を埋める
12. `期待する出力`
   - Stage 1 前に必要な checkpoint が読める implementation plan
13. `合格条件`
   - `CP-1` から `CP-4` と対応 task が読み取れる
14. `失敗条件`
   - Stage 順が曖昧、または Stage 1 の前に docs authority 更新を始める
15. `停止条件`
   - 依存順が requirements/basic design から一意に決まらない
16. `差し戻し条件`
   - acceptance mapping が verification とつながらない
17. `人判断へ上げる条件`
   - staged coexistence を owner が許容しない場合
18. `証拠`
   - updated implementation plan packet
19. `結果の記録先`
   - `workspace/20260607_sqlite_canonical_migration_implementation_plan.md`
20. `最終判定者`
   - owner

### Task ID: T-D

1. `Task ID`
   - `T-D`
2. `親テーマ`
   - SQLite canonical migration
3. `親チェックポイント`
   - `CP-4 Stage 1 着手入口固定`
4. `目的`
   - Stage 1 schema/import/smoke readback に入れる task-design を 20 項目で固定する
5. `このタスクが必要な理由`
   - `common` の execution-readiness gate を満たさないまま実装へ入らないため
6. `着手条件`
   - implementation plan で checkpoints と作業順が固定済み
7. `入力`
   - requirements
   - basic design
   - implementation plan
8. `読んでよい場所`
   - SQLite migration packet 群
   - `common/policies/execution-readiness-gate-policy.md`
9. `書いてよい場所`
   - `workspace/20260607_sqlite_canonical_migration_task_design.md`
10. `触ってはいけない場所`
   - runtime files
   - external home dir DB path
11. `やること`
   - parent checkpoint ごとに task spec を書き、Stage 1 schema/import/smoke の入口まで明示する
12. `期待する出力`
   - 実装開始に使える task-design packet
13. `合格条件`
   - 各 task が 20 required fields を持つ
14. `失敗条件`
   - `目的 / 着手条件 / 書いてよい場所 / 停止条件 / 証拠` のどれかが欠ける
15. `停止条件`
   - Stage 1 実装 task の scope が 1 束に収まらない
16. `差し戻し条件`
   - task が checkpoint から切れている
17. `人判断へ上げる条件`
   - SQLite path や persistent write approval の扱いに owner 裁定が必要
18. `証拠`
   - updated task design packet
19. `結果の記録先`
   - `workspace/20260607_sqlite_canonical_migration_task_design.md`
20. `最終判定者`
   - owner
