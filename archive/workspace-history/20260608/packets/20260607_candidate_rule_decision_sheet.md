# Candidate Rule Decision Sheet

## Purpose

未承認 heuristic をこれ以上積み増さず、VEIL の候補化ルールで user 判断が必要な点だけを短く固定する。

## Confirmed Foundation

- `capture -> normalize -> sync -> lint` の mainline は維持する
- `normalize` は保留処理、判別補助、level 提案、review-first text 出力を返せる
- `SQLite` canonical と mirror generation の土台は current 有効成果として残す

## Open Decisions

### D-1 `2回出現` の位置づけ

- question:
  - `2回出現` は広い目安に留めるのか、高影響語以外の default gate にするのか
- current heuristic:
  - `2回以上` を強めの条件として扱っている
- impact:
  - 強い gate にすると review 負荷は減る
  - 目安にすると高影響語例外を扱いやすい

### D-2 single-word 一般語の扱い

- question:
  - single-word の一般語は通常 `保留 / 観察` へ逃がすのか、extract で大きく切るのか
- current heuristic:
  - 強い採用候補へは上げず、保守側に残す
- impact:
  - extract で切るなら review 負荷は下がる
  - 保留へ流すなら取り逃がしは減る

### D-3 lowercase phrase の扱い

- question:
  - lowercase phrase を高影響語以外でどこまで review に残すか
- current heuristic:
  - 用途が広い phrase は保守側へ倒している
- impact:
  - ここを厳しくすると extract ノイズは減る
  - 緩めると project 固有 phrase を早く拾える

### D-4 厳しく落とす場所

- question:
  - 候補を厳しく落とす主戦場を `capture` に置くのか、`normalize` に置くのか
- current heuristic:
  - 現在は `normalize` 側に heuristic が多い
- impact:
  - `capture` で切るなら review 負荷は減る
  - `normalize` で切るなら extract は広く取れる

## Immediate Next Step

- 上の 4 点を user 判断で固定する
- 固定後にだけ `capture` / `normalize` の細則を正本ルールへ昇格させる
