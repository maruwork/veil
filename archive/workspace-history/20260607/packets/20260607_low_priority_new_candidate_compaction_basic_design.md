# Basic Design

## 1. Decision

- `new-candidate` を high / low priority に二分する
- low priority branch だけ compact にする

## 2. Low Priority Rule

- `suggested_level == 観察`
- `priority_hint == 保留候補`
- `retention_hint == 今は見送る`

## 3. High Priority Rule

- 上記以外

## 4. Boundary

- text renderer:
  - change
- JSON:
  - unchanged
