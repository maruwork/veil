# Capture Candidate Selection Execution Report

## Summary

- `veil-normalize.py` に candidate selection narrowing を追加した
- 各 result item に `selection_hint` と `selection_reason` を追加した
- 区分は `先に採る候補 / 保留寄り / 外す寄り` の 3 つ
- skills、README、design、current companion を selection hint 前提に追従させた

## Runtime Change

### `veil-normalize.py`

- `suggest_selection_hint(...)` を追加
- existing-match / new-candidate の両方へ `selection_hint`, `selection_reason` を追加
- text 出力に `選別目安`, `選別理由` を追加

## Verification

### Syntax

```text
python -m py_compile veil-normalize.py
```

- result: PASS

### Mixed Candidate Readback

`close / summary / current state / GitHub / normalization / status=close / verification` の readback で:

- `close`, `summary`
  - `selection_hint = 先に採る候補`
- `current state`
  - `selection_hint = 先に採る候補`
  - reason: `既存統合先があり、まずそれに寄せればよい`
- `normalization`, `verification`
  - `selection_hint = 保留寄り`
- `GitHub`, `status=close`
  - `selection_hint = 外す寄り`

### CLI JSON Smoke

```text
python veil-normalize.py --text "verification\nsummary\nsummary\nGitHub\nstatus=close" --json
```

- result:
  - `summary` -> `先に採る候補`
  - `verification` -> `保留寄り`
  - `GitHub`, `status=close` -> `外す寄り`

## Residual

- wave 4 は closed
- 次の自然な tuning wave は
  - `close` のような一般動詞をさらに保守的に扱う追加 tuning
  - capture skill の抽出基準そのものを少し締める wave
