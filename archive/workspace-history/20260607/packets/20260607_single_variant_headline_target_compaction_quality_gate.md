# Quality Gate

- `rtk python -m py_compile veil-normalize.py`
- text smoke で single-variant の冗長ケースは headline に `| <target>` が付き、`variants/target` 行が消える
- text smoke で multi-variant は `variants/target` 行を維持する
- text smoke で low-priority branch unchanged
- JSON smoke で key contract unchanged
- `rtk rg` で README / design / skills / current の契約が揃う
