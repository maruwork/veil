# PJ Template

Purpose: the shared template shelf for structuring projects.

This shelf stores reusable rules, templates, checklists, and examples.
It does not store any one project's current state, task state, runtime facts, or operating log.

## Open First

1. `frameworks/README.md`
2. `policies/README.md`
3. `templates/README.md` only when creating a document
4. `checklists/README.md` only when verifying work
5. `examples/README.md` only when an example is directly needed

If you are installing or adapting this shelf into a project, also read:

- `policies/gates/template-installation.md`

## Shelf Map

- `frameworks/`
  - thinking, decomposition, progression, and review methods
- `policies/`
  - required operating rules and gates
- `templates/`
  - document starters
- `checklists/`
  - verification lists
- `examples/`
  - support material only

## Boundary

Keep here:

- shared progression and workflow rules
- shared placement and naming rules
- shared templates, checklists, and examples
- shared entry-surface structure

Do not keep here:

- project-specific current state
- project-specific task state
- project-specific runtime or DB facts
- project-specific operating logs or registers

## Stable Entry Rule

Outside this shelf, prefer `README.md` as the default link target.

Use a shelf entry file or another declared stable entry surface only when the outer document truly needs that narrower route.

Do not make root entry files, governance docs, or project-local route docs depend on deep internal file paths by default.

## Adoption Rule

When adapting this shelf into a project:

- replace project-local paths, shelf names, command names, and route names
- keep root `AGENTS.md` and `CLAUDE.md` explicit
- keep project-specific judgment and current-state management outside this shelf

After installation, treat the installed `common/` shelf as a synced shared copy.

- do not use it as a project-local authoring area
- keep project-specific rules and operations outside this shelf
- update the shared source and then resync the installed copy

## Reference Boundary

Use `../reference/` only for history or failure analysis.
