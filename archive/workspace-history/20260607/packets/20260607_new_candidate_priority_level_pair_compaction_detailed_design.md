# Detailed Design

1. `veil-normalize.py` の `print_text_result` で non-low-priority `new-candidate` branch を対象にする
2. `priority: ...` と `level: ... | ...` の 2 行を削除する
3. `priority/level: <priority> | <level> | <reason>` の 1 行へ置き換える
4. low-priority compact branch の `level 提案` はそのまま維持する
5. docs / skills / current companion を新ラベルへ追従させる
