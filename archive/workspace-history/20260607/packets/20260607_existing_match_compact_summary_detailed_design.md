# Detailed Design

## Rendering Contract

- source header grouping は維持
- `existing-match` の各 item は複数行ではなく一行 compact

## Compact Shape

- `source: <file> (<count>件)`
- `- normalized -> preferred [level] | 表記ゆれ: variant xN, ...`

## Verification Conditions

- same source の existing-match が header 下にまとまる
- one-line compact で `preferred` と `level` が読める
- new-candidate detail / compact branch unchanged
- JSON unchanged

