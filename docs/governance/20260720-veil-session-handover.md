# VEIL session handover — 2026-07-20

**Status:** continuation handover. This document records the current worktree
and reasoning boundary. It does not authorize staging, committing, installing,
syncing, regenerating user-facing output, or changing `~/.veil`.

## 1. Read this first

1. Root `AGENTS.md`, then `README.md` and `common/README.md`.
2. `docs/governance/ai-agent-runtime-token-optimization.md`.
3. `docs/veil-design.md`, especially section 8.
4. `docs/governance/20260719-migration-worktree-classification.md`.
5. This handover, then the exact runtime/tool file being changed.

Do not broad-read `workspace/`, `archive/`, or `.trash-migration/`. They are
not VEIL canonical sources. The user explicitly requires all future audit/test
scratch space to be under this repository's `workspace/`; do **not** use
`C:\\tmp`. The agent-created `C:\\tmp\\veil*` audit artifacts were removed on
2026-07-20.

## 2. System and authority model

VEIL is a local-first vocabulary-consistency system.

- SQLite at `~/.veil/veil.db` is the canonical vocabulary store.
- Markdown mirrors, root `AGENTS.md` / `CLAUDE.md`, generated `veil.html`, and
  installed skills are derived or distribution surfaces; they are not the
  canonical vocabulary source.
- Active implementation is in `shared/runtime/`, `shared/tools/`, and
  `skills/`. `common/` is a reusable rule shelf, not the current vocabulary
  store.
- `README.md` is the developer entry route. `docs/veil-design.md` is design
  authority. Root `AGENTS.md` and `CLAUDE.md` in the worktree are classified
  as G (governance/entry), not migration release content.

The desired operational distinction is:

```text
User-facing: capture -> choose -> save
Internal:     classify -> normalize -> record -> export HTML -> sync -> lint
```

Do not create a second canonical store or a second sync/installer path.

## 3. Why this work started

The initial question compared the Zenn article's “referent before label” /
semantic-generation approach with VEIL. The conclusion was:

- Semantic-generation is a conversation-time method for establishing what a
  term refers to before naming it.
- VEIL is a persistent, post-decision vocabulary consistency layer.
- Do not make a referent table or pre-registration gate mandatory in VEIL.
  Use semantic-generation when a conversation needs it, and register only
  durable decisions in VEIL.

The UX review also concluded that “lighter” is not a goal by itself. A change
must improve comprehension, decision quality, or operational reliability.
Candidate 2 optionality is desirable in principle, but it is deferred because
the Skills, HTML UI, tests, and installation state were not yet aligned.
See `20260719-veil-ux-quality-proposal.md`; it remains a proposal, not an
implementation authorization.

### User decision criteria that govern continuation

The user explicitly rejected simplification as an aesthetic goal. A proposed
reduction is valid only when it demonstrably improves UX, vocabulary quality,
or operational reliability. This is why Candidate 2 optionality is deferred
rather than being applied as a superficial reduction in fields or prompts.

The user also explicitly selected this order:

```text
Git audit -> design boundary -> narrow implementation -> verification ->
only then distribution/update/commit
```

The rationale is that the pre-existing worktree contains a large, mixed,
partly-untracked migration. Adding UX work, installing Skills, or regenerating
HTML before ownership and delivery state are known would combine unrelated
decisions and destroy auditability.

Continue autonomously through safe, in-scope verification and implementation;
do not repeatedly pause merely to restate the next step. Conversely, do not
expand into installation, sync, generated-output refresh, external writes, or
Git history operations unless their release gates are satisfied and the user
has authorized that scope.

## 4. Initial audit findings and their implications

The following were directly verified earlier in this workstream. Re-derive
them before making a current-state claim if they affect a release decision.

1. The canonical DB had three active rules, so it is insufficient as broad UX
   evidence.
2. Candidate 2 was optional in the DB model but mandatory in both capture
   Skills and expected in the generated review flow.
3. The generated `~/.veil/veil.html` and installed Codex/Claude skills did not
   match the repository source. The observed HTML used the old UI (for example,
   old command-copy wording) rather than the source review flow.
4. `veil-status --check` treated HTML and skills as OK when present. It did not
   check freshness. Thus it could report OK for stale assets.
5. The former sync target `C:\\tmp\\veil_behavior_target.md` remained in
   `~/.veil/targets.json`. It is now absent and produces WARN. Do not recreate
   it; remove or otherwise resolve this stale target as part of the M1 status /
   delivery work.
6. Browser E2E coverage was absent at the original handover. Local Edge E2E
   is now implemented and passing as recorded in section 12; the remote
   Windows CI execution remains outstanding.

The design therefore defines four output states:

```text
OK       exists and matches the expected source fingerprint
STALE    exists but fingerprint does not match
MISSING  does not exist
ERROR    unreadable, corrupt, or verification failed
```

For required distribution surfaces, `STALE`, `MISSING`, and `ERROR` must make
`veil-status --check` return nonzero. HTML needs an exporter-owned embedded
manifest. Skills use the simple contract
`fingerprint(installed bytes) == fingerprint(source bytes)`; they do not need
an embedded manifest. Database fingerprints must be semantic display-data
fingerprints, not SQLite-file hashes.

## 5. Git and migration audit

### Baseline and scope

- Branch: `main`; HEAD is `26e58f77c0412ca40f404da6e9f6af54438ff71e` and was
  equal to `origin/main` when audited.
- The real Git index remains empty. No staging, commit, install, generated
  output refresh, or sync was performed in this workstream.
- The worktree is intentionally large and dirty. Do not reset, checkout,
  restore, or broadly clean it.
- `docs/governance/20260719-migration-worktree-classification.md` is the
  complete release-scope ledger. It classifies every changed/untracked item as
  M1, M2, G, C, R, or P.

Categories:

- **M1:** SQLite canonical, DB CLI, sync, lint, normalize, status, installer,
  profile import/export/audit, delivery/freshness foundation, and tests.
- **M2:** capture classifier/taxonomy, review HTML behavior, Skills, fixtures,
  and capture/review tests.
- **G:** active governance and entry files (`AGENTS.md`, `CLAUDE.md`,
  `.claudeignore`, `DESIGN.md`); excluded from migration release.
- **C:** PJ Framework-derived material (`.trash-migration/`); excluded.
- **R:** archive/residue (`archive/`); excluded.
- **P:** the dated UX proposal; separately reviewed and blocked on migration
  completion.

### Mixed-file result

`shared/tools/veil_rule_store.py` was the critical mixed M1/M2 file. Its
hunks are mapped in the ledger. The meaningful boundaries are:

```text
H-01  runtime paths/defaults                 M1
H-02  generated review template/browser UI   M2
H-03  SQLite/profile/canonical CRUD           M1
H-04  review-table rendering                  M2
H-05  review HTML composition                 M2
H-06  canonical read + protected HTML write   M1
H-07  lint-facing DB load                     M1
```

The old M1 and M2 changes share pre-change patch anchors, so the original
worktree cannot honestly be represented as two independently applicable Git
patches. Treat it as **one atomic migration release candidate** until a narrow
interface refactor creates independently verifiable units. Do not claim that
M1 and M2 can be committed separately merely because they have ownership
labels.

## 6. Changes made in this workstream

### Design and records

- Added/updated migration-lock contracts in `docs/veil-design.md`:
  canonical/delivery surfaces, four freshness states, fingerprint direction,
  M2-to-M1 boundary, deferred UX work, and lock exit conditions.
- Added `docs/governance/20260719-veil-ux-quality-proposal.md` as a proposal.
- Added and updated the migration classification ledger cited above.
- Added this handover.

### Implementation just completed

The first narrow interface extraction was made:

- New `shared/tools/veil_html_review.py` owns review-table rendering and HTML
  placeholder replacement.
- It accepts already-read canonical rows and configuration payloads; it does
  **not** open, read, or write SQLite.
- `shared/tools/veil_rule_store.py` now delegates that rendering while it keeps
  canonical DB readback, protected output validation, and file writing.
- The template and locale payloads still live in `veil_rule_store.py`, which
  is therefore a temporary compatibility/composition entry point. This is a
  real boundary improvement, not completion of the entire physical split.

### CI alignment

`.github/workflows/ci.yml` was updated to remove stale CLI invocation shapes
and to give the capture/classification surfaces their own syntax check. This
was needed because CI otherwise referenced obsolete `export-mirror` /
`--rules-dir` behavior.

### Line ending gate

`veil_rule_store.py` had mixed line endings which caused `git diff --check` to
report trailing whitespace and a blank EOF. After hunk ownership was recorded,
the file was normalized to LF without logic changes. Current result:

```text
git diff --check  -> pass (exit 0)
```

Git may still emit local `LF will be replaced by CRLF` advisory messages for
several files. They are not `git diff --check` failures. Do not “fix” them with
a repository-wide EOL rewrite.

## 7. Verification completed

All verification below used repository `workspace/audit/` as the test base;
no new `C:\\tmp` artifact was used.

```text
python -B -m pytest tests/test_db.py tests/test_locale.py -q \
  --basetemp workspace/audit/<run> -p no:cacheprovider
33 passed

python -B -m pytest tests -q \
  --basetemp workspace/audit/<run> -p no:cacheprovider
187 passed, 1 warning

git diff --check
pass
```

The warning is pytest's existing `cache_dir` configuration warning. Disable
the cache provider during these workspace-based runs because the pre-existing
`workspace/.pytest-cache` is access-denied in this environment.

## 8. Current state — not complete

The design-lock and Git-integrity subtask is now in a usable state. The VEIL
migration is **not** complete. The main remaining work, in order, is:

1. **Finish the M1 freshness contract.** Implement precise fingerprints and
   `OK/STALE/MISSING/ERROR` checks in `veil-status`, including nonzero exit for
   required non-OK distribution surfaces. Resolve the stale `C:\\tmp` target
   without recreating it.
2. **Define the exporter-owned HTML manifest.** Specify exact fields/input
   normalization, write it during export, and mark legacy HTML without it as
   `STALE`.
3. **Implement source-vs-installed Skill checks.** Byte fingerprints only;
   no embedded Skill manifest.
4. **Continue the physical M1/M2 extraction only where it improves an
   independently testable boundary.** The next likely move is the static HTML
   template and locale payloads from the compatibility/composition entry point.
   Do not split merely to make the file count smaller.
5. **Verify browser E2E locally and in remote Windows CI.** The local Edge
   run now passes capture preview, registration-request copy, manual fallback,
   and no direct browser write. Remote CI remains a release gate.
6. **Only then** regenerate HTML, reinstall/sync both Skills, run freshness
   checks, and make an intentional atomic migration commit.

Candidate 2 optionality, “keep current” behavior, and semantic-generation / a
referent table remain deferred UX work. Do not implement them while distribution
parity and freshness are unresolved.

## 9. Safe continuation commands

Use these as read/verification operations; do not stage or install as a
shortcut.

```powershell
rtk git status --short
rtk git diff --check
rtk python -B shared/runtime/veil-status.py --check
rtk python -B -m pytest tests -q --basetemp workspace/audit/<unique-run> -p no:cacheprovider
```

Before touching an implementation surface, inspect the corresponding tests and
the section in `docs/veil-design.md`. If adding test artifacts, place only
agent-created temporary material in a new unique `workspace/audit/<unique-run>`
directory. Do not delete existing inaccessible `workspace/tmp*` or
`workspace/.pytest-cache` entries: they were not created in this workstream.

## 10. Stop rules and handoff constraints

- Preserve all unrelated dirty worktree changes.
- Do not use `C:\\tmp` for VEIL work.
- Do not recreate the deleted stale sync target simply to make status green.
- Do not claim installed HTML or Skills are current without running the future
  fingerprint checks; current `veil-status` presence OK is insufficient.
- Do not run installer, sync, installed HTML generation, or commit before
  freshness, local browser E2E, and release-scope decisions are complete.
  A push for remote CI and later distribution still require explicit user
  authorization.
- Do not turn the proposal into implementation without a specific decision.
- When reporting status, distinguish: design-lock subtask complete; migration
  release incomplete; UX proposal deferred.

## 11. Explicit residual ambiguities and unrun checks

These are not omissions to be silently resolved by the next session; they are
known boundaries that require the stated follow-up work.

1. **Current status exit behavior is unsafe for freshness.** Directly on
   2026-07-20, `python -B shared/runtime/veil-status.py --check` printed the
   missing `C:\\tmp\\veil_behavior_target.md` as `[WARN]` and exited **0**.
   Its current implementation only makes `ERROR` nonzero. The new freshness
   contract must replace this for required delivery members; do not infer a
   healthy installation from the current zero exit.
2. **The normal-loop wording and migration detail are distinct.** Sections 1
   and 7 of `docs/veil-design.md` retain the normal operational shorthand
   `capture -> normalize -> sync -> lint`. The extended internal sequence in
   this handover (`classify -> normalize -> record -> export HTML -> sync ->
   lint`) describes migration/delivery implementation detail, not a competing
   user-facing main route. Preserve that distinction when consolidating the
   temporary migration section at lock exit.
3. **Renderer extraction is not a completed physical split.** The new M2
   renderer has no SQLite dependency, but `veil_rule_store.py` still holds the
   template/locales and invokes it as a compatibility composition entry point.
   A future change must prove a cleaner independent boundary before claiming
   separate M1/M2 release units.
4. **No remote CI was run.** Local tests, `git diff --check`, and the new
   Edge E2E pass as updated in section 12. No GitHub Actions run, install,
   sync, or installed-output refresh was performed; those remain explicit
   release operations, not implicit passes.

## 12. 2026-07-21 continuation update

The P0 audit was reopened because the unique-basetemp change to `pytest.ini`
was not recorded in the classification ledger. The ledger is now re-audited at
26 tracked modified files and 95 untracked files, with `pytest.ini` explicitly
owned by M1.

The temporary M1/M2 mixed implementation boundary was physically improved:

- `shared/tools/veil_rule_store.py` now owns canonical/profile operations and
  the protected export composition entry.
- `shared/tools/veil_html_assets.py` owns review-template loading, locale UI
  payloads, and locale selection.
- `shared/tools/veil_review_template.html` owns the static HTML/CSS/JavaScript.
- `shared/tools/veil_html_review.py` remains the pure review-row renderer.
- status and tests import HTML freshness inputs from the M2 asset module rather
  than treating the DB store as the UI owner.

A dependency-free browser E2E runner was added at
`tests/browser_e2e_runner.py` and wired into Windows CI. Local Edge headless E2E
passed with one capture result, successful form loading, successful
registration-request copy, successful manual fallback after clipboard denial,
and zero direct browser-write attempts.

Current local evidence: 192 source tests pass in bounded groups and
`git diff --check` passes. The live canonical DB and target registry are `OK`,
while installed `veil.html` and both installed capture Skills remain `STALE`.
No staging, commit, generated installed-output refresh, install, sync, or remote
CI operation was performed. Remote Windows CI, atomic release-scope review, and
explicit distribution authorization remain required.

## 13. 2026-07-21 exclusion-first audit reopening

The later exclusion-first implementation was externally audited before Git or
installation. Its prior source-complete claim is withdrawn.

Confirmed blockers in the live worktree:

- `Use "decision boundary" consistently.` and `Use the phrase decision
  boundary consistently.` produce zero exceptions.
- `Register current state as present state in VEIL.` and `Change current state
  to present condition.` resolve the existing source term as
  `existing-match`, hiding the requested change.
- `tests/browser_e2e_runner.py --json` fails with `capture_count=0`,
  `form_loaded=false`, and `success_copy=false`; pytest does not execute this
  runner, while Windows CI does.
- The 100 tuned cases are development regression data, not an independent
  holdout. Required reviewer, impact, reason, source-class, and second-review
  metadata are absent.
- At this audit point, the UX automation matrix had not been approved. This
  historical blocker is superseded by the explicit approval recorded in
  section 14.

Git release, install, sync, and installed-output refresh remain blocked. The
required order is: complete path/hunk classification, repair outcome intent
precedence, align Skill/HTML structured multi-result behavior, reclassify the
development corpus, freeze a separately reviewed holdout, update and run the
formal browser E2E, reproduce the historical 64-second timeout with its exact
command, then run all gates in one source state and re-audit.

## 14. 2026-07-21 remediation result after the external audit

The defects recorded in section 13 were reproduced before repair. Current
source behavior now differs as follows:

- quoted English requests, `the phrase`, explicit register/change mappings,
  Japanese change requests, and registered-term conflicts become one
  `exception` decision instead of being hidden as `existing-match`;
- plain use of an unchanged registered term remains `existing-match` with no
  question;
- HTML copies one combined **AI review** request, preserves requested preferred
  forms, asks AI to propose only missing forms, and never claims the copy action
  saved anything;
- the Skills pass accepted terms as data in one JSON file and require an atomic
  all-or-nothing batch result; no conversation text is placed in a shell
  command, and the temporary JSON is removed after result readback;
- registered sync targets carry a compact automatic task-close instruction, so
  a normal session needs no user launch, no question, and no VEIL-specific
  output; the manual command and HTML remain on-demand review/recovery routes;
- the formal Edge runner passes zero-decision, existing-match, two exceptions,
  locale switching, explicit change/fine-tuning, both clipboard paths, and zero
  direct browser writes.

The historical 64-second concern is not a SQLite deadlock. The exact recorded
group was `tests/test_db.py tests/test_status.py`: it formerly completed 35
tests in 62.38 seconds. Current isolated reproductions completed 37 tests in
31.58 seconds, while another DB-only run varied from 68.15 seconds to 20.51
seconds. The tests invoke the Python CLI in many child processes (`db_cmd`
appears 44 times in `test_db.py` and 11 times in `test_status.py`), so a 64
second outer command ceiling is unsafe on a contended Windows host. No current
single test exceeded 2.44 seconds in the exact DB/status reproduction.

Same-source local gates after remediation:

```text
pytest: 248 passed in 70.23 seconds
formal Edge Browser E2E: pass
capture syntax check: pass
git diff --check: pass
```

The tuned 100 cases remain development regression data. The separate
`20260721-independent-holdout-protocol.md` defines the required provenance,
two-reviewer metadata, freeze hash, and first-run boundary, but no independent
holdout has yet been authored or frozen. The automation matrix was explicitly
approved and fixed on 2026-07-21; two independent reviewer agents were then
authorized for holdout authoring and second review. Remote CI, Git release,
install, sync, and installed
output refresh remain blocked; current read-only status is DB `OK`, target
registry/registered target `OK`, installed HTML `STALE`, and both installed
Skills `STALE`.

## 15. 2026-07-21 independent holdout v1 and root remediation

Reviewer A authored 40 synthetic cases across 30 sessions without reading the
implementation, tests, fixtures, or prior results. Reviewer B independently
reviewed all 40 cases, agreed on all labels, and froze the corpus before VEIL
runtime execution. The frozen set has 20 ordinary sessions and 10 sessions
with exactly two exceptions. Its corpus SHA-256 is
`fed332f11931e3b541fcf9f895887727c00b1268ea125686774e36e318ed195b`.
The separate freeze attestation binds the corpus, manifest, approved matrix,
protocol, tracked diff, and exact 26-path runtime scope, including untracked
source.

The first evaluator preflight correctly stopped before runtime because the
evaluator had assumed one shared context per session. After that evaluator-only
assumption was corrected, the manifest-recorded first runtime attempt failed at
Python module import; its error result and unchanged DB fingerprints were
preserved. A separately recorded recovery run then evaluated the frozen source
and **failed**:

```text
exact outcomes: 18 / 40
exception outcomes: 3 / 20
high-impact false exclusions: 6
exclusion precision: 36.67%
existing-match precision: 100%
ordinary/exception question-count gates: failed
canonical DB/WAL/SHM changed: no
```

This result invalidated the prior usability inference and identified root
classes rather than isolated fixture misses: quoted registration syntax was too
narrow; natural preferred-form changes and conflicts were missed; high-impact
definition cues were incomplete; repetition relied only on literal token
counts; and descriptive Japanese `呼んでいます` could be mistaken for an
instruction. The implementation now separates descriptive repetition from
intent, supports broader English/Japanese registration/change forms, treats
source and `requested_preferred` as one mapping, and keeps proper-name prose
silent. The HTML analyzer was updated to the same contract, with parity tests
covering the new forms.

A v1 **development-only** rerun after the fixes reached 40/40, 100% exclusion
and existing-match precision, correct 20 zero-question and 10 one-question
sessions, zero high-impact false exclusions, zero unexpected exception terms,
and unchanged canonical files. It is not release evidence because the v1 cases
were already seen and the runtime scope changed after freeze.

Current same-source regression evidence superseding section 14:

```text
pytest: 253 passed in 152.48 seconds
formal Edge Browser E2E: pass
git diff --check: pass
```

One subsequent Edge invocation hit only the runner's fixed 30-second process
timeout; an immediate retry passed all assertions. Because the successful run
itself took more than 30 seconds end-to-end on the contended host, the formal
runner timeout is now 60 seconds. Syntax, E2E, and `git diff --check` pass after
that operational-reliability adjustment.

The protocol now also rejects unreviewed exception terms hidden inside one
combined question and defines multi-context session evaluation. A newly
authored, independently reviewed, pre-runtime-frozen **v2** is the next local
release gate. Remote CI, Git release, install, sync, and installed-output
refresh remain blocked; installed HTML and both installed Skills remain
`STALE` until a later explicitly authorized distribution step.

## 16. 2026-07-21 independent holdout v2 failure and root remediation

Reviewer A created a completely new v2 without reading v1, implementation,
tests, fixtures, evaluator, or prior results. Reviewer B independently reviewed
all 40 cases, agreed on all labels, verified that every exception session
enumerated exactly two durable terms, then froze and attested the set before
VEIL runtime execution. The set again contains 40 cases / 30 sessions: 20
ordinary sessions and 10 sessions with exactly two exceptions. Its frozen
corpus SHA-256 is
`1965c56e78101f479d3d17d0aaec4f979981f75113cf454054266ef341a1d93d`.

The preserved first run under
`workspace/audit/20260721-independent-holdout-v2/results/first-run/` **failed**
while every frozen input, source identity, evaluator identity, and canonical
DB/WAL/SHM fingerprint remained unchanged:

```text
exact outcomes: 26 / 40
exception outcomes: 9 / 20
high-impact false exclusions: 7
exclusion precision: 52.17%
existing-match precision: 100%
ordinary-session zero-question gate: pass
exception-session one-question gate: fail
unexpected-exception gate: fail
canonical DB/WAL/SHM changed: no
```

All 14 mismatches were enumerated before implementation changes. They reduced
to four shared causes: quoted terms lost their sentence-level intent after
masking; quoted meta labels could become false terms; durable inventory or
definition scope in a preceding sentence was ignored; and descriptive
repetition / one-off definitions had incomplete English/Japanese extraction.
The fix does not add per-term exceptions. It creates one quote-centered intent
path that evaluates explicit persistence, complete inventory, conflict,
durable definition, descriptive repetition, temporary scope, and directed
negation for each quoted term, with the same implementation in Python and the
HTML runtime.

The evaluator also had an operational contract bug: it required the frozen
first-run command string during a declared `--development-rerun-of`, making the
documented development rerun impossible. Exact command equality now applies to
the first run; recovery/development runs remain bound by corpus/manifest
identity, prior-result eligibility, source-state reporting, no-overwrite, and
canonical before/after fingerprints.

The post-fix v2 development run under `results/development-2/` passes 40/40,
with 100% exclusion and existing-match precision, zero high-impact false
exclusions, zero unexpected exception terms, 20 ordinary sessions with zero
questions, and 10 exception sessions with one combined question. It is
explicitly **not release evidence** because v2 was visible before source
behavior changed.

Current same-source regression evidence:

```text
focused Python/HTML outcome tests: 41 passed
full pytest from unique workspace/audit basetemp: 257 passed in 132.21 seconds
formal Edge Browser E2E: pass (all assertions, no direct writes)
Python syntax checks: pass
git diff --check: pass
```

One discarded full-suite attempt used `workspace/.tmp/` rather than the
project-approved `workspace/audit/` shelf. That basetemp directory disappeared
after 175 tests and produced 82 identical `FileNotFoundError` setup errors.
No test code that removes `workspace/.tmp/` was found, and the immediately
repeated full run on the governed audit shelf passed all 257 tests. This is not
a product/SQLite regression and does not replace the section 14 diagnosis of
the historical 64-second outer timeout.

A newly authored, independently reviewed, pre-runtime-frozen **v3** is now the
remaining local UX evidence gate. The already approved automation matrix stays
unchanged. Remote CI, Git release, install, sync, and installed-output refresh
remain blocked; installed HTML and both installed Skills remain `STALE`.

## 17. 2026-07-21 independent holdout v3 and architecture decision

Reviewer A authored a new 40-case / 30-session v3 without reading earlier
holdouts, implementation, tests, fixtures, evaluator, or results. Reviewer B
reviewed every case, agreed 40/40 with no material ambiguity, verified every
two-exception inventory, and froze the corpus. The original v3 command stopped
at preflight before importing VEIL because Reviewer B used semantically
equivalent but evaluator-incompatible manifest key names. That failure is
preserved under `results/preflight-1/preflight-failure.json`.

The original corpus, labels, review, manifest, and attestation were not edited.
Because no runtime had seen a case, Reviewer B created `recovery-1/` as a
mechanical schema recovery with a byte-identical corpus. All source, plan,
protocol, evaluator, and canonical identities were re-attested before the
eligible first runtime execution.

The eligible v3 run **failed**:

```text
exact outcomes: 26 / 40
exception outcomes: 10 / 20
high-impact false exclusions: 3
exclusion precision: 57.89%
existing-match precision: 100%
ordinary-session zero-question gate: fail
exception-session one-question gate: fail
unexpected-exception gate: fail
canonical DB/WAL/SHM changed: no
frozen inputs/source/evaluator changed: no
```

The 14 mismatches again crossed wording families: durable register requests,
preferred-form changes, conflicts, durable definitions, descriptive repetition,
temporary definitions, and explicit negation. It also exposed token-boundary
failures: `Record ... in quota_probe_ms` became a registration request, and an
apostrophe inside `person's` was interpreted as a quote delimiter. This is not
a missing-phrase-list problem.

No post-v3 regex or cue patch is allowed. The architecture decision is recorded
in `docs/governance/20260721-semantic-decision-frame-redesign.md`:

- the host AI performs evidence-backed semantic decision extraction plus a
  second background critic pass;
- local VEIL validates exact evidence and applies deterministic outcome policy;
- local code retains all DB/write authority and performs no write before one
  accepted combined exception result;
- raw-text regex outcomes become a diagnostic/fallback, not production evidence
  that arbitrary conversation intent was understood;
- a new unseen synthetic end-to-end holdout is allowed only after the redesign
  is implemented and development-tested;
- even a synthetic pass does not prove overall UX; approved anonymized real
  conversation evaluation remains a separate later gate.

Git release, remote CI, install, sync, installed-output refresh, and current
`STALE` remediation remain blocked.

## 18. 2026-07-21 independent semantic holdout v4 pass

After the contract-v2 semantic redesign was implemented and development-tested,
Reviewer A authored a new synthetic 40-case / 30-session v4 without access to
the implementation, tests, earlier holdouts, or their results. Reviewer B
reviewed all 40 rows and recorded 40 agreements, zero disagreements, and zero
ambiguities. The reviewed blind runtime input remained byte-identical to the
author version. No real conversation was used.

The freeze fixed the reviewed corpus, blind input, protocol, automation matrix,
evaluator, 32-path source inventory, `HEAD`, and tracked diff before the host AI
saw labels. The host AI read only the blind runtime input and current
Skill/schema, then wrote one extractor-plus-critic contract-v2 payload per
session. The eligible first run under
`workspace/audit/20260721-independent-semantic-holdout-v4/frozen/results/first-run/`
passed:

```text
exact outcomes: 40 / 40
ordinary sessions: 20 / 20 with zero questions
two-exception sessions: 10 / 10 with one combined question
high-impact false exclusions: 0
exclusion precision: 100%
existing-match precision: 100%
unexpected exception terms: 0
contract validation errors: 0
raw-text fallback count: 0
canonical DB access: no
frozen source identity changed: no
```

The frozen manifest SHA-256 is
`79eec034e78799f75eb8eab2582b055322e0c54483e3bc8567e83a8fb0bce2a7`;
the attestation SHA-256 is
`5fa397b962323d2014c5e85854b4c84afede86332258b1b3dcf5372ff9717ecb`;
the generated-frame artifact SHA-256 is
`368fa30c6740f5a89d51a30df30eef7e506631cbd78d75a45217632c861f2f80`.
Both failed raw-text holdouts and their development reruns remain preserved and
retain their original evidentiary status.

The same frozen source subsequently passed all 276 pytest cases in 79.46
seconds, the formal local Edge E2E, Python syntax checks, and
`git diff --check`. A live read-only delivery check still reports DB, target
registry, and the registered target `OK`; installed HTML and both installed
Skills remain `STALE`. No install, installed-output generation, sync, staging,
commit, push, or remote CI was performed.

This v4 pass establishes the approved automation boundary on a new independent
synthetic set. It does **not** establish overall real-conversation UX. Before
reading real conversations, the user must separately approve the conversation
scope, anonymization, retention, and two-reviewer handling. After that evidence,
remote Windows CI, final M1/M2 scope review, and separately authorized
distribution remain release gates.
