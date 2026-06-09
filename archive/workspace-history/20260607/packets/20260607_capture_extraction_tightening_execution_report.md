# Capture Extraction Tightening Execution Report

## Summary

- `veil-capture` の候補抽出基準を tightening した
- `2回以上` に加えて、`状態語 / 判断語 / 構造語 / 運用ラベル` を優先する契約に更新した
- 一般動詞単体は原則として候補へ送らない方針を明記した
- 一般動詞を扱うのは、複合語で意味が固まる場合か、同じ運用文脈で繰り返し出る場合だけに絞った
- skills、README、design、current companion を current contract に追従させた

## Surface Changes

### Skills

- [codex skill](/C:/Users/f_tan/project/veil/skills/codex/veil-capture/SKILL.md:45)
- [claude skill](/C:/Users/f_tan/project/veil/skills/claude-code/veil-capture.md:40)

更新点:

- `2回以上出るだけでなく、状態語、判断語、構造語、運用ラベルを優先する`
- `一般動詞単体は原則として候補に送らない`
- `一般動詞単体が機械的に混入していない`

### Docs

- [README.md](/C:/Users/f_tan/project/veil/README.md:24) の flow に抽出 tightening を追加
- [docs/veil-design.md](/C:/Users/f_tan/project/veil/docs/veil-design.md:46) の capture flow に抽出 tightening を追加
- [index/project-current-work.md](/C:/Users/f_tan/project/veil/index/project-current-work.md:31) を wave 5 進行中に更新

## Verification

- skill/docs/current readback:
  - `一般動詞単体は原則として候補に送らない`
  - `状態語、判断語、構造語、運用ラベルを優先する`
  - `一般動詞単体が機械的に混入していない`

## Residual

- wave 5 は closed
- 次の自然な tuning wave は
  - 一般動詞の追加保守 tuning
  - capture 後の保留候補の扱いをもう少し軽くする wave
