# Detailed Design

## 1. Rendering Contract

- group 内の existing-match は source file ごとにまとめる
- source ごとに `source: <file> (N件)` を出す
- その下に compact existing-match line を出す

## 2. Verification Conditions

- 同 source の existing-match が連続してまとまる
- new-candidate detail unchanged
- JSON unchanged
