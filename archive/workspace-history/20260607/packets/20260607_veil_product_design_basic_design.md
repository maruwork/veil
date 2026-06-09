# Basic Design

## Product Position

VEIL は `AI-assisted technical writing` 向けの terminology guardrail である。

- 主目的:
  - AI が会話や作業の中で使う語彙を、事前ルールで安定化させる
- 成功条件:
  - 運用者が無理なく candidate を確認できる
  - AI が最終出力で高影響語を守れる
  - current canonical と AI-readable surface がずれない

## Product Shape

- canonical:
  - SQLite
- AI-readable surface:
  - markdown mirror
- mainline:
  - `capture -> normalize -> sync -> lint`
- hard control:
  - flow と高影響語
- soft control:
  - 低頻度語、曖昧語、自然文全体

## Core Design Decisions

1. 候補抽出は `capture` が担当する
2. 候補の保留・採用順・既存統合候補の整理は `normalize` が担当する
3. 語彙の write authority は SQLite canonical に一本化する
4. AI への即時適用は markdown mirror + sync で行う
5. final answer control は `lint` が担当する

## Candidate Rule Strategy

- `2回出現` は current default では `必要条件`
- ただし高影響語は owner override で 1 回でも採用可能
- single-word 一般語は `capture` で原則として review 候補へ送らない
- lowercase phrase は 1 回では送らない
- lowercase phrase は 2 回でも原則は `normalize` の保留 review に留める
- 高影響で用途がかなり狭まる phrase だけを例外として上げる

## Why This Split

- `capture` を緩くしすぎると review 負荷が上がる
- `capture` を厳しすぎると高影響語を取り逃がす
- そのため
  - extract noise の主抑制は `capture`
  - nuanced hold / merge / level suggestion は `normalize`
  に置く
