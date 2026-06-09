# Basic Design

## Strategy

- single-word lowercase の自動昇格は保守的にする
- 名詞化 suffix があるものは現行どおり説明語候補に寄せる
- suffix がない repeated single-word は、2 回出現ではまだ曖昧語のままにする
- 3 回以上出現した時だけ、現行どおり説明語候補への自動昇格を許す

## Out Of Scope

- phrase 候補の再設計
- general verb family 以外の retention 契約変更
- JSON schema 変更
