# Basic Design

## Strategy

- `existing-match` の grouped-source branch で source file 種類数を見て分岐する
- source file が 1 種類だけなら header を出さず、各 item 行末へ `| <file>` を足す
- source file が複数ある時だけ従来どおり file header を使う

## Out Of Scope

- JSON 契約変更
- `new-candidate` 出力変更
- `existing-match` variant compact 契約変更
