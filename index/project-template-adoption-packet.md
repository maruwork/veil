# Veil Project Template Adoption Packet

Status: Active

## 1. Purpose

`pj-template` を `veil` に適用する際の local rule を固定する。

## 2. Reading Route

1. `C:\Users\f_tan\project\veil\AGENTS.md`
2. `C:\Users\f_tan\project\veil\common\README.md`
3. `C:\Users\f_tan\project\veil\common\frameworks\project-progression-rule.md`
4. `C:\Users\f_tan\project\veil\index\project-template-adoption-packet.md`
5. `C:\Users\f_tan\project\veil\index\project-file-taxonomy.md`
6. `C:\Users\f_tan\project\veil\index\project-boundary-register.md`
7. `C:\Users\f_tan\project\veil\index\project-workspace-and-artifact-policy.md`
8. `C:\Users\f_tan\project\veil\index\project-current-work.md`
9. `C:\Users\f_tan\project\veil\README.md`
10. `C:\Users\f_tan\project\veil\docs\veil-design.md`
11. `C:\Users\f_tan\project\veil\shared\runtime\veil-sync.py`
12. `C:\Users\f_tan\project\veil\shared\runtime\veil-lint.py`
13. `C:\Users\f_tan\project\veil\shared\runtime\veil-normalize.py`

## 3. Governance Shelf

- governance shelf:
  - `index/`
- governance entry:
  - `index/project-template-adoption-packet.md`
- common shelf:
  - `common/`
- common entry:
  - `common/README.md`

## 3.5 Bundle Adoption

- bundle declaration surface:
  - `index/project-current-work.md`
- continue check surface:
  - `index/project-current-work.md`
- close / residual split adoption:
  - `yes`
- template version status:
  - `upgraded-template`

## 4. Read / Write / No-Touch

### Read

- `AGENTS.md`
- `CLAUDE.md`
- `common/`
- `index/`
- `index/project-current-work.md`
- `README.md`
- `docs/`
- `shared/runtime/veil-sync.py`
- `shared/runtime/veil-lint.py`
- `shared/runtime/veil-normalize.py`
- `shared/tools/veil-profile-audit.py`
- `shared/tools/veil-profile-export.py`
- `shared/tools/veil-db.py`
- `shared/tools/veil_rule_store.py`
- `skills/`
- `workspace/`
- `archive/`

### Write

- `common/`
- `index/`
- `README.md`
- `docs/`
- `shared/runtime/veil-sync.py`
- `shared/runtime/veil-lint.py`
- `shared/runtime/veil-normalize.py`
- `shared/tools/veil-profile-audit.py`
- `shared/tools/veil-profile-export.py`
- `shared/tools/veil-db.py`
- `shared/tools/veil_rule_store.py`
- `skills/`
- `workspace/`

### No-Touch

- `archive/`
- `.agents/`
- `.claude/`
- `.remember/`

## 5. Current Shelf Classification

- common reusable rules:
  - `common/`
- current canonical:
- `README.md`
  - `docs/veil-design.md`
  - `docs/veil-product-design.md`
  - `index/project-current-work.md`
  - `shared/runtime/veil-sync.py`
  - `shared/runtime/veil-lint.py`
  - `shared/runtime/veil-normalize.py`
- support:
  - `index/project-template-adoption-packet.md`
  - `index/project-file-taxonomy.md`
  - `index/project-boundary-register.md`
  - `index/project-workspace-and-artifact-policy.md`
  - `index/project-current-work.md`
  - `shared/tools/veil-profile-audit.py`
  - `shared/tools/veil-profile-export.py`
  - `shared/tools/veil-db.py`
  - `shared/tools/veil_rule_store.py`
  - `skills/`
  - retired support surface (`app.py`, `veil-audit-db.py`, `veil_audit_core.py`, `ui/`, `uijs/`, `js/`, `docs/manual.html`, `vocab.db`, `install-startup.py`)

- current external canonical route:
  - `~/.veil/veil.db`
- current external transition mirror:
  - `~/.veil/rules/`
- temporary:
  - `workspace/`
- historical:
  - `archive/`

## 6. Runtime And Caller-Sensitive Paths

- runtime-sensitive paths:
  - `shared/runtime/veil-sync.py`
  - `shared/runtime/veil-lint.py`
  - `shared/runtime/veil-normalize.py`
  - `shared/tools/veil-profile-audit.py`
  - `shared/tools/veil-profile-export.py`
  - `shared/tools/veil-db.py`
  - `shared/tools/veil_rule_store.py`
- caller-sensitive rename / move:
  - `shared/runtime/veil-sync.py`
  - `shared/runtime/veil-lint.py`
  - `shared/runtime/veil-normalize.py`

## 7. Expected Local Deliverables

- `common/README.md`
- `common/frameworks/project-progression-rule.md`
- `index/project-template-adoption-packet.md`
- `index/project-file-taxonomy.md`
- `index/project-boundary-register.md`
- `index/project-workspace-and-artifact-policy.md`

## 8. Output And Reporting

- generated / scratch work:
  - `workspace/`
- current project docs must not be written into `archive/`
- hidden helper / memory shelves stay outside canonical route

## 9. Owner-Only Decisions

- archive / restore / delete
- moving current canonical docs out of `README.md` / `docs/`
- restructuring runtime out of `shared/runtime/veil-sync.py` / `shared/runtime/veil-lint.py` / `shared/runtime/veil-normalize.py`
- promoting retired support back into canonical status

## 10. Stop Conditions

- a new top-level shelf becomes necessary
- `index/` stops being the right governance shelf
- `workspace/` output appears to be treated as canonical
- moving or renaming caller-sensitive mainline runtime assets becomes necessary

## 11. Completion Rule

- governance route is explicit
- local common shelf is explicit
- `README.md` / `docs/` remain canonical doc surfaces
- mainline runtime and doc authority are separated
- retired support does not override the mainline
- `workspace/` and `archive/` remain non-canonical
