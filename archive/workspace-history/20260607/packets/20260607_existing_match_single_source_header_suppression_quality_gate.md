# Quality Gate

- `rtk python -B -m py_compile veil-normalize.py`
- text smoke で 1 件 source の existing-match は `source: ...` header を持たず、行末 `| source: <file>` になる
- text smoke で複数件 source は現行 header grouping を維持する
- new-candidate branch unchanged
- JSON unchanged
- `rtk rg` で README / design / skills / current の契約が揃う
