# Lint Fix Guidance Execution Report

## Summary

- `veil-lint.py` に fix guidance を追加した
- violation / warning の各 item に `suggested_preferred` と `suggested_action` を追加した
- hit 単位に `suggested_replacement`、`suggested_action`、`suggested_line_preview` を追加した
- text 出力は `直し方` と `置換例` を返すようになった
- `README.md`、`docs/veil-design.md`、`index/project-current-work.md` を current contract に追従させた

## Runtime Change

### `veil-lint.py`

- `build_suggested_action(...)` を追加
- `build_line_preview(...)` を追加
- item 単位の guidance field を追加
- hit 単位の replacement / preview field を追加
- text output に `直し方` と `置換例` を追加

## Verification

### Syntax

```text
python -m py_compile veil-lint.py
```

- result: PASS

### Text Smoke

```text
python veil-lint.py --text "current state を整理した" --db workspace/veil_stage1_smoke.db
```

- result:
  - `NG: required 1 rule(s), 1 hit(s); recommended 0 rule(s), 0 hit(s) from db:workspace/veil_stage1_smoke.db`
  - `直し方: current state を 今の状態 へ直す`
  - `置換例: 今の状態 を整理した`

```text
python veil-lint.py --text "summary を更新した" --db workspace/veil_stage1_smoke.db
```

- result:
  - `WARN: recommended 1 rule(s), 1 hit(s) from db:workspace/veil_stage1_smoke.db`
  - `直し方: summary を 要約 へ直す`
  - `置換例: 要約 を更新した`

### JSON Smoke

```text
python veil-lint.py --text "current state を整理した" --db workspace/veil_stage1_smoke.db --json
```

- result:
  - top-level `status=violation`
  - item-level `suggested_preferred`, `suggested_action`
  - hit-level `suggested_replacement`, `suggested_action`, `suggested_line_preview`

## Residual

- lint guidance wave 1 は閉じた
- 次の自然な tuning wave は `normalize` 判別精度か、`capture report` の軽量化
