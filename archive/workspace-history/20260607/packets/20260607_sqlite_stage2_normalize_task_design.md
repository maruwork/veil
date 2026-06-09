# SQLite Stage 2 Normalize Task Design

## 1. Parent Theme

- SQLite canonical migration Stage 2 normalize wave

## 2. Task Designs

### Task ID: S2N-A

1. `Task ID`
   - `S2N-A`
2. `親テーマ`
   - SQLite canonical migration Stage 2 normalize wave
3. `親チェックポイント`
   - normalize wave packet fixed
4. `目的`
   - normalize wave の scope と contract を packet に固定する
5. `このタスクが必要な理由`
   - existing-match drift を防ぐため
6. `着手条件`
   - audit wave completed
7. `入力`
   - audit wave report
   - current normalize code
8. `読んでよい場所`
   - audit wave packet/report
   - `veil-normalize.py`
   - `veil_rule_store.py`
9. `書いてよい場所`
   - normalize wave packet files
10. `触ってはいけない場所`
   - `veil-lint.py`
11. `やること`
   - source selection / contract / smoke items を定義する
12. `期待する出力`
   - normalize wave packet
13. `合格条件`
   - existing-match contract preservation が packet で読める
14. `失敗条件`
   - scope に lint switch が混ざる
15. `停止条件`
   - contract が hidden のまま
16. `差し戻し条件`
   - source selection が曖昧
17. `人判断へ上げる条件`
   - owner が contract change を望む場合
18. `証拠`
   - normalize wave packet
19. `結果の記録先`
   - `workspace/20260607_sqlite_stage2_normalize_*.md`
20. `最終判定者`
   - owner

### Task ID: S2N-B

1. `Task ID`
   - `S2N-B`
2. `親テーマ`
   - SQLite canonical migration Stage 2 normalize wave
3. `親チェックポイント`
   - normalize SQLite read added
4. `目的`
   - `veil-normalize.py` に SQLite source route を加える
5. `このタスクが必要な理由`
   - Stage 2 次波の実装対象だから
6. `着手条件`
   - normalize wave packet fixed
7. `入力`
   - `veil-normalize.py`
   - `veil_rule_store.py`
8. `読んでよい場所`
   - normalize wave packet
   - Stage 1 helper
9. `書いてよい場所`
   - `veil-rule_store.py`
   - `veil-normalize.py`
10. `触ってはいけない場所`
   - `veil-lint.py`
11. `やること`
   - db index helper
   - `--db` option
   - source label
   - existing-match parity
12. `期待する出力`
   - dual-source normalize CLI
13. `合格条件`
   - db / rules-dir 両方で `current state` が existing-match になる
14. `失敗条件`
   - existing-match key が欠ける
15. `停止条件`
   - helper 契約が lint wave まで広がる
16. `差し戻し条件`
   - lint switch を混ぜる
17. `人判断へ上げる条件`
   - contract change が必要
18. `証拠`
   - CLI smoke output
19. `結果の記録先`
   - execution report
20. `最終判定者`
   - owner
