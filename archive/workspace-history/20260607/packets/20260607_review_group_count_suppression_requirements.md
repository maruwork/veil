# review group count suppression requirements

## Goal

`veil-normalize.py` の text 出力にある review group header から件数表示を外し、review group も source header と同様に行数で読む契約へそろえる。

## Scope

- `veil-normalize.py` の `短い review に残す (N件):` / `短い review から外す寄り (N件):` を件数なし header へ変更する
- `README.md`
- `docs/veil-design.md`
- `skills/codex/veil-capture/SKILL.md`
- `skills/claude-code/veil-capture.md`
- `index/project-current-work.md`
- execution report

## Out Of Scope

- normalize/capture の意味判定ロジック変更
- JSON 契約変更
- existing-match / source header の再設計
- lint / sync / db schema の変更

## Acceptance

- text 出力で review group header から件数が消える
- docs / skills / current companion が「件数は行数で読む」契約にそろう
- `rtk python -B -m py_compile veil-normalize.py` が通る
- text smoke と JSON smoke が通る
