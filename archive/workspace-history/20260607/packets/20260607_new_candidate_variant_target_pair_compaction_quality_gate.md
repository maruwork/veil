# Quality Gate

- `rtk python -m py_compile veil-normalize.py`
- text smoke で non-low-priority `new-candidate` が `variants/target: ... | ...` になる
- text smoke で low-priority branch unchanged
- JSON smoke で key contract unchanged
- `rtk rg` で README / design / skills / current の契約が揃う
