# Capture Candidate Selection Task Design

## 1. Parent Theme

- VEIL tuning wave 4

## 2. Task Designs

### Task ID: CS-1

1. `Task ID`
   - `CS-1`
2. `親テーマ`
   - VEIL tuning wave 4
3. `親チェックポイント`
   - selection hint runtime fixed
4. `目的`
   - normalize result に選別目安を追加する
5. `このタスクが必要な理由`
   - capture で先に見る候補を絞るため
6. `着手条件`
   - wave 1-3 close
7. `入力`
   - current `veil-normalize.py`
8. `読んでよい場所`
   - `veil-normalize.py`
9. `書いてよい場所`
   - `veil-normalize.py`
10. `触ってはいけない場所`
   - unrelated runtime
11. `やること`
   - selection bucket/reason を追加する
12. `期待する出力`
   - selection hint in text/json
13. `合格条件`
   - 先に採る/保留寄り/外す寄り が見える
14. `失敗条件`
   - existing classification or level suggestion を壊す
15. `停止条件`
   - ranking algorithm redesign が必要になる
16. `差し戻し条件`
   - schema change が必要になる
17. `人判断へ上げる条件`
   - selection bucket policy を owner が変えたい場合
18. `証拠`
   - smoke output
19. `結果の記録先`
   - execution report
20. `最終判定者`
   - owner
