# Workspace Shelf Cleanup Basic Design

## Principle

- `current` は daily bundle と current authority に必要な最小面だけ残す
- `generated` は `workspace/` に残すが、active に使うものと support artifact に絞る
- `historical` は `archive/` へ退避する
- 整理は非破壊 move を使う

## Keep In Workspace

- active bundle packet
- open decision sheet
- smoke fixture / smoke db / profile export / reference

## Move To Archive

- close 済み wave packet
- close 済み execution report
- stray UI check artifact
- root に溜まった obsolete dated markdown

## Archive Shape

- `archive/workspace-history/20260607/`
  - `packets/`
  - `artifacts/`

## Authority Update

- `project-current-work.md` は整理 bundle へ切替
- taxonomy / boundary は `archive/` を実体化した shelf として扱う
