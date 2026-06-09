# Normalize Single Word Precision Task Design

## 1. Parent Theme

- VEIL tuning wave 2

## 2. Task Designs

### Task ID: NP-1

1. `Task ID`
   - `NP-1`
2. `親テーマ`
   - VEIL tuning wave 2
3. `親チェックポイント`
   - normalize heuristic fixed
4. `目的`
   - single-word lowercase 判定を改善する
5. `このタスクが必要な理由`
   - 候補精度を上げつつ過剰統制を避けるため
6. `着手条件`
   - tuning wave 1 close
7. `入力`
   - current `veil-normalize.py`
8. `読んでよい場所`
   - `veil-normalize.py`
9. `書いてよい場所`
   - `veil-normalize.py`
10. `触ってはいけない場所`
   - unrelated runtime
11. `やること`
   - occurrence_count と noun-like suffix を見る heuristic を追加する
12. `期待する出力`
   - improved `classification_hint`
13. `合格条件`
   - single-word 一般語が一部 `説明語候補` へ寄る
14. `失敗条件`
   - 識別子や固有名の保守性が崩れる
15. `停止条件`
   - broad dictionary rule が必要になる
16. `差し戻し条件`
   - runtime contract を変える必要が出る
17. `人判断へ上げる条件`
   - heuristic 範囲を owner が変えたい場合
18. `証拠`
   - smoke output
19. `結果の記録先`
   - execution report
20. `最終判定者`
   - owner

### Task ID: NP-2

1. `Task ID`
   - `NP-2`
2. `親テーマ`
   - VEIL tuning wave 2
3. `親チェックポイント`
   - docs/current aligned
4. `目的`
   - docs/current を normalize precision wave に追従させる
5. `このタスクが必要な理由`
   - runtime と current companion を揃えるため
6. `着手条件`
   - NP-1 完了
7. `入力`
   - updated runtime
8. `読んでよい場所`
   - `README.md`
   - `docs/veil-design.md`
   - `index/project-current-work.md`
9. `書いてよい場所`
   - same docs
10. `触ってはいけない場所`
   - UI
11. `やること`
   - normalize hint wording と current position を更新する
12. `期待する出力`
   - consistent docs/current
13. `合格条件`
   - wave 2 wording が current surface に反映される
14. `失敗条件`
   - old next action が残る
15. `停止条件`
   - docs が runtime より先走る
16. `差し戻し条件`
   - runtime と docs の不一致
17. `人判断へ上げる条件`
   - owner が next wave を変えたい場合
18. `証拠`
   - readback
19. `結果の記録先`
   - execution report
20. `最終判定者`
   - owner
