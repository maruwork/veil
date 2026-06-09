# Veil Project Workspace And Artifact Policy

Status: Active

## 1. Purpose

`veil` の workspace / artifact / historical の扱いを固定する。

この文書は workspace / generated / archive の扱いを決めるための local policy であり、

- reusable common rule shelf
- current canonical doc surface
- runtime authority surface

そのものを単独で決める文書ではない。
それらは `common/README.md`、`index/project-file-taxonomy.md`、
`index/project-boundary-register.md` を正本に読む。

## 2. Workspace Root

- active workspace:
  - `workspace/`

## 3. Workspace Allowed Content

- active packet
- open decision sheet
- current smoke helper
- temporary notes
- generated drafts
- local experiments
- one-off review outputs

## 4. Workspace Prohibited Content

- reusable common rules
- current canonical docs
- active runtime code
- final governance rules
- files that should already live in `archive/`

## 5. Artifact Rule

- generated or trial artifacts go to `workspace/`
- generated output must not be treated as canonical without review
- generated output must not be written into `common/` or `index/`
- hidden helper state under `.agents/`, `.claude/`, `.remember/` remains outside canonical route

## 6. Promotion Rule

Promote from `workspace/` only after review.

- reusable common rules -> `common/`
- governance / structure rules -> `index/`
- current docs -> `README.md` or `docs/`
- active runtime updates -> declared root runtime surface
- historical material -> `archive/`

## 7. Archive Rule

- historical shelf:
  - `archive/`
- workspace history route:
  - `archive/workspace-history/<date>/packets/`
  - `archive/workspace-history/<date>/artifacts/`
- do not restore from archive without explicit decision

## 8. Stop Rule

Stop if:

- workspace output appears to become current canonical without review
- `common/` or `index/` is being used as scratch or generated dump
- archive / restore / delete is needed
- hidden helper state is being treated as governance or canonical authority
