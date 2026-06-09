# Profile Export Manifest Contract Basic Design

## 1. CLI Design

- `--domain`
  - default: `technical-writing`
- `--intended-use`
  - default: `AI-assisted technical writing terminology guardrail`
- `--base-profile`
  - default: `none`

## 2. Manifest Design

- `profile_name`
- `domain`
- `intended_use`
- `base_profile`
- `source_rules_dir`
- `export_dir`
- `exported_at`
- `summary`
- `files`

## 3. Design Principle

- contract を増やしすぎず、branch 判定に必要な最小限だけ持つ
