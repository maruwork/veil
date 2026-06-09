# Capture Report Lightening Execution Report

## Summary

- `veil-capture` の完了報告 contract を軽量化した
- 採用行は `- [level] term → 候補1` を基本形にした
- 候補2 / 候補3 は必要時だけ `補助候補` として残す形にした
- `保留:` は必要時だけ、`同期:` は 1 行、`返答前検査:` は固定短文にそろえた
- skills、README、design、current companion を current contract に追従させた

## Surface Changes

### Skills

- [codex skill](/C:/Users/f_tan/project/veil/skills/codex/veil-capture/SKILL.md:283)
- [claude skill](/C:/Users/f_tan/project/veil/skills/claude-code/veil-capture.md:278)

更新点:

- 採用語の基本形式を `- [level] term → 候補1` に変更
- 補助候補は `| 補助候補: ...` の時だけ表示
- `保留:` は必要時だけ
- `同期:` は 1 行

### Docs

- [README.md](/C:/Users/f_tan/project/veil/README.md:189) の出力例を軽量版に更新
- [docs/veil-design.md](/C:/Users/f_tan/project/veil/docs/veil-design.md:297) の report 契約を軽量版に更新
- [index/project-current-work.md](/C:/Users/f_tan/project/veil/index/project-current-work.md:31) を wave 3 進行中に更新

## Verification

- skill surface readback:
  - `採用語は - [level] term → 候補1`
  - `補助候補`
  - `保留語がある場合だけ`
  - `同期結果を 1 行`
- docs/current readback:
  - README example
  - design report contract
  - current companion next action

## Residual

- wave 3 は closed
- 次の自然な tuning wave は
  - normalize の追加保守 tuning
  - capture report ではなく capture candidate selection 側の絞り込み強化
