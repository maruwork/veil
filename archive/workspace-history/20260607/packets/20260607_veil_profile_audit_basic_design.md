# VEIL Profile Audit Basic Design

## 1. Architecture

- input: rules dir
- parser: heading-aware rule parser
- output:
  - summary
  - per-file counts
  - legacy flat rule presence

## 2. Data Model

### File Report

- `file`
- `required_count`
- `recommended_count`
- `observe_count`
- `legacy_flat_count`
- `total_rules`

### Summary

- files
- total rules
- total required
- total recommended
- total observe
- total legacy flat

## 3. Output Design

### Text

- summary line
- file list
- legacy flat file marker

### JSON

- machine-readable summary + file reports

## 4. Compatibility

- heading のない rule line は `legacy_flat_count` へ入れる
- runtime semantics と同じく logical level は `必須` とみなしてよいが、audit では legacy として表面化する
