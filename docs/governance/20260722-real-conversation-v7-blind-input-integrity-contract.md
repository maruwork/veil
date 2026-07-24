# VEIL next real-conversation holdout: blind-input integrity contract

**Status:** G2 complete. This contract defines the freeze and evaluator
preflight required for the next real-conversation holdout. It does not create
a source row, reviewed corpus, frozen directory, blind output, or evaluation
result, and it does not authorize runtime, DB, sync, install, Git, remote, or
release actions.

## Authority and non-negotiable boundary

This contract extends the reviewed-label contract at
`docs/governance/20260721-real-conversation-v7-evaluation-contract.md`. It
does not change the contract-v2 outcome policy.

The v6 first run remains immutable evidence. Its failure showed that a
plausible manifest is insufficient when it does not freeze the procedure
actually supplied to the blind generator. The next holdout is valid only if
every party can prove which inputs it was allowed to use and which input bytes
the evaluator checked before it interpreted expected labels.

All recorded paths are project-relative POSIX paths. Every file record is
exactly:

```json
{"path": "relative/path", "sha256": "lowercase-hex", "bytes": 123}
```

`sha256` is the SHA-256 of the file's raw bytes, and `bytes` is its raw byte
length. A path must resolve inside the project root to a regular file. Duplicate
record IDs or duplicate normalized paths are invalid.

## Frozen input register

The freeze tool owns creation of all records below. The manifest and the
attestation must each contain a full path/hash/bytes record for every entry in
this table, except that the manifest itself is recorded only by the attestation
to avoid a circular hash.

| Record ID | Frozen artifact | Owner | Blind generator may read | Evaluator verifies before labels |
| --- | --- | --- | --- | --- |
| `generator_procedure` | dedicated v7 blind-generation procedure | evaluation owner | yes | yes |
| `semantic_frame_schema` | `shared/tools/veil_decision_frames.py` | runtime owner | yes | yes |
| `runtime_input` | frozen label-free session JSONL | freeze tool | yes | yes |
| `reviewed_corpus` | frozen reviewed corpus with expected labels | reviewers then freeze tool | no | yes, bytes only before labels |
| `canonical_snapshot` | read-only normalized canonical-term snapshot | review owner then freeze tool | no | yes |
| `approved_evaluation_matrix` | v7 reviewed-label contract | evaluation owner | no | yes |
| `evaluator_wrapper` | next-holdout evaluator entry point | evaluation owner | no | yes |
| `evaluator_core` | scorer/preflight implementation invoked by wrapper | evaluation owner | no | yes |
| `normalization_source` | `shared/tools/veil_rule_store.py` used by scoring | runtime owner | no | yes |
| `execution_source_inventory` | ordered records of every repository source imported by the evaluator or needed to validate contract-v2 frames | freeze tool | no | yes, as an aggregate hash and per-file records |

The next v7 generator procedure must name only the three permitted blind reads
in this table: `generator_procedure`, `semantic_frame_schema`, and
`runtime_input`. It may write only the reserved output path
`frozen/generated-frames.jsonl`. It must not read the reviewed corpus, review
reports, expected labels, canonical snapshot, evaluation matrix, evaluator
sources, prior holdouts, DB, raw source material, or any unrecorded artifact.

The blind output is not a frozen input and cannot have a pre-generation hash.
The manifest reserves its project-relative path and requires the public outer
JSONL envelope (`session_id` copied verbatim and `payload` only). The evaluator
hashes that output into its first-run result manifest after successful
preflight, before expected labels are interpreted.

## Manifest and attestation shape

The manifest has these required top-level members in addition to the register:

```text
contract_version, holdout_id, status, created_at, frozen_at,
first_runtime_execution_at, evaluator_args, blind_output,
source_state, artifact_policy
```

Requirements:

1. `contract_version` is the current contract-v2 payload version; `status` is
   `frozen`; and `first_runtime_execution_at` is `null` before evaluation.
2. `evaluator_args` is the sole permitted invocation suffix, including the
   reserved `results/first-run` path. A pre-existing result directory is an
   error.
3. `blind_output` has the reserved path, exact outer-envelope field set, and
   one-output-row-per-runtime-session requirement. It does not claim a hash
   before generation.
4. `source_state` records the Git head, tracked-diff SHA-256, and the ordered
   `execution_source_inventory`. The inventory hash is calculated from each
   normalized path, a NUL separator, byte length, and raw bytes, in order.
5. The manifest must record `reviewed_corpus` as the frozen copy that the
   evaluator will score, not merely the mutable reviewer work file.

The attestation repeats every register record verbatim, including `path`. It
also contains `manifest` as a path/hash/bytes record, the holdout ID, the same
`first_runtime_execution_at`, and pre-runtime confirmations that review is
complete, runtime has not seen cases, generated frames do not yet exist, and
frozen inputs will not be modified. It must not omit a path merely because the
manifest already has one.

Because the manifest cannot hash its own attestation without a circular
dependency, the evaluator treats the attestation's `manifest` record as the
one-way binding: its path must be the invoked manifest and its hash/byte count
must equal that file. The evaluator then requires every repeated register
record and source-state record to be byte-for-byte equal between manifest and
attestation.

## Evaluator preflight: required order

The next evaluator must perform these steps before parsing or interpreting any
expected label from `reviewed_corpus` and before creating
`results/first-run/`.

1. Resolve every CLI path under the project root. Reject a non-exact argument
   sequence, a pre-existing result directory, an absent file, or a path outside
   the root.
2. Parse manifest and attestation with duplicate-key rejection. Require the
   expected top-level field sets, matching holdout ID and contract version,
   `status=frozen`, and both first-runtime timestamps equal to `null`.
3. Require the complete frozen input register in both files. Reject an unknown,
   missing, duplicate, substituted, path-mismatched, SHA-mismatched, or
   byte-mismatched record; reject a manifest/attestation disagreement.
4. Recompute and compare every register file record, including the generator
   procedure, schema source, runtime input, evaluator wrapper/core,
   normalization source, frozen corpus, canonical snapshot, and approved
   evaluation matrix. Recompute the ordered execution-source inventory and
   source-state record.
5. Verify the attested manifest record against the invoked manifest. Verify the
   reserved blind-output path, parse only its label-free outer envelope, and
   require exact session-ID equality with `runtime_input`.
6. Only after steps 1--5 pass may the evaluator create `results/first-run/`,
   write a runtime-started manifest, validate contract-v2 payloads, and read
   the expected labels from the frozen reviewed corpus for scoring.

Any failure in steps 1--5 is a preflight failure: the evaluator exits non-zero
and creates no `results/first-run/` directory or result file. A failure after
step 6 is recorded in the already-created first-run manifest as a runtime
failure and is never a reason to rerun the same frozen holdout.

## G3 implementation and regression requirements

G3 must implement the register and preflight above in the next freeze tool and
evaluator. Its focused tests must prove all of the following:

1. a self-consistent fixture succeeds through preflight without parsing labels;
2. each required register record missing from either manifest or attestation
   fails before result-directory creation;
3. a changed procedure, schema source, runtime input, wrapper, core,
   normalization source, corpus, snapshot, matrix, or inventory member fails
   before result-directory creation;
4. altered path, SHA-256, byte count, holdout ID, exact CLI args, manifest
   record, or manifest/attestation parity fails before result-directory
   creation;
5. an unrecorded generator-readable file and a generator procedure containing
   a prohibited blind input are rejected by the freeze/preflight contract; and
6. a structurally invalid blind output fails before expected-label parsing and
   before result-directory creation.

The tests must distinguish preflight failure from a scored runtime failure and
must prove that the evaluator performs no canonical-DB access or raw-text
fallback.

## v6 defect-to-prevention map

| v6 defect | Why v6 could not prove the declared procedure | Required v7 prevention |
| --- | --- | --- |
| Manifest fingerprinted the v5 protocol, not the v6 generator procedure | The actual generator instruction was never frozen | `generator_procedure` is required in both files and verified before labels. |
| Attestation had no path-bearing generator-procedure record | There was no attested identity for the blind instruction | Every register item includes the same path/hash/bytes record in manifest and attestation. |
| Wrapper delegated to generic evaluator without procedure verification | A passing generic check could not establish procedure integrity | Preflight explicitly verifies all register items and attestation parity before output or labels. |
| `host_generation.procedure` was only prose | It could not bind a file or prevent substitution | The manifest has a dedicated file record, not descriptive prose, for the procedure. |
| Generic preflight checked only a subset of declared inputs | Core and imported scoring dependencies could drift without a contract check | Wrapper, core, schema, normalization source, and complete execution-source inventory are all frozen and recomputed. |

## Acceptance and next boundary

G2 is complete when this contract is the sole definition of the next
holdout's blind input register and evaluator preflight. G3 may implement it;
G3 may not weaken it, collect a source, or create a frozen directory.
