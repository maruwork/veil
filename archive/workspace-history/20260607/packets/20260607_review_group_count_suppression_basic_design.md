# review group count suppression basic design

## Intent

review group header の冗長な件数表示を消し、出力をさらに軽くする。件数は source header と同じく明示せず、行数から把握する。

## Design

1. `print_text_result()` の group header 出力を `短い review に残す:` / `短い review から外す寄り:` に変更する
2. group 内 item 並び順や item 本体は変えない
3. JSON 出力は変更しない
4. docs / skills は group header でも件数を見ず行数で把握する契約へ更新する

## Invariants

- `new-candidate` を先、`existing-match` を後に並べる
- low-priority compact / existing-match compact 契約はそのまま維持する
- group 名自体は変えない
