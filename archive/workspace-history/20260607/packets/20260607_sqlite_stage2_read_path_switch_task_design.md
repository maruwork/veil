# SQLite Stage 2 Read Path Switch Task Design

## 1. Parent Theme

- SQLite canonical migration Stage 2

## 2. Task Designs

### Task ID: S2-A

1. `Task ID`
   - `S2-A`
2. `親テーマ`
   - SQLite canonical migration Stage 2
3. `親チェックポイント`
   - Stage 2 order fixed
4. `目的`
   - Stage 2 の read path switch 順を packet に固定する
5. `このタスクが必要な理由`
   - 先に順序を決めないと lint 側へ逸脱しやすいため
6. `着手条件`
   - Stage 1 current writeback が完了している
7. `入力`
   - Stage 1 reports
   - current work
8. `読んでよい場所`
   - Stage 1 packet/report
   - `veil-profile-audit.py`
   - `veil-normalize.py`
   - `veil-lint.py`
9. `書いてよい場所`
   - Stage 2 packet files
10. `触ってはいけない場所`
   - lint/normalize runtime behavior
11. `やること`
   - order, scope, first-wave target を定義する
12. `期待する出力`
   - Stage 2 packet
13. `合格条件`
   - `audit -> normalize -> lint` が packet で読める
14. `失敗条件`
   - 順序が曖昧なまま実装へ進む
15. `停止条件`
   - first-wave target が support runtime に定まらない
16. `差し戻し条件`
   - Stage 2 scope に capture/sync が混ざる
17. `人判断へ上げる条件`
   - owner が順序を変えたい場合
18. `証拠`
   - Stage 2 packet files
19. `結果の記録先`
   - `workspace/20260607_sqlite_stage2_read_path_switch_*.md`
20. `最終判定者`
   - owner

### Task ID: S2-B

1. `Task ID`
   - `S2-B`
2. `親テーマ`
   - SQLite canonical migration Stage 2
3. `親チェックポイント`
   - audit SQLite read added
4. `目的`
   - `veil-profile-audit.py` に SQLite source route を加える
5. `このタスクが必要な理由`
   - first wave 実装対象だから
6. `着手条件`
   - Stage 2 packet で order が fixed
7. `入力`
   - `veil_rule_store.py`
   - existing `veil-profile-audit.py`
8. `読んでよい場所`
   - Stage 2 packet
   - Stage 1 support code
9. `書いてよい場所`
   - `veil-profile-audit.py`
10. `触ってはいけない場所`
   - `veil-normalize.py`
   - `veil-lint.py`
11. `やること`
   - `--db` option
   - source selection
   - db summary/report
12. `期待する出力`
   - dual-source audit CLI
13. `合格条件`
   - rules-dir と db 両方で audit 可能
14. `失敗条件`
   - rules-dir 互換が壊れる
15. `停止条件`
   - source contract が曖昧
16. `差し戻し条件`
   - normalize/lint switch が混ざる
17. `人判断へ上げる条件`
   - source precedence で owner 判断が必要
18. `証拠`
   - CLI smoke output
19. `結果の記録先`
   - execution report
20. `最終判定者`
   - owner
