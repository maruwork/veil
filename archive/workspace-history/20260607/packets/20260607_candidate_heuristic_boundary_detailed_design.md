# Detailed Design

## Current Writeback

- active bundle を heuristic boundary bundle へ切り替える
- success subject は `foundation と heuristic の境界固定`
- next action は `user confirmation なしに細則を増やさない`

## README Writeback

- `normalize` 説明段に、single-word / phrase の threshold は未承認 heuristic と明記する
- foundation として有効な部分はそのまま残す

## Design Writeback

- detailed behavior 節に、candidate threshold は provisional heuristic と明記する
- phase boundary 節にも user confirmation 前提を追記する

## Verification

- `rtk rg` で `未承認 heuristic`、`foundation`、`user confirmation` を readback
- `current work` で new bundle を確認
