# Lint Fix Guidance Task Design

## 1. Parent Theme

- VEIL tuning wave 1

## 2. Task Designs

### Task ID: LG-1

1. `Task ID`
   - `LG-1`
2. `親テーマ`
   - VEIL tuning wave 1
3. `親チェックポイント`
   - lint runtime guidance fixed
4. `目的`
   - `veil-lint.py` に fix guidance を実装する
5. `このタスクが必要な理由`
   - gate を通した後の修正コストを下げるため
6. `着手条件`
   - canonical migration close
7. `入力`
   - current `veil-lint.py`
8. `読んでよい場所`
   - `veil-lint.py`
9. `書いてよい場所`
   - `veil-lint.py`
10. `触ってはいけない場所`
   - unrelated runtime
11. `やること`
   - item/hit guidance と preview を追加する
12. `期待する出力`
   - text/json guidance
13. `合格条件`
   - violation と warning で修正先が明示される
14. `失敗条件`
   - exit code 契約が崩れる
15. `停止条件`
   - guidance が自動修正契約に広がる
16. `差し戻し条件`
   - normalize 再設計が必要になる
17. `人判断へ上げる条件`
   - preview 契約を owner が変えたい場合
18. `証拠`
   - smoke output
19. `結果の記録先`
   - execution report
20. `最終判定者`
   - owner

### Task ID: LG-2

1. `Task ID`
   - `LG-2`
2. `親テーマ`
   - VEIL tuning wave 1
3. `親チェックポイント`
   - docs/current aligned
4. `目的`
   - docs/current を lint guidance contract に追従させる
5. `このタスクが必要な理由`
   - mainline surface を current runtime に合わせるため
6. `着手条件`
   - LG-1 完了
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
   - lint output wording と current bundle を更新する
12. `期待する出力`
   - consistent docs/current
13. `合格条件`
   - fix guidance が current docs に載る
14. `失敗条件`
   - old output wording が残る
15. `停止条件`
   - docs が runtime より先走る
16. `差し戻し条件`
   - runtime と docs が不一致
17. `人判断へ上げる条件`
   - owner が next bundle scope を変えたい場合
18. `証拠`
   - readback
19. `結果の記録先`
   - execution report
20. `最終判定者`
   - owner
