# Detailed Design

1. `veil-normalize.py` の `print_text_result` で non-low-priority `new-candidate` branch を対象にする
2. `判別: ... | ...` と `priority/level: ... | ... | ...` の 2 行を削除する
3. `判別/priority/level: <classification hint> | <classification reason> | <priority> | <level>` の 1 行へ置き換える
4. `variants/target: ... | ...` は現行のまま残す
5. docs / skills / current companion を新ラベルへ追従させる
