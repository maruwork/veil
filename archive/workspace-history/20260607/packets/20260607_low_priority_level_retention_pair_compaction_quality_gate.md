# Quality Gate

- `rtk python -B -m py_compile veil-normalize.py`
- text smoke で low-priority branch が `level/保留処理: ... | ...` になる
- text smoke で `target: ...` 独立行が維持される
- non-low-priority branch unchanged
- JSON unchanged
- `rtk rg` で README / design / skills / current の契約が揃う
