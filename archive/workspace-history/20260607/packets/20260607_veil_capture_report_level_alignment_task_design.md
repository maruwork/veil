# VEIL Capture Report Level Alignment Task Design

## 1. Parent Theme

- workstream: VEIL capture report level alignment

## 2. Task Designs

### Task ID: T-A

- 親テーマ:
  - VEIL capture report level alignment
- 親チェックポイント:
  - level-aware report in skills
- 目的:
  - skill の完了報告を level-aware にする
- このタスクが必要な理由:
  - close 時に hard gate へ上げた語が見えないため
- 着手条件:
  - parent packet 読了
- 入力:
  - current skill report section
- 読んでよい場所:
  - 2 つの skill
- 書いてよい場所:
  - 2 つの skill
- 触ってはいけない場所:
  - runtime scripts
- やること:
  - `採用:` `保留:` `同期:` `返答前検査:` の report 形式へ更新する
- 期待する出力:
  - level-aware close report
- 合格条件:
  - 採用語に level が付いている
- 失敗条件:
  - 候補列挙だけで level が見えない
- 停止条件:
  - report が冗長化しすぎる
- 差し戻し条件:
  - docs 例と意味がずれる
- 人判断へ上げる条件:
  - 候補2 / 候補3 の既定表示を維持するか迷う場合
- 証拠:
  - skill diff
- 結果の記録先:
  - updated skills
- 最終判定者:
  - project operator

### Task ID: T-B

- 親テーマ:
  - VEIL capture report level alignment
- 親チェックポイント:
  - README follow-through
- 目的:
  - README の出力例を level-aware にする
- このタスクが必要な理由:
  - public entry でも report 形式が一致している必要がある
- 着手条件:
  - T-A 完了
- 入力:
  - updated skill report
- 読んでよい場所:
  - `README.md`
- 書いてよい場所:
  - `README.md`
- 触ってはいけない場所:
  - runtime scripts
- やること:
  - 出力例と説明を level-aware に更新する
- 期待する出力:
  - level-aware README example
- 合格条件:
  - README だけ見ても report が理解できる
- 失敗条件:
  - README が旧例のまま
- 停止条件:
  - README が説明過多になる
- 差し戻し条件:
  - skill 例と一致しない
- 人判断へ上げる条件:
  - 候補2 / 候補3 を README 例に残すか迷う場合
- 証拠:
  - doc diff
- 結果の記録先:
  - updated README
- 最終判定者:
  - project operator
