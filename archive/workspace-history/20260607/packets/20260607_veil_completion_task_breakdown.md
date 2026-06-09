# Task Breakdown

## Path

- `CP-1` completion packet fixed
- `CP-2` current completion bundle switch
- `CP-3` completion path writeback to authority surfaces
- `CP-4` verification and execution record

## Tasks

### T-A Completion Packet

- purpose:
  - completion definition と blocker を固定する
- write:
  - completion packet 6 本

### T-B Current Switch

- purpose:
  - active bundle を completion-oriented bundle へ切り替える
- write:
  - `index/project-current-work.md`

### T-C Authority Writeback

- purpose:
  - `README.md` と `docs/veil-design.md` に completion path を反映する

### T-D Verify and Record

- purpose:
  - completion path の一致を証拠化する

## Stop Condition

- owner decision なしに candidate rule を確定しようとした時は停止する
- heuristic を追加実装する方向へ逸れた時は停止する
