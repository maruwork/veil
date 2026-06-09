# Detailed Design

1. `veil-normalize.py` の `print_text_result` で `existing_items` の source grouping branch を対象にする
2. source ごとの item count が 1 件かどうかを判定する
3. 1 件 source の時は header を出さず、その item line 末尾へ `| source: <file>` を追加する
4. 複数件 source の時は現行 header と item line を維持する
5. docs / skills / current companion を新契約へ追従させる
