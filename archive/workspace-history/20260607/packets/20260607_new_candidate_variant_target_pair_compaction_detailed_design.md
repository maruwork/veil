# Detailed Design

1. `veil-normalize.py` の `print_text_result` で non-low-priority `new-candidate` branch を対象にする
2. `variants` 文字列の組み立ては現行ロジックを流用する
3. `variants: ...` と `target: ...` の 2 行を削除し、`variants/target: ... | ...` の 1 行へ置き換える
4. low-priority compact branch の `target: ...` はそのまま維持する
5. docs / skills / current companion を新ラベルへ追従させる
