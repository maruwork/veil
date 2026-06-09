# VEIL Capture Rule Section Alignment Task Design

## 1. Parent Theme

- workstream: VEIL capture rule section alignment

## 2. Task Designs

### Task ID: T-A

- 親テーマ:
  - VEIL capture rule section alignment
- 親チェックポイント:
  - write target includes section
- 目的:
  - skill task 7 を file + section 決定へ更新する
- このタスクが必要な理由:
  - current skill が level-aware write を説明できていない
- 着手条件:
  - parent packet 読了
- 入力:
  - current skills
- 読んでよい場所:
  - 2 つの skill
  - parent packet
- 書いてよい場所:
  - 2 つの skill
- 触ってはいけない場所:
  - runtime scripts
- やること:
  - level 提案を見て section を決める流れを追加する
- 期待する出力:
  - section-aware target selection
- 合格条件:
  - task 7 で file と section の両方が決まる
- 失敗条件:
  - file 決定だけで終わる
- 停止条件:
  - skill と runtime semantics が衝突する
- 差し戻し条件:
  - section 名が packet とずれる
- 人判断へ上げる条件:
  - level 提案を無視する条件を追加裁定したい場合
- 証拠:
  - skill diff
- 結果の記録先:
  - updated skill
- 最終判定者:
  - project operator

### Task ID: T-B

- 親テーマ:
  - VEIL capture rule section alignment
- 親チェックポイント:
  - section-aware write
- 目的:
  - skill task 8 を section-aware 書き込みへ更新する
- このタスクが必要な理由:
  - current task 8 が flat line 前提だから
- 着手条件:
  - T-A 完了
- 入力:
  - updated skills
- 読んでよい場所:
  - 2 つの skill
- 書いてよい場所:
  - 2 つの skill
- 触ってはいけない場所:
  - runtime scripts
- やること:
  - `# {letter}` と `## level` を扱う
  - section がなければ作る
  - heading のない既存 line は `必須` 扱いとする
- 期待する出力:
  - section-aware write procedure
- 合格条件:
  - task 8 で section 作成・追記・整列が読める
- 失敗条件:
  - `- {term} → {訳語}` のみで終わる
- 停止条件:
  - existing flat file の扱いが決め切れない
- 差し戻し条件:
  - backward compatibility 記述が docs と衝突する
- 人判断へ上げる条件:
  - flat file をどう整理するか複数案で割れる場合
- 証拠:
  - skill diff
- 結果の記録先:
  - updated skill
- 最終判定者:
  - project operator

### Task ID: T-C

- 親テーマ:
  - VEIL capture rule section alignment
- 親チェックポイント:
  - docs follow-through
- 目的:
  - README / design に必要最小限の補足を入れる
- このタスクが必要な理由:
  - skill だけ更新すると canonical explanation が追従しない
- 着手条件:
  - T-A, T-B 完了
- 入力:
  - updated skill
- 読んでよい場所:
  - `README.md`
  - `docs/veil-design.md`
- 書いてよい場所:
  - `README.md`
  - `docs/veil-design.md`
- 触ってはいけない場所:
  - runtime scripts
- やること:
  - section-aware write の最小補足
- 期待する出力:
  - docs / skill consistency
- 合格条件:
  - surface 間で flat write 前提が残らない
- 失敗条件:
  - docs が旧 write flow のまま
- 停止条件:
  - docs が冗長に膨らむ
- 差し戻し条件:
  - skill wording と docs wording がずれる
- 人判断へ上げる条件:
  - docs にどこまで詳細を書くか迷う場合
- 証拠:
  - diff and rg
- 結果の記録先:
  - updated docs
- 最終判定者:
  - project operator
