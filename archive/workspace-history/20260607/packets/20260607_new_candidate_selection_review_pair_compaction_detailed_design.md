# Detailed Design

1. `veil-normalize.py` の `print_text_result` で non-low-priority `new-candidate` branch を対象にする
2. `選別: ... | ...` と `review: ... | ...` の 2 行を削除する
3. `選別/review: <selection hint> | <selection reason> | <review hint>` の 1 行へ置き換える
4. `判別: ... | ...` は現行のまま残す
5. docs / skills / current companion を新ラベルへ追従させる
