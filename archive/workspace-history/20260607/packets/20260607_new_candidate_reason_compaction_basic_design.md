# Basic Design

## Intent

headline compact の後でも detail branch はまだ縦に長い。理由を対になる 2 行のまま並べるのではなく、一行要約へ寄せて走査を速くする。

## Chosen Shape

- `選別: 先に採る候補 | 説明語候補で頻度もあり、先に採用候補として見やすい`
- `review: 短い review に残す | 今回の確認候補として短い一覧に残してよい`
- `判別: 説明語候補 | 同じ小文字単語が複数回現れ、一般語として使われている可能性が高い`

## Non-Goals

- 理由情報の削除
- `保留処理` の削除
- JSON 側への compact 表現追加

