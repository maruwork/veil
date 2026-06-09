# SQLite Stage 3 Capture Sync Execution Report

## Summary

- Stage 3 の目的だった `capture/sync` の write-generate route を SQLite canonical 前提へ切り替えた
- `veil-db.py` に `upsert-rule` と `export-mirror` を追加した
- `veil-sync.py` は DB-first で markdown mirror を再生成してから同期する route へ切り替えた
- `README.md`、`docs/veil-design.md`、2 つの `veil-capture` skill、`AGENTS.md`、`index/project-current-work.md` を current route に追従させた

## Runtime Changes

### `veil_rule_store.py`

- `upsert_rule(...)` を追加
- `choose_mirror_filename(...)` を追加
- `render_markdown_mirror_from_rows(...)` を追加
- `export_markdown_mirror_from_db(...)` を追加

### `veil-db.py`

- `upsert-rule` subcommand を追加
- `export-mirror` subcommand を追加

### `veil-sync.py`

- `--config-dir`, `--db`, `--rules-dir`, `--quiet` を追加
- DB canonical が存在する current phase では mirror を再生成してから sync する route を追加
- DB がない場合だけ rules-dir fallback を維持

## Verification

### Syntax

```text
python -m py_compile veil_rule_store.py veil-db.py veil-sync.py workspace/veil_stage3_capture_sync_smoke.py
```

- result: PASS

### Smoke

```text
python workspace/veil_stage3_capture_sync_smoke.py
```

- result:
  - `STAGE3-SMOKE: total=2, required=1, recommended=1, observe=0, mirror_files=2`
  - `MIRROR: c.md, s.md`
  - `SYNC-TARGET: C:\Users\f_tan\project\veil\workspace\veil_stage3_smoke\TARGET.md`

### Surface Readback

- mainline surface で `capture` が SQLite canonical 記録 -> mirror 生成 -> sync の流れに更新されていることを確認した
- `upsert-rule` と `export-mirror` の文言が README / design / skills に入っていることを確認した

## Residual

- canonical migration の mainline 実装はここで閉じた
- 次の自然な bundle は `precision / usability tuning`
