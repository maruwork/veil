# Project Template Adoption Completion Policy

この policy は
`../frameworks/project-progression-rule.md`
のうち、主に

- `完成の定義`
- `完了条件の明示化`
- `入口の判定`
- `進んでよい条件`

を、template adoption の場面に限定して具体化する。

## 1. Purpose

This policy defines what it means for a project-template adoption packet and template set to be ready for normal delegated use across projects.

## 2. Shared Template Set Completion

Treat the shared template set as complete for delegated use only when all of the following are true:

1. Entry, route, taxonomy, boundary, and workspace policy templates exist.
2. Placement rules are explicit.
3. Stop conditions and owner-only decisions are explicit.
4. A project-local adoption packet template exists.
5. Request and result-intake templates exist.
6. The canonical reading order is explicit.
7. Template-side branch decisions are explicit.

Template-side branch decisions means at least:

- `current ownership`
- `restart aid`
- `publication mode`
- `structure weight`
- `runtime placement`

このうち、

- `current ownership = no-current-canonical`
- `runtime placement = runtime-none`

は、静的 project、schema 棚、artifact 棚、guide 棚のように
daily current や runtime 実体を持たない場合を明示的に許可する。

## 3. Project-Local Packet Completion

Treat a project-local adoption packet as complete only when all of the following are true:

1. The project reading route is explicit.
2. Read, write, and no-touch boundaries are explicit.
3. Current canonical, support, generated, historical, and workspace handling are explicit.
4. Runtime and caller-sensitive paths are explicit.
5. Output files and unresolved-point reporting are explicit.
6. Owner-only decisions remain owner-only.
7. Template-side branch decisions have been filled before project-specific rules are added.
8. Branch consequences are explicit.
9. Any project-specific exception is recorded with a reason why template could not absorb it.

Project-local packet must be able to answer:

- what is decided by the shared progression rule
- what is decided by template-side branches
- what is left as truly project-specific
- what evidence was used to choose the branch decisions

## 4. Non-Goals

The following are not required to call the shared template set complete:

- proof that every target project has already been mutated
- project-specific final close verdicts
- project-specific archive or delete decisions
- project-specific hidden asset disposition
- project-specific runtime naming details that do not affect branch structure

Those belong to project-local adoption work, not shared template completion.

## 5. Fail-Close Rule

If any required shared rule or project-local packet section is unclear, missing, or contradictory, delegated project-template adoption is not ready.

## 6. Stop And Owner Boundary

Delegated AI must stop and return control to the owner if any of the following is true:

1. The current canonical route is unclear.
2. Archive and active work are mixed and the project-local rule is unclear.
3. A hidden active asset is suspected but not described in a visible manifest or entry file.
4. A generated artifact appears to be consumed by a current caller but that caller relationship is not documented.
5. A rename, move, delete, archive, or restore action would affect an unclear caller, runtime, or external dependency.
6. A new shelf or folder would be created without an existing placement rule.
7. The delegated packet conflicts with project-local canonical files.
8. Canonical versus historical classification would need to be redefined.
9. The delegated AI would need to make a final owner judgment rather than return options.
10. Branch consequences cannot be derived from the chosen branch values.
11. A project-specific exception is present but has no justification record.

Delegated AI may continue only if all of the following are true:

1. Project entry and route files are explicit.
2. Read, write, and no-touch paths are explicit.
3. Placement rules are explicit.
4. Hidden active assets are either absent or explicitly described.
5. Owner-only decisions are clearly separated from delegated work.
6. No destructive action is required.

Delegated AI may return:

- current inventory
- placement suggestions under existing rules
- boundary and taxonomy updates in allowed paths
- workspace and artifact policy updates in allowed paths
- rename or move candidates as proposals
- read-only route and caller observations
- unresolved points for owner judgment

Delegated AI must not decide:

- final canonical versus historical classification
- archive, restore, or delete
- hidden active asset keep versus expose versus retire
- caller-sensitive rename, move, or delete
- final close verdict for the project

When stopping, return:

- the exact blocking condition
- the affected path or rule
- the owner decision required
- any safe work that was still completed
- any safe next step that remains possible after owner input

## 7. Reading Bundle For Delegated Use

The normal canonical reading bundle is:

1. `project-progression-rule.md`
2. `project-progression-rule-integration-audit.md`
3. `project-structure-governance-starter-pack.md`
4. `project-file-taxonomy-template.md`
5. `project-boundary-register-template.md`
6. `project-workspace-and-artifact-policy-template.md`
7. `project-template-adoption-packet-template.md`
8. `project-template-adoption-completion-policy.md`
