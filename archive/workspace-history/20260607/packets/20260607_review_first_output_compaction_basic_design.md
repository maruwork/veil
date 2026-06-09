# Basic Design

## 1. Decision

- `veil-normalize.py` の text renderer だけを compact 化する
- grouping key は `shortlist_hint`

## 2. Groups

- `短い review に残す`
- `短い review から外す寄り`

## 3. Boundary

- text renderer:
  - change
- JSON:
  - unchanged

## 4. Rejected Alternatives

- JSON も grouping する
  - rejected: 既存 caller 互換を壊す
- item detail を削る
  - rejected: evidence が弱くなる
