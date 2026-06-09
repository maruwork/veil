# Project Template Installation Gate Policy

## 1. Purpose

This policy defines the gate that must be passed before any project-local file or folder is created for `pj-template` adoption.

The goal is to prevent delegated AI from creating governance shelves, entry files, packets, or other installation artifacts before rule compatibility has been checked.

## 2. Core Rule

Do not create any new project-local file or folder for `pj-template` adoption until all installation-gate checks in this policy have passed.

If the checks have not passed, stop at review and return findings, options, and owner decisions only.

## 3. Installation-Gate Checks

Treat project-local installation as allowed only when all of the following are true.

1. The shared `pj-template` set is itself complete enough for delegated use.
2. The target project's current entry route is explicit.
3. The target project's existing governance, guide, register, and support shelves have been inspected.
4. Existing shelves cannot already explain the intended role.
5. The placement rule for any new file or folder is explicit.
6. Read, write, and no-touch boundaries are explicit.
7. Current canonical, support, generated, historical, and workspace handling are explicit enough to avoid redefinition by the delegated AI.
8. No owner-only decision is being smuggled into the installation step.
9. Template-side branch decisions have been checked first.
10. The evidence used to fill branch decisions is explicit.
11. Any new project-specific rule is justified by a recorded template-side exception.

If any one of these checks fails, installation is not ready.

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

If these can absorb the difference, do not create a new project-local rule just to explain that difference.

Record at least:

- what branch value was chosen
- what file or shelf confirmed that choice
- what linked consequence was created by that choice

## 4. Required Review Order

Before proposing or creating any project-local installation artifact, read in this order.

1. `project-progression-rule.md`
2. `project-progression-rule-integration-audit.md`
3. `project-template-adoption-completion-policy.md`
4. `file-operation-policy.md`
5. `naming-and-shelf-policy.md`
6. `entry-guide-reference-separation-policy.md`
7. the target project's current entry file
8. the target project's current governance or closest equivalent shelf

Do not skip from shared templates directly to file creation in the target project.

## 5. What Counts As Installation

The following are installation actions and require this gate.

- creating a new `governance/` shelf
- creating a new `README.md` inside an existing shelf for `pj-template` use
- creating a `project-template-adoption-packet.md`
- creating taxonomy / boundary / workspace policy files in the target project
- creating any new guide, register, or route file whose purpose is template adoption

## 6. Stop Conditions

Delegated AI must stop and not install if any of the following is true.

1. The target project already has a governance, guide, register, or rule shelf whose authority relationship is still unclear.
2. A new folder would be created without an explicit placement rule.
3. The target project has an existing file that may already serve the same role.
4. Installing a new file would change the entry route, governance authority, or canonical reading order without owner approval.
5. Archive, restore, delete, or caller-sensitive rename would be needed first.
6. A hidden active asset or generated caller relationship is still unresolved.
7. The delegated AI would need to decide final canonical versus historical classification.
8. The delegated AI is about to create a project-local rule for something that should still be handled by template-side branch decisions.
9. The delegated AI cannot point to evidence for the chosen branch decisions.
10. The delegated AI is about to add a project-specific rule without filling the exception register.

## 7. Allowed Outputs Before Installation

Before the gate passes, delegated AI may still return:

- current inventory
- existing shelf analysis
- route and authority observations
- conflict analysis
- placement suggestions under existing rules
- owner-decision questions
- proposed installation plan

Delegated AI must not create project-local installation files at this stage.

## 8. Allowed Installation After Gate Passes

After the gate passes, delegated AI may create only the minimum files needed by the approved installation plan.

Default rule:

- prefer existing shelves over new shelves
- prefer existing entry files over replacement entry files
- prefer updating an existing register path over creating a parallel authority path

## 9. Follow-Up Rule

If installation is allowed and performed, the delegated AI must also update:

- the local route or governance entry that points to the installed file
- the management record that tracks where installation happened
- any shared or project-local note that defines the resulting authority relationship

If those follow-up updates are not yet safe, stop before installation.

## 10. Fail-Close Rule

If there is uncertainty about whether a new file or folder is legitimate under the project's file and folder rules, fail closed and do not install.

Return:

- the exact rule conflict or uncertainty
- the affected path
- the owner decision required
- the safe next step
