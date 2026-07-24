# VEIL v9 G6 integrity implementation design

**Status:** complete. I1--I4 verification passed and I5 created the one v9
input-fixed package. This document replaced the unaccepted G6-v9 prototype;
the resulting package is immutable.

## Scope and fixed boundary

G6 converts the already merged G5-v9 corpus into one verifier-backed input
package. It does not generate frames, call the canonical DB, run a scorer, or
create a result directory. The only irreversible action is the final rename to
`workspace/audit/20260722-real-conversation-ux-v9/frozen/`; it is prohibited
until every implementation and verification gate in this document passes.

G4-v9 source eligibility and G5-v9 independent review remain valid. The
master contract remains
`20260722-real-conversation-v9-completion-design.md`; its exact artifact
schemas and G7--G9 rules are unchanged. This document defines how G6 must make
those schemas executable.

## Deliverables, ownership, and ordering

| Unit | Owned files | Completion fact | May not do |
| --- | --- | --- | --- |
| I1 integrity model | `v9/holdout_integrity.py`, focused tests | strict read/write/verify APIs pass isolated fixtures | create `frozen/` |
| I2 freeze CLI | `v9/freeze_real_holdout.py`, focused tests | CLI resolves only declared v9 paths | invoke it on the real reviewed corpus |
| I3 evaluator adapter | `v9/evaluate_real_holdout.py`, focused tests | v4 core is callable only behind v9 preflight and access hooks | score a real v9 package |
| I4 integration verification | G6 test suite and static checks | all fixtures prove atomicity and failure taxonomy | create real `frozen/` |
| I5 one input fixed package | `v9/frozen/` once | read-only verifier accepts it with no generated output | retry, modify, or replace it |

I1 -> I2 -> I3 -> I4 -> I5 is mandatory. The current unaccepted files are
I1/I2/I3 prototypes only; they must be replaced or deleted from the G6 source
inventory before I4. A prototype is not evidence of any completed unit.

## I1: integrity model contract

The module exposes only these public operations:

1. `build_input_package(...)`: stages a package but never writes the final
   path until all validation completes.
2. `verify_input_package(...)`: validates an existing fixed package without
   creating files.
3. `validate_preflight(...)`: validates fixed input and generated payload
   before the evaluator reads a reviewed label or creates a result directory.
4. `compute_source_state(...)`: returns the exact tracked HEAD, tracked-diff
   digest, and ordered execution-source inventory specified by the master
   design.

Every JSON object is parsed with duplicate-key rejection. Manifest,
attestation, runtime row, record, alias, and nested policy object validation is
strict: missing, unknown, type-invalid, and value-invalid fields fail before
the next state transition. The exact schemas are those in the master design;
this module must not introduce aliases, optional fields, null placeholders, or
an alternative source-state shape.

`compute_source_state` receives an explicit, repository-relative ordered list.
It refuses a missing file, duplicate path, path outside the repository, or an
untracked/unlisted execution dependency. Its inventory digest is path UTF-8,
NUL, eight-byte length, raw bytes for each record in order. The tracked-diff
digest is the exact `git diff --binary` byte stream. Verification recomputes
both values and rejects change.

## I2: atomic input-package algorithm

The CLI has only `--reviewed-dir`, `--frozen-dir`, and an optional test-only
failure hook unavailable in normal invocation. All dependency paths are fixed
v9 paths in code and are added to the execution-source inventory.

1. Refuse existing final `frozen/`, generated output, or first-run result.
2. Validate the G5 merged corpus and canonical snapshot read-only.
3. Create a sibling unique staging directory.
4. Copy corpus and snapshot into staging; derive exactly one label-free runtime
   row per session.
5. Hash every fixed dependency and compute source state.
6. Write manifest, then attestation, and verify the staged package using the
   same read-only verifier used after finalization.
7. Confirm that generated output and result directory are absent.
8. Rename staging to final `frozen/` once.

Any exception removes staging, leaves final `frozen/` absent, and writes one
failure record outside the reserved final path containing stage, exception type,
message, and no label contents. No failure record makes the final package
retryable; I5 may start only after a newly authorized G6 recovery design.

## I3: evaluator adapter contract

The adapter owns v9 preflight and result-state handling. It may load the v4
scoring core only by explicit path recorded as `evaluator_core`; it does not
import v7/v8 evaluator or integrity modules.

Before labels are loaded it must verify: exact six option/value pairs, no
existing result directory, duplicate-key-safe manifest/attestation, every
record/alias/source-state value, three allowed generator inputs, generated
payload validity, and matching session set. Preflight failure writes only the
external `g8-v9-preflight-failure-record.json`; it never creates a result
directory.

After preflight it creates `runtime-started`, patches DB connection to increment
and deny `canonical_db_access_attempts`, patches raw-text fallback to increment
and deny `raw_text_fallback_attempts`, and invokes the core once. A post-start
exception produces exactly the terminal `runtime-error` manifest. A normal run
produces exactly the terminal scored manifest and summary from the master
design. The two access gates are calculated from counters, never literals.

## I4: required test evidence

Focused tests must cover all of the following before I5:

- missing, unknown, invalid-type, invalid-value, and inconsistent manifest or
  attestation fields, including every alias and repeated record;
- altered source file, source-state inventory, tracked diff, runtime row,
  reserved generated output, and reserved result directory;
- copy, hash, manifest, and attestation failure injection, each proving final
  `frozen/` is absent and one external failure record exists;
- one successful disposable package verified before and after atomic rename;
- preflight rejection before corpus-label loading and before result creation;
- DB and raw fallback denial with nonzero measured counters;
- injected post-start exception retained as `runtime-error`;
- one disposable fully scored fixture proving all ten gate fields are produced.

The full project test suite, Python compilation of all new v9 files, VEIL lint
for all edited Markdown, and a static check that includes untracked v9 files
must also pass. `git diff --check` alone is insufficient for untracked files.

## I5 entry checklist and stop rule

The operator records one checklist with exact commands and outputs for I1--I4.
Only a checklist with every item passing permits the CLI against the real G5
reviewed corpus. Immediately before that one invocation, verify the reviewed
hashes, source state, and absence of `frozen/`, generated output, and results.

If any I1--I4 condition is false, stop before I5 and revise implementation;
do not create a partial real package. If I5 fails after staging begins, preserve
the external failure record and return to a new recovery design rather than
retrying this package.
