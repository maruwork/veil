# Basic Design

## Problem

VEIL は土台実装が進んでいる一方で、candidate rule の本決めが未了のため、completed と言える条件が曖昧になっている。

## Direction

- 「何を実装するか」より先に「何が揃えば completed か」を固定する
- completion path を `implementation` と `owner decision` の混合工程として扱う
- 未承認 heuristic は completion blocker として明記し、曖昧なまま completed 扱いしない

## Completion Phases

### Phase 1 Foundation Freeze

- SQLite canonical
- mainline route
- rule level contract
- retention / review support

### Phase 2 Candidate Rule Decision

- `2回出現` の位置づけ
- single-word 一般語の扱い
- lowercase phrase の扱い
- `capture` と `normalize` の responsibility split

### Phase 3 Rule-Driven Runtime Alignment

- Phase 2 で確定した rule を `capture` / `normalize` / docs / skills に反映する

### Phase 4 End-to-End Verification

- representative capture -> normalize -> sync -> lint flow を strong evidence で確認する

### Phase 5 Completion Close

- blocker none
- current / README / design / execution evidence が一致

## Principle

- Phase 2 を飛ばして completed へ進まない
- heuristic を増やすことを前進とみなさない
- owner decision を待つ間は、decision surface と verification route の整備だけを前進とみなす
