# Profile Branch From Manifest Basic Design

## 1. CLI Design

- new option:
  - `--base-manifest <path>`

## 2. Inheritance Rule

- `--base-manifest` 指定時:
  - source rules dir:
    - manifest と同じ directory
  - default `base_profile`:
    - base manifest `profile_name`
  - default `intended_use`:
    - base manifest `intended_use`
- explicit CLI arg があればそちらを優先する

## 3. Branch Recipe

1. `technical-writing-default` pack を export する
2. その `manifest.json` を `--base-manifest` に渡す
3. 新しい `--profile-name` と `--domain` を指定して branch pack を作る

## 4. Verification Design

- py_compile
- `--base-manifest workspace/profile-exports/technical-writing-default/manifest.json --profile-name medical-guardrail --domain medical`
- manifest readback
