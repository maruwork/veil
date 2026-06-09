# Detailed Design

1. `veil-normalize.py` の `print_text_result` で non-low-priority `new-candidate` branch を対象にする
2. retention がある時だけ `選別/review` と `保留` をまとめて `選別/review/保留: ...` へ置き換える
3. retention がない時は `選別/review: ...` を維持する
4. `判別: ... | ...` は現行のまま残す
5. docs / skills / current companion を新ラベルへ追従させる
