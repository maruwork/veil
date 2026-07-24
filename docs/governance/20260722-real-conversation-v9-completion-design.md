# VEIL v9 completion design

**Status:** closed `requires-revision`. G4-v9 through G7-v9 completed their
one permitted artifacts. G8-v9 is a terminal adapter/core `runtime-error` and
G9-v9 closed that evidence; v9 has no scored classifier conclusion. The next
work is the v10 adapter/core compatibility recovery design; no v10 source,
review, input-fixed package, generation, or evaluation exists.

This document is the execution design for the v9 recovery line. The fixed
label policy remains the authority in
`20260721-real-conversation-v7-evaluation-contract.md`; the v7 blind-input
integrity contract supplies the baseline integrity obligations; and
`20260722-real-conversation-v9-generation-recovery-design.md` plus the v9
generator procedure supply v9 recovery-specific constraints. Where a v9-local
path, identifier, or schema is specified below, this document is the binding
selection. No v8 implementation file is an import source for v9.

## Objective and non-negotiable boundary

The objective is met only when one fresh v9 real-conversation holdout has a
valid two-reviewer corpus, an immutable verified input package, one valid blind
generation, one scored evaluation, and a G9 evidence close that states whether
the required gates passed. A closed failed first run is evidence completion,
not objective success.

v1-v8 are historical evidence. In particular, v8 frozen inputs and its one
invalid generated output are immutable and must never be repaired, rerun,
relabeled, or used as v9 source material. No current step authorizes a
canonical-DB write, sync, installation, Git mutation, remote action, or release.

## Immutable v9 execution order

`G4-v9 -> G5-v9 -> G6-v9 -> G7-v9 -> G8-v9 -> G9-v9`

G4-v9 is complete. The remaining stages may start only in this order. Each
stage has one owner, one bounded write surface, and an explicit stop outcome.
No later-stage artifact may be created early.

| Stage | Entry evidence | Only durable write | Stop outcome | Enables |
| --- | --- | --- | --- | --- |
| G5-v9 | G4 source record and fixed label contract | `v9/reviewed/` + validator | reviewer disagreement or invalid artifact; preserve it and revise review work | G6-v9 |
| G6-v9 | merged two-reviewer corpus | `v9/frozen/` once | atomic freeze failure; no final directory | G7-v9 |
| G7-v9 | frozen package verifies and output absent | `frozen/generated-frames.jsonl` once | invalid output; preserve it and block G8-v9 | G8-v9 |
| G8-v9 | frozen package + valid generated payload | a scored/runtime `frozen/results/first-run/` **or** the external preflight-failure record | preflight failure creates no result directory; runtime/score failure preserves its one result; neither is rerun | G9-v9 |
| G9-v9 | either a terminal first-run result or the named preflight-failure record | cause analysis, execution, handover | incomplete/inconsistent evidence; do not claim success | explicit next decision |

## G5-v9: independently reviewed corpus

The fixed outcome policy is
`docs/governance/20260721-real-conversation-v7-evaluation-contract.md`. It is
not amended by v9. The relevant source is exactly
`workspace/audit/20260722-real-conversation-ux-v9/input/anonymized-source.jsonl`.

1. Obtain the canonical snapshot through a read-only DB readback; store only
   normalized active terms in `reviewed/canonical-snapshot.json`.
2. Reviewer A writes `reviewer-a-corpus.jsonl` with exact context, one primary
   lexical target per normalized concept, exact evidence occurrences,
   matrix-derived outcome, provenance, and `second_review: "pending"`.
3. Reviewer B is isolated from A, every corpus/report artifact, all previous
   holdouts, source history, and evaluator/freeze files. B receives only the
   anonymized source, snapshot, fixed label contract, and a B assignment.
4. A v9-local `validate_reviewed_corpus.py` verifies source linkage, snapshot
   membership, evidence occurrence, frame shape, matrix outcome, distinct
   reviewer identities, and agreement on source, target, snapshot membership,
   and outcome. It may not require reuse of A's arbitrary case ID or confidence.
5. The merger alone writes `corpus.jsonl` and `review-report.json`, and only
   after all checks pass.

The only G5 work products are `reviewed/canonical-snapshot.json`,
`reviewed/reviewer-a-corpus.jsonl`, `reviewed/reviewer-b-verdict.jsonl`,
`reviewed/corpus.jsonl` (the mechanical merge), `reviewed/review-report.json`,
`validate_reviewed_corpus.py`, and its focused tests. Rejected reviewer
revisions and their rejection records are preserved supporting evidence under
`reviewed/rejected/`; they are never merger inputs.

`canonical-snapshot.json` has exactly `contract_version`, `read_at`, `source`,
and `normalized_active_terms`. `source` is exactly `read-only canonical DB
readback`; `normalized_active_terms` is a sorted, duplicate-free array of
nonempty normalized strings.

Every Reviewer-A and merged corpus line has exactly `contract_version`,
`case_id`, `session_id`, `context`, `term`, `registered_terms`,
`expected_outcome`, `impact`, `reason`, `source_class`, `reviewer`,
`second_review`, `provenance`, and `review_frame`. Every Reviewer-B line has
exactly `case_id`, `session_id`, `context`, `term`, `registered_terms`,
`review_frame`, `expected_outcome`, `reviewer`, `verdict`, and `reason`.

The Reviewer-A `reviewer` object has exactly `id: "reviewer-a-v9"` (or a
preserved revision suffix) and ISO-8601 `reviewed_at`; Reviewer-B is the same
shape with `id: "reviewer-b-v9"` (or its preserved revision suffix). Before
merge, `second_review` is exactly `"pending"`. In a merged line it is exactly
an object with `required: true`, Reviewer-B's `reviewer_id`,
`verdict: "agree"`, nonempty `reason`, and ISO-8601 `reviewed_at`. Both
reviewers must use `verdict: "agree"`; another verdict is disagreement, not a
mergeable corpus.

`provenance` has exactly `kind`, `scope_id`, and `contains_real_conversation`,
with values `anonymized-real-conversation`,
`20260722-real-conversation-ux-v9`, and `true`. `registered_terms` is exactly
`[term]` when that normalized term is in the snapshot and exactly `[]`
otherwise. `source_class` is exactly `anonymized-real-conversation`, and
`contract_version` is exactly `2`. `expected_outcome` is the fixed v7 matrix
outcome, never reviewer judgement.

`review_frame` has exactly `term`, `intent`, `persistence`, `polarity`,
`scope`, `impact`, `term_evidence`, `intent_evidence`, and `confidence`.
Allowed values are intent `mention|adopt|rename|define|conflict`, persistence
`none|temporary|durable|unclear`, polarity `affirmed|negated|reported`, scope
`one-off|session|project|global|unclear`, and impact/confidence
`low|medium|high`. Each evidence item has exactly nonempty `text` and integer
`occurrence >= 1`; `term_evidence` is one item and `intent_evidence` is a
nonempty list. The case term, registered state, frame, and outcome must all
agree with source and matrix.

The focused validator suite must prove acceptance of a valid independently
worded B review, and rejection of each of: missing or unknown field; duplicate
case or normalized term; invalid type/value/evidence; snapshot ordering or
membership mismatch; source/session/context/term/registered-state disagreement;
B's own invalid frame or matrix outcome; an A/B target or outcome disagreement;
and an attempted merge when a required output artifact already exists. The
report records exact input hashes, accepted/rejected counts, and output hash.

Reviewer disagreement, invalid JSON shape, or an incorrect matrix outcome is
retryable G5 supporting work. Preserve the rejected artifact and record why;
do not silently overwrite it or create a merged corpus from it. G5 completion
requires a machine-passed report, not an asserted agreement.

## G6-v9: v9-local atomic freeze contract

The executable G6 implementation design is
`20260722-real-conversation-v9-g6-integrity-implementation-design.md`. Its I1
through I5 order and I5 entry checklist are mandatory. No current G6 prototype
is accepted as a G6 result.

Before any real freeze, implement and test these v9-local files:

- `workspace/audit/20260722-real-conversation-ux-v9/holdout_integrity.py`;
- `workspace/audit/20260722-real-conversation-ux-v9/freeze_real_holdout.py`;
- `workspace/audit/20260722-real-conversation-ux-v9/evaluate_real_holdout.py`.

They must not import v8 integrity or evaluator code. The v4 scorer may be
used only as an explicitly recorded `evaluator_core` dependency, while every
v9 wrapper, integrity module, payload validator, schema source, normalization
source, and imported scoring source is in the ordered execution-source
inventory.

The manifest and attestation must use strict exact top-level field sets and
repeat every path/SHA-256/byte record. The register is:

`generator_procedure`, `semantic_frame_schema`, `runtime_input`,
`reviewed_corpus`, `canonical_snapshot`, `approved_evaluation_matrix`,
`evaluator_wrapper`, `evaluator_core`, `normalization_source`, and
`payload_validator`.

A file record is exactly `{path, sha256, bytes}`: repository-relative POSIX
path, lowercase hexadecimal SHA-256, and exact nonnegative byte count.
`frozen-manifest.json` has exactly `contract_version`, `holdout_id`, `status`,
`created_at`, `frozen_at`, `first_runtime_execution_at`, every dependency
register identifier above, `corpus`, `evaluator`, `protocol`,
`approved_matrix`, `evaluator_args`, `host_generation`, `blind_output`,
`source_state`, and `artifact_policy`. `freeze-attestation.json` has exactly
`contract_version`, `holdout_id`, `attested_at`, `first_runtime_execution_at`,
every dependency-register identifier, `corpus`, `evaluator`, `protocol`,
`approved_matrix`, `manifest`, `source_state`, and
`pre_runtime_confirmation`.

The mandatory aliases are byte-for-byte equal to their register counterparts:
`corpus=reviewed_corpus`, `evaluator=evaluator_wrapper`,
`protocol=generator_procedure`, and
`approved_matrix=approved_evaluation_matrix`. `manifest` is the record for
`frozen-manifest.json`. `holdout_id` is
`20260722-real-conversation-ux-v9`, `status` is `frozen`, and both
`first_runtime_execution_at` values are JSON null before G8.

`evaluator_args` is the six option/value pairs, in this exact order:
`--corpus`, frozen corpus path; `--runtime-input`, runtime-input path;
`--generated-frames`, reserved generated-output path; `--manifest`, manifest
path; `--attestation`, attestation path; `--result-dir`, reserved first-run
result path. `blind_output` has exactly `path` and `outer_fields`, the latter
being exactly `["payload", "session_id"]`. `host_generation` records only the
authorized host command identity and its input hashes; it cannot contain corpus
labels. `artifact_policy` states immutable frozen inputs, one
generated-output attempt, and one evaluation attempt.
`pre_runtime_confirmation` has exactly `review_complete: true`,
`runtime_has_seen_cases: false`, `generated_frames_exist: false`, and
`frozen_inputs_will_not_be_modified: true`.

`source_state` has exactly `head`, `tracked_diff_sha256`, and
`execution_source_inventory`; the inventory has exactly `sha256`, `bytes`, and
`records`. Its ordered records are each `{path, sha256, bytes}` and its digest
uses each path's UTF-8 bytes, a NUL, eight-byte length, and raw bytes in order.
This makes the wrapper, core, validator, freeze tool, procedure, and tests part
of the immutable execution surface.

The freeze tool copies the merged corpus and canonical snapshot into staging,
derives one label-free runtime row per session, records every dependency,
writes manifest/attestation, self-validates the staged package, and then does
one rename to `frozen/`. It reserves but does not create the generated output
or first-run result directory.

Every `runtime-input.jsonl` row has exactly `session_id`, `source_text`, and
`registered_terms`; its session and source text must be copied from the merged
corpus, and `registered_terms` must be the common reviewed value for that
session. It contains no `term`, expected outcome, review frame, reason,
reviewer, or other label-bearing field. There is exactly one row per reviewed
session, in ascending session-id order.

Regression tests must inject failures during corpus copy, snapshot copy, hash,
manifest, and attestation work. Every failure must leave no final `frozen/`
directory and retain a separate failure record outside the reserved final path.
They must also reject every missing, unknown, or type-invalid top-level
manifest/attestation field; altered repeated record; alias mismatch; invalid
runtime row; non-null pre-runtime execution timestamp; existing generated
output; and existing first-run directory. A successful freeze is followed by a
read-only verifier run with generated output absent.

Because source-state hashes the complete tracked diff, all tracked edits needed
for G6-G8 must be complete before the one freeze. Do not alter tracked state
between the successful G6 freeze and G8 scoring. This restriction prevents an
unrelated documentation change from invalidating the frozen package.

## G7-v9: one blind generation

Immediately before delegation, the host runs the v9 frozen-input verifier with
`expect_generated=False`, verifies source state, and confirms that both the
reserved output and `results/first-run/` are absent.

The isolated generator reads exactly three frozen-recorded inputs:

1. v9 generator procedure;
2. semantic-frame schema; and
3. label-free runtime input.

It writes only `frozen/generated-frames.jsonl` once. The v9 procedure's
contiguous-substring and Unicode self-check applies to every term and intent
evidence string. The host then runs the v9 payload validator plus the frozen
input verifier with `expect_generated=True` before any reviewer label is read.

If either check fails, G7-v9 is fixed failure evidence. Do not regenerate,
evaluate, alter frozen inputs, or use this package for a second attempt.

## G8-v9: one preflighted evaluation

The exact CLI suffix is created by G6 and stored verbatim in the manifest:

`--corpus`, `--runtime-input`, `--generated-frames`, `--manifest`,
`--attestation`, `--result-dir`.

The v9 evaluator wrapper accepts only that exact suffix and performs this order
before it parses `expected_outcome` or creates `results/first-run/`:

1. resolve all paths under the repository root and reject an existing result;
2. parse manifest/attestation with duplicate-key rejection and strict field sets;
3. verify every repeated register record, path, SHA-256, byte count, alias,
   manifest binding, and source-state inventory;
4. require the v9 procedure's exact three blind inputs and the reserved output
   session set; and
5. invoke `validate_generated_payloads` against runtime input and generated
   output, including ASCII-only output and exact Unicode evidence.

Only then may it create `results/first-run/`, write `runtime-started`, read the
frozen corpus labels, and score. The wrapper fail-closes canonical DB access
and raw-text fallback with measured counters. The wrapper is v9-local. It may
call the frozen v4 scoring core only through an explicit adapter that sets the
core project root to v9, replaces its `compute_source_state` function with the
v9 verifier, and supplies v9 runtime-access counters. It must not import v8
files or inherit mutable v8 paths.

The adapter wraps the canonical DB connection entry point so any attempt
increments `canonical_db_access_attempts` and raises before connection. It
wraps the raw-text fallback entry point so any attempt increments
`raw_text_fallback_attempts` and raises. The wrapper derives
`no_canonical_db_access` and `zero_raw_text_fallback` from these measured
counters; it may never write either gate as a fixed literal.

After successful preflight, the wrapper creates
`frozen/results/first-run/result-manifest.json`. The transient
`runtime-started` object has exactly `contract_version`, `holdout_id`, `status`,
`started_at`, `frozen_manifest`, `freeze_attestation`, `generated_frames`,
`source_state_before`, and `runtime_access`; `runtime_access` has exactly
`canonical_db_access_attempts` and `raw_text_fallback_attempts`.

The terminal scored object has exactly `contract_version`, `holdout_id`,
`status`, `started_at`, `completed_at`, `frozen_manifest`,
`freeze_attestation`, `generated_frames`, `source_state_before`,
`source_state_after`, `runtime_access`, `case_results`, `summary`, and `gates`.
The terminal runtime-error object has exactly `contract_version`, `holdout_id`,
`status`, `started_at`, `completed_at`, `frozen_manifest`,
`freeze_attestation`, `generated_frames`, `source_state_before`,
`runtime_access`, and `runtime_error`; `runtime_error` has exactly `type` and
`message`. Every named artifact field is a file record. `status` is exactly
`scored` for the former and `runtime-error` for the latter.

The summary has exactly `holdout_id`, `status`, `case_count`,
`exact_case_count`, `session_count`, `validation_error_session_count`,
`high_impact_false_exclusion_count`, `question_mismatch_session_count`,
`unexpected_exception_count`, `exclusion_precision`,
`existing_match_precision`, `gates`, and `sessions`. A preflight failure
creates neither the result directory nor any frozen-directory write.

On a preflight failure, the host writes exactly one external record:
`workspace/audit/20260721-real-conversation-ux-v6/g8-v9-preflight-failure-record.json`.
It has exactly `schema_version`, `status`, `occurred_at`, `holdout_id`,
`command_args`, `failed_stage`, `error_type`, `error`, `frozen_manifest`,
`freeze_attestation`, `generated_frames`, `result_dir_exists`, `labels_read`,
`canonical_db_access_attempts`, and `raw_text_fallback_attempts`; its status is
`preflight-failed`, `result_dir_exists` is false, and the three access/read
counts are zero. It records the original failure and does not make the frozen
package retryable.

The scored result succeeds only if every summary gate is true:

- `all_case_outcomes_exact`;
- `zero_high_impact_false_exclusions`;
- `exclusion_precision_at_least_0_99`;
- `existing_match_precision_at_least_0_99`;
- `all_question_counts_exact`;
- `zero_unexpected_exception_terms`;
- `zero_contract_validation_errors`;
- `zero_raw_text_fallback`;
- `no_canonical_db_access`; and
- `source_state_unchanged`.

A runtime or scored failure is the only first-run result for that package. A
preflight failure instead has the external failure record above; it is still
terminal for that package and not rerunnable. In either case, diagnosis does
not authorize a second attempt.

Focused wrapper tests must prove: label data is unread on every preflight
failure; a DB or raw-fallback attempt increments its counter and fails; gate
values follow actual counters; a complete scored fixture creates the exact
result record; and an injected post-runtime exception is retained as
`runtime-error`. They must additionally prove all ten gates, including source
state unchanged, are produced from measured runtime and post-run verification.

## G9-v9: evidence close and decision

G9 reads either the immutable terminal first-run result or the immutable
external preflight-failure record and writes only closing analysis and state
records. It separately states:

1. frozen procedure/input validity;
2. generated payload validity;
3. score and every gate value;
4. expected versus actual outcome and question-count behavior;
5. canonical-DB/raw-fallback measurements; and
6. remaining risk and next authorized action.

The parent objective is **achieved** only when G8 has a complete first-run
result, every one of the ten listed gates is true, source state is unchanged
through scoring, and G9 records that conclusion without qualification. If G8
has the preflight-failure record, or if any generation, runtime, or scoring
condition fails, G9 closes the evidence as a failure and names the smallest
corrective design/implementation task; it does not claim objective success.

## Acceptance before execution

G5-v9 may begin now. G6-v9's one irreversible freeze may occur only after the
G5 merger, v9-local freeze/evaluator implementation, focused regression tests,
full test suite, static checks that explicitly include untracked source, and
this design's source-state rule are all satisfied. G7-v9 and G8-v9 may start
only from their respective immutable predecessor artifacts.
