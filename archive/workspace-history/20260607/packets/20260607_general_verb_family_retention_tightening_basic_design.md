# Basic Design

## Strategy

- `suggest_retention_hint()` で single-word general verb family を優先的に `今は見送る` へ倒す
- `priority_hint` や JSON schema は変えない
- shortlist 移動は既存の `retention_hint == 今は見送る` ルールを使う

## Out Of Scope

- 新しい level 種別追加
- `capture` skill 全体の再設計
- `existing-match` 出力変更
