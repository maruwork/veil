# Current Default Profile Audit Execution Basic Design

## 1. Flow

1. `veil-profile-audit.py` を real `~/.veil/rules/` に対して実行する
2. text / json を読む
3. summary と注目 file を抽出する
4. workspace artifact に固定する

## 2. Evidence

- audit text summary
- audit json payload
- residual issues list

## 3. Output

- current profile audit report
- next cleanup wave candidate list
