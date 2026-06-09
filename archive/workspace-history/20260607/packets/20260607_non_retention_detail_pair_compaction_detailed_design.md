# Detailed Design

1. `veil-normalize.py` の `print_text_result` で non-low-priority `new-candidate` branch を対象にする
2. `retention_hint` がない時だけ `選別/review` と `判別/priority/level` をまとめる
3. 新表示は `選別/review/判別/priority/level: ...` の 1 行にする
4. `retention_hint` がある時は現行の 2 行構成を維持する
5. docs / skills / current companion を新契約へ追従させる
