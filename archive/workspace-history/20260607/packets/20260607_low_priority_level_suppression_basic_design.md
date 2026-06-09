# low-priority level suppression basic design

## Intent

low-priority branch は `観察 + 保留候補 + 今は見送る` に固定されるので、text 出力では level を省いても判定を失わない。必要なら JSON 側で level を参照する。

## Design

1. low-priority compact line を `normalized | target | retention_hint` に変える
2. `suggested_level` は JSON では維持する
3. docs / skills には low-priority は `normalized | target | 保留処理` で読むと記す

## Invariants

- low-priority 判定条件は変更しない
- low-priority 以外の branch は変更しない
- JSON 契約は変更しない
