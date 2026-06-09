# SQLite Stage 1 Task Design

## 1. Parent Theme

- SQLite canonical migration Stage 1

## 2. Task Designs

### Task ID: S1-A

1. `Task ID`
   - `S1-A`
2. `親テーマ`
   - SQLite canonical migration Stage 1
3. `親チェックポイント`
   - schema support 追加
4. `目的`
   - SQLite schema と Markdown parser を shared module にまとめる
5. `このタスクが必要な理由`
   - import/readback の再利用核になるため
6. `着手条件`
   - Stage 1 basic design が読める
7. `入力`
   - Stage 1 requirements/basic design
   - current lint/normalize/audit parser code
8. `読んでよい場所`
   - `veil-lint.py`
   - `veil-normalize.py`
   - `veil-profile-audit.py`
   - Stage 1 packet 群
9. `書いてよい場所`
   - `veil_rule_store.py`
10. `触ってはいけない場所`
   - existing runtime behavior inside lint/normalize/audit
11. `やること`
   - schema 定義
   - Markdown rule parse helper
   - DB init/import/readback helper
12. `期待する出力`
   - reusable shared module
13. `合格条件`
   - init/import/readback 関数が揃う
14. `失敗条件`
   - shared helper が current rule format を読み取れない
15. `停止条件`
   - schema 決定に owner 判断が必要
16. `差し戻し条件`
   - helper が Stage 2 用 read path 切替まで抱え込む
17. `人判断へ上げる条件`
   - canonical schema field の追加裁定が必要
18. `証拠`
   - `veil_rule_store.py`
19. `結果の記録先`
   - repo files
20. `最終判定者`
   - owner

### Task ID: S1-B

1. `Task ID`
   - `S1-B`
2. `親テーマ`
   - SQLite canonical migration Stage 1
3. `親チェックポイント`
   - import/readback CLI 追加
4. `目的`
   - init-db / import-rules / readback を呼べる CLI を追加する
5. `このタスクが必要な理由`
   - shared module だけでは運用入口にならないため
6. `着手条件`
   - `veil_rule_store.py` の API が見えている
7. `入力`
   - shared module
8. `読んでよい場所`
   - `veil_rule_store.py`
   - Stage 1 packet 群
9. `書いてよい場所`
   - `veil-db.py`
10. `触ってはいけない場所`
   - existing runtime scripts
11. `やること`
   - argparse CLI
   - init/import/readback subcommands
   - text/JSON output
12. `期待する出力`
   - support CLI
13. `合格条件`
   - 3 subcommand が動く
14. `失敗条件`
   - CLI が workspace smoke を通せない
15. `停止条件`
   - CLI contract が shared module と噛み合わない
16. `差し戻し条件`
   - Stage 2 の read path 切替を混ぜる
17. `人判断へ上げる条件`
   - command contract への owner 判断が必要
18. `証拠`
   - `veil-db.py`
19. `結果の記録先`
   - repo files
20. `最終判定者`
   - owner

### Task ID: S1-C

1. `Task ID`
   - `S1-C`
2. `親テーマ`
   - SQLite canonical migration Stage 1
3. `親チェックポイント`
   - smoke evidence 生成
4. `目的`
   - workspace fixture で init/import/readback を確認する
5. `このタスクが必要な理由`
   - home dir write を使わず Stage 1 完了を示すため
6. `着手条件`
   - CLI が動く
7. `入力`
   - `veil-db.py`
   - fixture rules
8. `読んでよい場所`
   - workspace fixture
   - `veil-db.py`
9. `書いてよい場所`
   - `workspace/veil_stage1_rules_fixture/`
   - `workspace/veil_stage1_smoke_check.py`
   - workspace smoke DB
10. `触ってはいけない場所`
   - real `~/.veil/` home dir content
11. `やること`
   - fixture を作る
   - smoke script を作る
   - readback count を確認する
12. `期待する出力`
   - repeatable smoke evidence
13. `合格条件`
   - imported rows の件数と level が確認できる
14. `失敗条件`
   - smoke が workspace 内だけで完結しない
15. `停止条件`
   - fixture で parser edge case が崩れる
16. `差し戻し条件`
   - smoke が docs 更新作業にすり替わる
17. `人判断へ上げる条件`
   - fixture ではなく real home rules を使う必要が出る
18. `証拠`
   - smoke script output
   - workspace DB
19. `結果の記録先`
   - workspace files
20. `最終判定者`
   - owner
