# Basic Design

## Strategy

- lowercase phrase を一律に説明語候補へ上げるのをやめる
- occurrence_count >= 2 の phrase は従来どおり説明語候補に寄せる
- occurrence_count == 1 の phrase は、noun-like token がない限り `境界が曖昧な候補` に残す

## Out Of Scope

- single-word 判定の再変更
- JSON schema 変更
- existing-match 出力変更
