# Veil Project File Taxonomy

Status: Active

## 1. Purpose

`veil` の file type ごとの置き場を固定する。

## 2. Entry Rule

- single entry:
  - `AGENTS.md`
- common rule route:
  - `AGENTS.md` -> `common/README.md`
- governance route:
  - `AGENTS.md` -> `index/`
- daily current route:
  - `AGENTS.md` -> `index/project-current-work.md`
- current canonical route:
  - `AGENTS.md` -> `README.md` -> `docs/`
- runtime route:
  - `AGENTS.md` -> `README.md` -> `docs/veil-design.md` -> `shared/runtime/veil-sync.py`

## 3. Placement Matrix

| file type | canonical shelf | examples | notes |
|---|---|---|---|
| `entry / AI control surface` | `./` | `AGENTS.md`, `CLAUDE.md`, `.claudeignore` | root control files only |
| `common reusable rules` | `common/` | `frameworks/`, `policies/`, `templates/`, `checklists/`, `examples/` | local copy of pj-template assets |
| `governance / policy` | `index/` | `project-file-taxonomy.md` | local structure authority |
| `current companion` | `index/` | `project-current-work.md` | active bundle / continue surface; does not replace canonical docs or runtime authority |
| `current canonical docs` | `./`, `docs/` | `README.md`, `docs/veil-design.md`, `docs/veil-product-design.md` | active project docs |
| `mainline runtime code` | `shared/runtime/` | `shared/runtime/veil-sync.py`, `shared/runtime/veil-lint.py`, `shared/runtime/veil-normalize.py` | active mainline runtime |
| `profile support runtime` | `shared/tools/` | `shared/tools/veil-profile-audit.py`, `shared/tools/veil-profile-export.py`, `shared/tools/veil-db.py`, `shared/tools/veil_rule_store.py` | active support tools; not mainline authority |
| `skill assets` | `skills/` | `veil-capture` | mainline skill shelf |
| `temporary work` | `workspace/` | active packet, decision sheet, smoke fixture, generated drafts | non-canonical only |
| `historical` | `archive/` | retired outputs/docs, prior wave packet | historical only |
| `retired support` | `archive/retired-support/` | `app.py`, `docs/manual.html`, `veil-audit-db.py`, `veil_audit_core.py`, `vocab.db`, `ui/`, `uijs/`, `js/`, `install-startup.py` | not part of current mainline |
| `hidden helper state` | `.agents/`, `.claude/`, `.remember/` | helper state | do not treat as governance or canonical |

## 4. Placement Decision Order

1. prefer existing declared shelf
2. do not create a new top-level shelf unless role changes
3. reusable common rules go to `common/`
4. governance and placement rules go to `index/`
5. current project docs stay in `README.md` or `docs/`
6. active mainline runtime stays in declared root runtime files
7. retired support stays out of the current mainline route
8. temporary or generated work stays in `workspace/`

## 5. Canonical Separation Rule

- `common/` is reusable rule shelf and not current project canonical
- `index/` is governance support and not current project canonical
- `index/project-current-work.md` is the daily current / bundle declaration surface
- `README.md` and `docs/` hold canonical docs
- `shared/runtime/veil-sync.py`, `shared/runtime/veil-lint.py`, and `shared/runtime/veil-normalize.py` are mainline runtime authority
- `~/.veil/veil.db` is the current canonical route for vocabulary rules
- `~/.veil/rules/` is the AI-readable markdown surface and transition mirror
- `shared/tools/veil-profile-audit.py`, `shared/tools/veil-profile-export.py`, `shared/tools/veil-db.py`, and `shared/tools/veil_rule_store.py` are active support runtime and not part of the mainline authority route
- retired support lives under `archive/retired-support/<date>/`
- `app.py`, `docs/manual.html`, `ui/`, `uijs/`, `js/`, `veil-audit-db.py`, `veil_audit_core.py`, and `vocab.db` are outside the current mainline route
- `workspace/` is temporary
- `workspace/` root keeps only active packet, open decision sheet, and current smoke helper
- close 済み wave packet は `archive/workspace-history/<date>/packets/` に置く
- dated stray artifact は `archive/workspace-history/<date>/artifacts/` に置く
- `archive/` is historical
- hidden helper shelves are not canonical

## 6. Root Rule

Keep root thin.

Allowed root files now:

- `AGENTS.md`
- `CLAUDE.md`
- `.claudeignore`
- `README.md`
- `CHANGELOG.md`
- `LICENSE`
- `SECURITY.md`
- `CODE_OF_CONDUCT.md`
- `CONTRIBUTING.md`

Root shelves:

- `common/`
- `docs/`
- `index/`
- `shared/`
- `skills/`
- `workspace/`
- `archive/`

## 7. Workspace Rule

- active workspace:
  - `workspace/`
- workspace root keep set:
  - active packet
  - open decision sheet
  - current smoke helper
- generated support sub-shelves:
  - `workspace/reference/`
  - `workspace/profile-exports/`
  - `workspace/veil_stage*/`
- generated output must not be mixed into `README.md` or `docs/`
- reusable rules must not be mixed into `README.md`, `docs/`, or runtime files
- close 済み wave packet must not remain in `workspace/` root

## 8. Archive Rule

- archive root:
  - `archive/`
- workspace history route:
  - `archive/workspace-history/<date>/packets/`
  - `archive/workspace-history/<date>/artifacts/`
- do not mix active files into archive
