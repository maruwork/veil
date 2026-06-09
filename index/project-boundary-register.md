# Veil Project Boundary Register

Status: Active

## 1. Purpose

`veil` の shelf class と authority を固定する。

## 2. Register

| shelf | class | current canonical | role | notes |
|---|---|---|---|---|
| `./AGENTS.md` | `front current surface` | `yes` | entry | first read |
| `./CLAUDE.md` | `support` | `no` | AI instruction surface | root control file |
| `./.claudeignore` | `support` | `no` | AI read-scope control | root control file |
| `common/` | `support` | `no` | reusable rule shelf | local copy of pj-template assets |
| `index/` | `support` | `no` | governance support | structure and placement authority |
| `index/project-current-work.md` | `support` | `yes` | daily current / active bundle surface | `continue` returns here first |
| `./README.md` | `current canonical` | `yes` | product/project overview | primary doc surface |
| `docs/` | `current canonical` | `yes` | active docs | design surface |
| `shared/runtime/veil-sync.py` | `current canonical` | `yes` | mainline runtime code | sync authority |
| `shared/runtime/veil-lint.py` | `current canonical` | `yes` | mainline runtime code | verify authority |
| `shared/runtime/veil-normalize.py` | `current canonical` | `yes` | mainline runtime code | normalization authority |
| `shared/tools/veil-profile-audit.py` | `support` | `no` | profile support runtime code | audit only |
| `shared/tools/veil-profile-export.py` | `support` | `no` | profile support runtime code | export only |
| `shared/tools/veil-db.py` | `support` | `no` | SQLite Stage 1 support runtime code | init/import/readback only |
| `shared/tools/veil_rule_store.py` | `support` | `no` | SQLite Stage 1 shared support runtime code | schema/parser/helper only |
| `skills/` | `support` | `no` | skill assets | support only |
| `archive/retired-support/` | `historical` | `no` | retired support shelf | old runtime, UI, manual, helper data live here |
| `workspace/` | `generated` | `no` | active generated work | root keeps only active packet, decision sheet, smoke helper |
| `archive/` | `historical` | `no` | history | prior wave packet and retired artifact live here |
| `.agents/` | `generated` | `no` | helper state | hidden helper shelf |
| `.claude/` | `generated` | `no` | helper state | hidden helper shelf |
| `.remember/` | `generated` | `no` | helper state | hidden helper shelf |

## 3. Reading Rules

- `common/` is the reusable rule shelf for project-wide progression and templates
- `index/` is governance support, not current project truth
- `index/project-current-work.md` is the daily current / bundle declaration surface
- `README.md` and `docs/` are canonical doc surfaces
- `shared/runtime/veil-sync.py`, `shared/runtime/veil-lint.py`, and `shared/runtime/veil-normalize.py` are mainline runtime authority
- `~/.veil/veil.db` is the current canonical route for vocabulary rules
- `~/.veil/rules/` is the transition mirror and AI-readable markdown surface
- `shared/tools/veil-profile-audit.py`, `shared/tools/veil-profile-export.py`, `shared/tools/veil-db.py`, and `shared/tools/veil_rule_store.py` are active support runtime and not mainline authority
- retired support lives under `archive/retired-support/<date>/`
- `workspace/`, `archive/`, and hidden helper shelves do not become canonical without explicit review
- close 済み wave packet は `archive/workspace-history/<date>/packets/` へ退避する
- dated stray artifact は `archive/workspace-history/<date>/artifacts/` へ退避する

## 4. Minimum Required Shelves

- entry surface
- common reusable rule shelf
- governance shelf
- canonical doc surface
- runtime authority surface
- workspace shelf
- archive shelf

## 5. Boundary Questions

- reusable progression / checklist / template assets are read from `common/`
- structure and placement rules are read from `index/`
- current project docs go to `README.md` or `docs/`
- active mainline runtime code goes to declared root runtime files
- retired support stays outside the current mainline route
- temporary or generated work goes to `workspace/`
- historical material goes to `archive/`

## 6. Completion Rule

- taxonomy and register agree
- doc authority and runtime authority are explicit
- workspace, archive, and hidden helper shelves are separated from active authority
