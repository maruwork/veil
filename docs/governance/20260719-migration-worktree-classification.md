# Current migration worktree classification

**Status:** audit record - no commit, installation, generation, or cleanup is authorized by this record.  
**Recorded:** 2026-07-19  
**Design authority:** `docs/veil-design.md`, section 8

**Current audit status (2026-07-21): BLOCKED FOR RELEASE.** The confirmed
outcome, batch, automatic-trigger, and Browser E2E defects have been remediated
locally. Independent two-reviewer holdouts v1, v2, and v3 were frozen correctly
and all failed against their frozen source. The v1/v2 40/40 development reruns
are not release evidence. v3 proves that the raw-text regex outcome engine is
not a reliable production intent boundary. The semantic decision-frame
redesign is now implemented locally as an M2 contract/policy/Skill/recovery-UI
surface. A new independent two-reviewer semantic holdout v4 passed its immutable
first run at 40/40, and the same source passed 276 pytest cases plus the formal
local Edge E2E. This is synthetic evidence only; approved anonymized real-
conversation evaluation, remote CI, final scope review, and distribution remain
unrun. The current
addendum below supersedes historical defect and test-status sentences in this
record.

## Baseline

- branch: `main`, equal to `origin/main` at `26e58f7`
- index: no staged changes
- tracked worktree: 26 modified files, `+2776 / -2233`
- untracked worktree: 95 files after the 2026-07-21 browser E2E addition
- Initial `git diff --check`: failed with exit 2 because the mixed M1/M2 file
  `shared/tools/veil_rule_store.py` had approximately 1,468 CRLF and 897
  LF-only lines, producing trailing-whitespace / EOF blank-line findings.
- Current `git diff --check`: passed after the ownership ledger was fixed and
  the file's CRLF-only noise was normalized to LF. The semantic M1/M2 changes
  remain subject to the release boundary below.

Line-ending remediation is part of mixed-hunk review: assign each affected
hunk to M1 or M2 first, then normalize the owned change. Do not perform a
whole-file mechanical rewrite before that boundary is fixed.

This classification is a release-scope ledger. It does not declare the current
worktree complete or authorize moving, deleting, staging, or committing files.

## 2026-07-21 exclusion-first remediation addendum

Baseline for this addendum: `main` at
`da20b17bea5161b1d3e3de12e09488341c9a2435`; index empty; no install, sync,
staging, commit, push, or generated installed-output refresh. This addendum
classifies the complete exclusion-first remediation surface before further
implementation. It does not authorize release.

### Current path ownership

| Path or semantic hunk | Owner | Current role and boundary |
|---|---|---|
| `shared/tools/veil_capture_outcomes.py` | M2 | Contract v1 raw-text outcome analysis retained only as an explicitly marked diagnostic and HTML-regression reference. It is not the production semantic boundary. |
| `shared/tools/veil_decision_frames.py` | M2 | Contract v2 schema/evidence/critic validator and deterministic read-only policy engine. No text-intent regex and no write authority. |
| `shared/runtime/veil-classify.py` outcome-mode hunks | M2 | Read-only CLI adapter. `--semantic-frames` is the contract v2 route; raw-text `--outcomes` is marked diagnostic and never used as silent fallback. |
| `shared/tools/veil-db.py`, `shared/tools/veil_rule_store.py` atomic JSON batch-upsert hunks | M1 | Validated, all-or-nothing canonical-write adapter used by the Skill so user text is never interpolated into a shell command. No sync-target or installer authority. |
| `shared/runtime/veil-sync.py`, `tests/test_sync.py` background-capture hunks | M2 | Put automatic task-close invocation and silent normal behavior into already-registered targets. No target auto-add or implicit sync authority. |
| `shared/tools/veil_review_template.html` capture/result/clipboard hunks | M2 | Recovery UX. The complete-text AI request is primary; local regex preview is diagnostic only; no direct canonical write. |
| `shared/tools/veil_html_assets.py`, `shared/tools/veil_html_review.py` review-copy hunks | M2 | Generated review UI assets and placeholder rendering. |
| `skills/claude-code/veil-capture.md`, `skills/codex/veil-capture/SKILL.md` | M2 | Conversation interaction and accepted-result processing: silent automatic normal flow, one combined decision, safe structured atomic input, plural completion, and bounded failure reporting. |
| `README.md` lines 70-89, 232-307, 422-438 | M2 | Outcome CLI, capture/browser flow, and exclusion-first operating guidance. |
| `docs/veil-capture-classification.md` | M2 | Outcome contract and evaluation gates. |
| `docs/veil-design.md` sections 3-1, 3-4, 4 wording fields, 5, and capture portions of 7 / 8-3 | M2 | UX behavior and release gates. |
| `docs/veil-design.md` section 8 migration-lock consolidation hunk | M1 | Delivery-contract cleanup, not UX evidence. Keep separately owned; inclusion in any UX release is undecided. |
| `locale/en.json`, `locale/ja.json` capture and runtime-instruction hunks | M2 | User-visible review copy plus the compact background-capture contract injected into registered targets. |
| `tests/test_capture_outcomes.py`, `tests/test_capture_outcomes_cli.py`, `tests/test_capture_outcomes_html.py` | M2 | Development regression for legacy diagnostic parity plus contract-v2 CLI separation. Not independent usability evidence. |
| `tests/test_decision_frames.py` | M2 | Invariant tests for schema, exact evidence, rename, conflicts, critic findings, deterministic policy, and no-write output. Development evidence only. |
| `tests/fixtures/veil_capture_outcome_stratified.json`, `tests/test_capture_outcome_stratified.py` | M2 | Development corpus and regression only. The legacy `stratified` filename does not make it a holdout. |
| `tests/test_db.py` generated-review assertions; `tests/test_locale.py`; `tests/test_skills.py` | M2 | HTML/locale/Skill regression hunks. |
| `tests/browser_e2e_runner.py` | M2 | Formal dependency-free recovery-UI E2E. Covers explicit diagnostic labeling, complete-text semantic review copy, locale, optional fine-tuning, clipboard success/fallback, and zero direct writes; it does not claim semantic accuracy. |
| `.github/workflows/ci.yml` capture compile and Windows Browser E2E hunks | M2 | Must compile the outcome helper and execute the corrected formal runner. |
| `docs/governance/20260719-migration-worktree-classification.md`, `docs/governance/20260720-veil-session-handover.md` | G | Governance/audit records; excluded from runtime release. |
| `docs/governance/20260720-exclusion-first-ux-validation-plan.md`, `docs/governance/20260721-independent-holdout-protocol.md`, `docs/governance/20260721-semantic-decision-frame-redesign.md` | P | Evaluation/authorization and architecture records; excluded from runtime release. |
| `workspace/audit/20260721-exclusion-first-*` | P | Ignored development evidence. No file in these directories is an independent holdout or release payload. |
| `workspace/audit/20260721-independent-holdout-v1/` | P | Ignored independent evaluation input/results. Evidence only; never a runtime release payload. |
| `workspace/audit/20260721-independent-holdout-v2/` | P | Ignored independent evaluation input/results, including the preserved failed first run and non-release development reruns. Evidence only; never a runtime release payload. |
| `workspace/audit/20260721-independent-holdout-v3/` | P | Ignored independent evaluation input/results, including the preserved schema preflight, byte-identical recovery freeze, and failed eligible first run. Evidence only; never a runtime release payload. |
| `workspace/audit/20260721-independent-semantic-holdout-v4/` | P | Ignored independent contract-v2 evaluation input/results, including two-reviewer blind input, immutable freeze, host-AI frames, and the passed eligible first run. Synthetic evidence only; never a runtime release payload. |

The intended runtime/test remediation surface is therefore 28 exact paths: the
20 currently modified tracked runtime/test/document paths plus the eight
untracked M2 paths (`shared/tools/veil_capture_outcomes.py`,
`shared/tools/veil_decision_frames.py`, the stratified development fixture/test,
the three outcome tests, and `tests/test_decision_frames.py`). Existing G/C/R/P
groups retain their prior classification. No other current path is admitted to
the remediation or future release scope; the current unclassified count is
zero.

### Hunk and approval gates

- The M2 sections of `README.md` and `docs/veil-design.md` may move with the UX
  contract only after their wording matches runtime, Skill, HTML, and E2E.
- The M1 section-8 cleanup in `docs/veil-design.md` is separately owned and
  cannot be smuggled into an M2 release by whole-file staging.
- The current 100 cases are development regression data. They cannot support a
  holdout or general-usability claim.
- The automation matrix for `exclude`, `observe`, `existing-match`, and
  `exception` is approved and fixed for holdout v1 and later versions. It permits no automatic
  canonical write; only user-accepted exception mappings may be written as one
  atomic batch.
- The corrected `tests/browser_e2e_runner.py --json` passes locally in Edge.
  Pytest still does not execute this standalone runner; remote Windows CI is a
  separate release gate.

## M1 - canonical and delivery migration

### Owned tracked files

- `install.ps1`, `install.sh`
- `pytest.ini`: disables pytest's shared cache provider so verification does
  not reuse a mutable cross-run cache. The unique audit-shelf base path is
  assigned by the M1-owned `tests/conftest.py` hook.
- `shared/runtime/veil-lint.py`
- `shared/runtime/veil-normalize.py`
- `shared/runtime/veil-status.py`
- `shared/runtime/veil-sync.py`
- `shared/tools/veil-db.py`
- `shared/tools/veil-profile-audit.py`
- `shared/tools/veil-profile-export.py`
- `shared/tools/veil_rule_store.py`: DB schema, SQLite migration, DB
  readback/upsert, profile import/export, lint loading, and the M1-owned
  export composition entry that passes canonical rows to the M2 renderer
- M1-owned hunks in `README.md` and `docs/veil-design.md`: canonical-source,
  installer, sync, lint, status, and profile contracts
- M1-owned hunks in `locale/en.json`, `locale/ja.json`, and the existing test
  files that support the above commands

### Owned untracked files

- `shared/default-profile/technical-writing-default.json`
- `shared/tools/veil_delivery_freshness.py`: M1 exporter/status helper for
  canonical JSON, semantic display-data fingerprints, embedded HTML manifest,
  and `OK` / `STALE` / `ERROR` validation. It does not own review UI behavior
  or SQLite reads/writes.

## M2 - capture classification and review

### Owned tracked files

- `skills/claude-code/veil-capture.md`
- `skills/codex/veil-capture/SKILL.md`
- M2-owned hunks in `README.md`, `docs/veil-design.md`, `locale/en.json`, and
  `locale/ja.json`: capture, HTML review, and candidate behavior
- M2-owned hunks in the existing test suite for capture, HTML, locale, and
  skill behavior

### Owned untracked files

- `docs/veil-capture-classification.md`
- `shared/runtime/veil-classify.py`
- `shared/tools/veil_capture_classifier.py`
- `shared/tools/veil_capture_taxonomy.py`
- `shared/tools/veil_capture_outcomes.py`: contract v1 raw-text diagnostic only.
- `shared/tools/veil_decision_frames.py`: contract v2 semantic-frame validator
  and deterministic no-write policy.
- `shared/tools/veil_html_review.py`: browser-review row renderer. It accepts
  already-read canonical rows and has no SQLite read/write dependency.
- `shared/tools/veil_html_assets.py`: review template loader, locale payloads,
  and locale selection. It has no SQLite read/write dependency.
- `shared/tools/veil_review_template.html`: static browser review and capture
  template loaded only by the M2 asset module.
- `tests/test_capture_classifier.py`
- `tests/fixtures/veil_capture_outcome_stratified.json`
- `tests/test_capture_outcome_stratified.py`
- `tests/test_capture_outcomes.py`
- `tests/test_capture_outcomes_cli.py`
- `tests/test_capture_outcomes_html.py`
- `tests/test_decision_frames.py`
- `tests/test_skills.py`
- `tests/browser_e2e_runner.py`: dependency-free generated-HTML browser E2E
  runner. It serves only a temporary audit copy over loopback and never writes
  the canonical DB, installed HTML, Skill paths, or sync targets.
- `tests/fixtures/veil_capture_attachment_candidates.txt`
- `tests/fixtures/veil_capture_attachment_long_tail.txt`
- `tests/fixtures/veil_capture_chat_seed.json`
- `tests/fixtures/veil_capture_chat_transcript.json`

### Interface ledger: canonical export and review assets

The 2026-07-21 extraction removed the HTML template and locale payloads from
`veil_rule_store.py`. Ownership is now file-based at the M1/M2 interface:

| ID | Surface | Owner | Content and release boundary |
|---|---|---|---|
| B-01 | `shared/tools/veil_rule_store.py` | M1 | Canonical/profile CRUD, normalization, lint loading, protected output validation, and export composition. It may pass already-read rows and explicit settings to M2. |
| B-02 | `shared/tools/veil_html_review.py` | M2 | Pure review-row and placeholder rendering; no DB or filesystem write. |
| B-03 | `shared/tools/veil_html_assets.py` | M2 | Template loading, UI locale payloads, and locale selection; no DB read/write. |
| B-04 | `shared/tools/veil_review_template.html` | M2 | Static review/capture HTML, CSS, and browser JavaScript. It cannot directly write SQLite. |
| B-05 | `shared/tools/veil_delivery_freshness.py` | M1 | Manifest construction and verification over explicitly supplied M2 assets, settings, and canonical rows. |

The dependency direction is `M1 exporter -> M2 renderer/assets -> M1 freshness
envelope`. M2 receives values; it does not select a DB, output path, sync
target, or installer. The physical boundary is now independently testable, but
it does not authorize separate commits or distribution before browser E2E and
the remaining release gates pass.

### Hunk ledger: entry and locale surfaces

| File | Current semantic range | Owner | Content and release boundary |
|---|---:|---|---|
| `README.md` | 12-228 | M1 | Developer route, canonical model, installation, and sync-target contract. |
| `README.md` | 231-351 | M2 | Capture selection and browser review / registration guidance. |
| `README.md` | 352-453 | M1 | Sync, lint, status, SQLite support, and profile-export operations. |
| `README.md` | 454-473 | M2 | Term-adoption priority and capture decision guidance. |
| `README.md` | 474-end | M1 | Runtime file structure and repository operation information. |
| `docs/veil-design.md` | 7-38, 66-108, 142-284, 306-356, 358-end | M1 | Canonical, delivery, status, profile, and migration-completion contracts. The migration section records M2 constraints but introduces no M2 interaction behavior. |
| `docs/veil-design.md` | 41-64, 109-141, 285-305 | M2 | Capture-skill, capture-classifier, and classification-order behavior. |
| `locale/en.json` | all semantic changes | M2 | Review HTML and capture interaction copy. |
| `locale/ja.json` | all semantic changes | M2 | Review HTML and capture interaction copy. |
| `.github/workflows/ci.yml` | Removal of obsolete `export-mirror` / `--rules-dir` invocations in both platform jobs | M1 | CI now follows the SQLite-canonical DB and export contract; this is the delivery-foundation command surface. |
| `.github/workflows/ci.yml` | `Capture syntax check` additions in both platform jobs | M2 | CI syntax coverage for capture classifier, taxonomy, raw diagnostic, semantic-frame policy, HTML assets, runtime classifier, and browser runner. |
| `.github/workflows/ci.yml` | Windows `Browser E2E` step | M2 | Executes recovery wording, diagnostic labeling, complete-text AI request copy, form loading, manual clipboard fallback, and zero direct browser-write assertions in Edge/Chrome. |
| `pytest.ini` | Disable the shared pytest cache provider | M1 | Prevents cross-run cache reuse; unique per-run temporary paths remain owned by `tests/conftest.py`. |
| `tests/conftest.py` | SQLite-only fixtures; removal of legacy rules-directory fixture; unique audit-shelf pytest base path | M1 | Canonical test setup and reproducible isolated test workspace. |
| `tests/helpers.py` | CLI environment overrides and DB/status/sync/profile helper paths | M1 | Delivery and canonical CLI test harness. |
| `tests/helpers.py` | `classify_cmd` helper | M2 | Capture-classification harness. |
| `tests/test_db.py` | SQLite CRUD, seed/profile, protected-output, handle-release, and HTML freshness-manifest assertions | M1 | Canonical/exporter delivery contract. |
| `tests/test_db.py` | Capture/review markup, locale, and browser-review interaction assertions | M2 | Generated review behavior contract. |
| `tests/test_lint.py` | Markdown masking and lint results | M1 | Canonical lint contract. |
| `tests/test_locale.py` | Capture/review copy and embedded review-UI locale assertions | M2 | Review UI wording. |
| `tests/test_profile.py` | SQLite profile audit/export behavior | M1 | Canonical profile support. |
| `tests/test_status.py` | DB and delivery freshness states, JSON, and exit behavior | M1 | Required distribution verification. |
| `shared/runtime/veil-sync.py`, `tests/test_sync.py` canonical/distribution hunks | Canonical-source sync, target protection, and failure behavior | M1 | Delivery sync contract. |
| `shared/runtime/veil-sync.py`, `tests/test_sync.py` background-capture instruction hunks | Automatic task-close invocation and silent normal-flow behavior | M2 | Removes manual task-close invocation from the normal UX. It affects only already-authorized registered targets when a later sync is explicitly run. |

End-of-line-only portions follow the owner of the semantic range containing
them. This completes the current M1/M2 hunk-ownership pass; it does not decide
whether G/C/R material belongs in a release.

## G - active governance and entry surfaces

These paths are active project routing or operating configuration. They are not
M1/M2 release content, and their inclusion in a future change requires a
separate governance release decision.

**Current decision:** exclude G from the M1/M2 migration release. Retain these
files in the worktree; consider them only as a separately reviewed governance
unit after the M1 delivery foundation is verified.

- `.claudeignore`
- `AGENTS.md`
- `CLAUDE.md`
- `DESIGN.md`
- `docs/governance/20260719-migration-worktree-classification.md`
- `docs/governance/20260720-veil-session-handover.md`
- `docs/governance/ai-agent-runtime-token-optimization.md`
- `docs/governance/project-token-optimization-ledger.md`

## C - excluded PJ Framework material

- `.trash-migration/` (67 untracked files)

**Current decision:** exclude C from VEIL migration and do not stage, install,
or delete it in this work unit. Any PJ Framework disposition needs its own
owner and release decision.

## R - retained residue

- `archive/veil-generated.html`

**Current decision:** exclude R from VEIL migration and leave it untouched.
It is neither evidence of current review-HTML freshness nor an installation
target. Archival retention or deletion requires a separately authorized action.

## P - separately recorded proposal

- `docs/governance/20260719-veil-ux-quality-proposal.md`
- `docs/governance/20260720-exclusion-first-ux-validation-plan.md`
- `docs/governance/20260720-p0-integrity-remediation-plan.md`
- `docs/governance/20260721-independent-holdout-protocol.md`
- `docs/governance/20260721-semantic-decision-frame-redesign.md`

This proposal is intentionally outside M1 and M2. It is blocked on migration
completion and must not be folded into the migration release scope.

## Verification result and remaining release gates

Current local source evidence on 2026-07-21:

1. HTML freshness manifest and source-vs-installed Skill checks are implemented.
   The live no-write status check now correctly reports the installed HTML and
   both installed Skills as `STALE`.
2. The HTML template and locale payloads are physically separated from
   `veil_rule_store.py` into M2-owned assets. The M1 exporter retains DB and
   protected-write ownership.
3. The post-v4 same-source run passed all 276 pytest cases in 79.46 seconds
   with a unique `workspace/audit/` basetemp. A prior discarded run used
   `workspace/.tmp/`; that basetemp disappeared after 175 tests and caused 82
   setup errors, so it is not accepted as product regression evidence.
4. The dependency-free Edge E2E passes normal zero-decision, existing-match
   zero-decision, two-exception batching, English/Japanese locale, explicit
   existing-rule change, fine-tuning form load, clipboard success/fallback,
   and zero direct browser-write assertions.
5. `git diff --check` passes. Test-created temporary files use unique paths
   under `workspace/audit/`; no VEIL test artifact is written to `C:\tmp`.

6. The separately authored/reviewed semantic holdout v4 passed its immutable
   first run at 40/40 with zero high-impact false exclusions, 100% exclusion
   and existing-match precision, zero contract validation errors, and exact
   zero/one question counts for ordinary/exception sessions. It performed no
   canonical DB access and did not use the raw-text fallback.

Remaining release gates:

1. Obtain separate approval for an anonymized real
   conversation scope and two-reviewer evaluation before claiming overall UX.
2. Run the same browser step in remote Windows CI. This requires a later
   intentional Git/remote operation and is not implied by local success.
3. Review the final atomic migration candidate scope; do not include G, C, R,
   or P material in the M1/M2 release.
4. Obtain explicit authorization before staging, committing, regenerating the
   installed HTML, reinstalling either Skill, or syncing targets.
5. After authorized distribution, require every delivery member to report
   `OK`; do not suppress or reinterpret the current `STALE` results.
