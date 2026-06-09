# Basic Design

## Strategy

- `new-candidate` の multi-variant detail line だけを `variants:` へ短縮する
- headline / JSON / low-priority / existing-match には触らない
- surface は code と同じ文言にだけ追従させる

## Out Of Scope

- JSON 契約変更
- source grouping 再設計
- `review:` line の再設計
