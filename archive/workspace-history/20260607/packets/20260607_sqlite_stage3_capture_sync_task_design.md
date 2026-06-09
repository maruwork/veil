# SQLite Stage 3 Capture Sync Task Design

## 1. Parent Theme

- SQLite canonical migration Stage 3

## 2. Task Designs

### Task ID: S3-1

1. `Task ID`
   - `S3-1`
2. `親テーマ`
   - SQLite canonical migration Stage 3
3. `親チェックポイント`
   - helper / CLI write route fixed
4. `目的`
   - SQLite canonical へ 1 rule を追加更新し、mirror を生成する helper/CLI を実装する
5. `このタスクが必要な理由`
   - capture skill が DB canonical へ書ける具体 route が必要なため
6. `着手条件`
   - Stage 2 完了
7. `入力`
   - existing schema/import/readback helper
8. `読んでよい場所`
   - `veil_rule_store.py`
   - `veil-db.py`
9. `書いてよい場所`
   - same files
10. `触ってはいけない場所`
   - UI
11. `やること`
   - upsert helper と export helper を追加し、CLI subcommand をつなぐ
12. `期待する出力`
   - `upsert-rule`, `export-mirror`
13. `合格条件`
   - CLI から 1 rule を DB へ書け、mirror が生成される
14. `失敗条件`
   - canonical write route が file 直書きのまま残る
15. `停止条件`
   - schema 契約を壊さずに upsert できない
16. `差し戻し条件`
   - schema redesign が必要になる
17. `人判断へ上げる条件`
   - unique key 契約変更が必要になる
18. `証拠`
   - smoke output
19. `結果の記録先`
   - execution report
20. `最終判定者`
   - owner

### Task ID: S3-2

1. `Task ID`
   - `S3-2`
2. `親テーマ`
   - SQLite canonical migration Stage 3
3. `親チェックポイント`
   - sync route fixed
4. `目的`
   - `veil-sync.py` を DB-first mirror generate sync へ切り替える
5. `このタスクが必要な理由`
   - canonical route と AI-readable mirror route を runtime で閉じるため
6. `着手条件`
   - S3-1 完了
7. `入力`
   - helper/CLI
8. `読んでよい場所`
   - `veil-sync.py`
   - `veil_rule_store.py`
9. `書いてよい場所`
   - same files
10. `触ってはいけない場所`
   - unrelated runtime
11. `やること`
   - DB 優先 mirror refresh と fallback route を実装する
12. `期待する出力`
   - sync 前に mirror refresh される runtime
13. `合格条件`
   - DB source から同期できる
14. `失敗条件`
   - DB があるのに rules-dir only route を通る
15. `停止条件`
   - fallback 互換を維持できない
16. `差し戻し条件`
   - targets/config 契約変更が必要になる
17. `人判断へ上げる条件`
   - sync source policy を変える必要がある
18. `証拠`
   - smoke output
19. `結果の記録先`
   - execution report
20. `最終判定者`
   - owner

### Task ID: S3-3

1. `Task ID`
   - `S3-3`
2. `親テーマ`
   - SQLite canonical migration Stage 3
3. `親チェックポイント`
   - docs/skills/current aligned
4. `目的`
   - docs/skills/current work を new write route へ追従させる
5. `このタスクが必要な理由`
   - mainline surface の誤誘導を防ぐため
6. `着手条件`
   - S3-2 完了
7. `入力`
   - updated runtime
8. `読んでよい場所`
   - `README.md`
   - `docs/veil-design.md`
   - `skills/*/veil-capture*`
   - `index/project-current-work.md`
9. `書いてよい場所`
   - same docs
10. `触ってはいけない場所`
   - UI
11. `やること`
   - file 直書き前提を外し、DB canonical route を明記する
12. `期待する出力`
   - consistent current route wording
13. `合格条件`
   - capture skill が DB write -> mirror export -> sync を指示する
14. `失敗条件`
   - `~/.veil/rules/*.md` 直書きが mainline guidance に残る
15. `停止条件`
   - docs update が code rewrite を先回りする
16. `差し戻し条件`
   - runtime 実装と docs が一致しない
17. `人判断へ上げる条件`
   - owner が write route wording を変えたい場合
18. `証拠`
   - readback
19. `結果の記録先`
   - execution report
20. `最終判定者`
   - owner
