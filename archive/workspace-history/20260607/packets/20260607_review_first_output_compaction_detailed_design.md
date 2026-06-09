# Detailed Design

## 1. Rendering Contract

text 出力は次の順にする。

1. 参照ルール
2. `短い review に残す (N件)`
3. その group の item block
4. `短い review から外す寄り (N件)`
5. その group の item block

## 2. Item Contract

item block 自体の詳細は維持する。

## 3. Verification Conditions

- `summary`, `verification` が前段
- `close`, `closed`, `closing`, `updates`, `status=close` が後段
- JSON output は before/after で key contract unchanged
