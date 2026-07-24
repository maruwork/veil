# VEIL P0 integrity remediation plan

**Status:** planning only. This record authorizes no runtime implementation,
canonical DB change, HTML generation, Skill installation, sync, staging,
commit, push, or Git-history action.

## Objective

Restore a single auditable contract before either migration delivery work or
exclusion-first UX evaluation continues. A passing test suite is insufficient
while worktree ownership, user-facing documentation, and runtime behavior
disagree.

## P0-1: Restore release-ledger completeness

**Known gap:** `shared/tools/veil_delivery_freshness.py` is untracked and is
not named in the M1 ledger, despite implementing the M1 HTML delivery contract.

**Work:**

1. Enumerate every `git status --porcelain=v1` entry, expanding untracked
   directories to individual files.
2. Compare the exact paths and each semantic hunk with the ledger.
3. Add the freshness helper as M1, and review the ownership of `veil-status`,
   `veil_rule_store`, `veil-db`, and their tests.
4. For mixed files, record hunk ranges and an owner; do not rely on a filename
   class alone.

**Evidence:** a path-by-path reconciliation table with `unclassified = 0`.

**Exit criterion:** every changed or untracked item is assigned once to
M1/M2/G/C/R/P or an explicitly recorded proposal.

## P0-2: Establish one four-state status contract

**Known gap:** ordinary design and README language still describe
`OK/WARN/ERROR` and ERROR-only nonzero exit, while migration design and runtime
use `OK/STALE/MISSING/ERROR` with all required non-OK delivery members failing
`--check`.

**Work:**

1. Inventory all status claims in `docs/veil-design.md`, `README.md`, locale
   strings, CLI text/JSON, and tests.
2. Write one contract table defining each state, which members are required,
   and `--check` exit behavior.
3. Reconcile the documentation and locale terms with the accepted contract.
4. Define JSON fields and stable machine-readable state values.
5. Test HTML and Skill cases for OK, STALE, MISSING, and ERROR; test unreadable
   or corrupt DB and malformed manifest separately.

**Evidence:** source-to-doc matrix and explicit test names for all states.

**Exit criterion:** no remaining user-facing or machine-facing text describes
the obsolete three-state/ERROR-only rule.

## P0-3: Repair the evaluation-plan write boundary

**Known gap:** the exclusion-first plan calls evaluation evidence "read-only"
while also requiring limited writes under `workspace/audit/`.

**Work:**

1. Replace the phrase with: "no writes to canonical, distribution, external,
   or Git state; bounded evaluation-artifact writes under workspace/audit are
   allowed."
2. Define artifact naming, retention owner, deletion authority, and a
   reproducibility command for each run.
3. Separate `exclude` (non-decision) from `existing-match` (a valid resolved
   operational outcome) in definitions, metrics, and summaries.
4. Add corpus prerequisites: sampling unit, source/period approval, privacy
   treatment, labeller, disagreement handling, holdout split, impact rubric,
   and baseline measurement.

**Exit criterion:** WP-1 can begin without interpreting any ambiguous write,
data-scope, or metric rule.

## P0-4: Reproducible M1 verification and release boundary

**Work:**

1. Use a unique `workspace/audit/<run>/` base path and disable pytest cache.
2. Run DB/status tests, then the full suite in bounded groups if runtime limits
   require it; record commands, counts, exit codes, and warnings.
3. Run `git diff --check`.
4. Run `veil-status --check` without treating stale delivery members as fixed.

**Exit criterion:** M1 verification evidence distinguishes passing source tests
from stale installed HTML/Skills. No installer, sync, regeneration, staging,
or commit is performed.

## Sequence and stop rule

Execute P0-1 through P0-4 in order. Do not begin exclusion-first corpus work,
new UX work, generated-output refresh, installation, sync, or Git operations
until P0 exit criteria are met and the next scope is explicitly approved.
