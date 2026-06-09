# Profile Support Alignment And Export Basic Design

## 1. Design Principle

- `capture -> normalize -> sync -> lint` の mainline は変えない
- profile support tools は mainline authority ではなく support runtime として分離する
- export は read-only source から non-destructive output を作る

## 2. Governance Design

- `veil-profile-audit.py` と `veil-profile-export.py` は root の active support runtime とする
- `index/project-file-taxonomy.md` には `profile support runtime` を追加する
- `index/project-boundary-register.md` では `support` class として登録する
- `AGENTS.md` では mainline authority と切り分けて `profile support tools` として案内する

## 3. Export Design

- source:
  - `~/.veil/rules/` または `--rules-dir`
- default output:
  - `workspace/profile-exports/<profile-name>`
- output:
  - copied rule files
  - `manifest.json`
- manifest fields:
  - `profile_name`
  - `source_rules_dir`
  - `export_dir`
  - `summary`
  - `files`
- script は source を一切変更しない

## 4. Verification Design

- `python -m py_compile veil-profile-audit.py veil-profile-export.py`
- export to `workspace/profile-exports/technical-writing-default`
- exported files と manifest readback
