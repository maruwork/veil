# Detailed Design

1. `veil-normalize.py` の `existing_items` rendering を対象にする
2. 各 item について `variant_counts` から sole variant 条件を判定する
3. 条件一致時は item 行の `| 表記ゆれ: ...` を省く
4. 1 件 source は `| source: <file>` だけ残す
5. 複数件 source grouping は現行のまま維持する
6. docs / skills / current companion を新契約へ追従させる
