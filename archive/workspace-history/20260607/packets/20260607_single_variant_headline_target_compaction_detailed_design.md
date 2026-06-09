# Detailed Design

1. `veil-normalize.py` の `print_text_result` で non-low-priority `new-candidate` branch を対象にする
2. `variant_counts` から single-variant かどうかを判定する
3. sole variant を正規化した値が `normalized` と一致し、count も headline の `occurrence_count` と一致する時だけ compact を適用する
4. compact 時は headline の末尾へ `| <target_file>` を追加し、`variants/target` 行は出さない
5. それ以外は現行の `variants/target: ... | ...` を維持する
6. docs / skills / current companion を新契約へ追従させる
