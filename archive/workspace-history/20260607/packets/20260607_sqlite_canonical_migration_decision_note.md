# SQLite Canonical Migration Decision Note

## Decision

分野別 profile 分岐を次の主題にせず、VEIL の語彙正本を SQLite に移す方を優先する。

## Why

- 現状の問題は branch の不足ではなく、current tool の精度と使い勝手
- Markdown 正本では queue / review / usage analysis / lint support を伸ばしにくい
- SQLite 正本なら machine-readable canonical として筋がよい

## Superseded Direction

次の方向は current mainline の直近主題から外す。

- branch-first で domain profile を増やすこと
- Markdown 正本を長期維持すること

## New Priority

1. SQLite を canonical にする
2. Markdown は generated artifact に落とす
3. そのうえで query / queue / lint support を強くする
