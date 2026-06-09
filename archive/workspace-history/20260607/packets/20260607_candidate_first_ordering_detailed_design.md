# Detailed Design

## 1. Rendering Contract

各 group の items は次の順で出す。

1. `new-candidate`
2. `existing-match`

## 2. Verification Conditions

- `短い review に残す` group で new-candidate があれば existing-match より前
- existing-match compact branch は維持
- JSON output unchanged
