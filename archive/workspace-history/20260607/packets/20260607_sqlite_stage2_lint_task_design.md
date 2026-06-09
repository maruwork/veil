# SQLite Stage 2 Lint Task Design

## 1. Parent Theme

- SQLite canonical migration Stage 2 lint wave

## 2. Task Designs

### Task ID: S2L-A

1. `Task ID`
   - `S2L-A`
2. `親テーマ`
   - SQLite canonical migration Stage 2 lint wave
3. `親チェックポイント`
   - lint wave packet fixed
4. `目的`
   - lint wave の scope と contract を packet に固定する
5. `このタスクが必要な理由`
   - mainline gate を壊さず source switch するため
6. `着手条件`
   - normalize wave completed
7. `入力`
   - normalize wave report
   - current lint code
8. `読んでよい場所`
   - normalize wave packet/report
   - `veil-lint.py`
   - `veil_rule_store.py`
9. `書いてよい場所`
   - lint wave packet files
10. `触ってはいけない場所`
   - capture/sync implementation
11. `やること`
   - source selection / level mapping / smoke items を定義する
12. `期待する出力`
   - lint wave packet
13. `合格条件`
   - violation/warning/clean parity が packet で読める
14. `失敗条件`
   - scope に docs canonical update が混ざる
15. `停止条件`
   - skip policy が曖昧
16. `差し戻し条件`
   - source selection が hidden
17. `人判断へ上げる条件`
   - owner が output contract change を望む場合
18. `証拠`
   - lint wave packet
19. `結果の記録先`
   - `workspace/20260607_sqlite_stage2_lint_*.md`
20. `最終判定者`
   - owner

### Task ID: S2L-B

1. `Task ID`
   - `S2L-B`
2. `親テーマ`
   - SQLite canonical migration Stage 2 lint wave
3. `親チェックポイント`
   - lint SQLite read added
4. `目的`
   - `veil-lint.py` に SQLite source route を加える
5. `このタスクが必要な理由`
   - mainline gate の source switch を閉じるため
6. `着手条件`
   - lint wave packet fixed
7. `入力`
   - `veil-lint.py`
   - `veil_rule_store.py`
8. `読んでよい場所`
   - lint wave packet
   - Stage 1 helper
9. `書いてよい場所`
   - `veil_rule_store.py`
   - `veil-lint.py`
10. `触ってはいけない場所`
   - sync/capture write path
11. `やること`
   - db rule loader
   - `--db` option
   - source info payload
   - violation/warning parity
12. `期待する出力`
   - dual-source lint CLI
13. `合格条件`
   - db / rules-dir 両方で required/recommended/clean が返る
14. `失敗条件`
   - exit code contract が崩れる
15. `停止条件`
   - skip policy が定まらない
16. `差し戻し条件`
   - canonical docs 全面更新を混ぜる
17. `人判断へ上げる条件`
   - skip semantics に owner 判断が必要
18. `証拠`
   - CLI smoke output
19. `結果の記録先`
   - execution report
20. `最終判定者`
   - owner
