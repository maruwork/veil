# Basic Design

## Intent

review-first 出力では `new-candidate` の詳細 block が長い。まず headline だけで優先候補の把握を速くし、その下で必要な理由を見る形へ寄せる。

## Chosen Shape

- headline:
  - `- [new-candidate] summary [推奨] x2`
- detail:
  - 既存の詳細行を継続

## Non-Goals

- detail 行の全面削除
- low-priority compact branch の統合
- JSON headline 追加

