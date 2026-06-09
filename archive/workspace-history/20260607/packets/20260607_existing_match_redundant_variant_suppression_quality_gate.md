# Quality Gate

- `rtk python -B -m py_compile veil-normalize.py`
- text smoke で redundant な `existing-match` は `表記ゆれ:` を持たない
- text smoke で multi-variant または count>1 は `表記ゆれ:` を維持する
- new-candidate branch unchanged
- JSON unchanged
- `rtk rg` で README / design / skills / current の契約が揃う
