# VEIL v13 recovery design

## Purpose and boundary

v12 is immutable `requires-revision` evidence. Its one evaluator invocation
scored seven cases but recorded only three gates. It is not a v13 fixture,
input, source, or reusable result. v13 must use seven fresh sessions and may
not reuse any v1--v12 source, corpus, generated output, or result.

The immediate work is a disposable integration suite. It proves that a v13
adapter can invoke the real v4 scoring kernel after v13-owned preflight. It
does not select a v13 source, create `frozen/`, call a host generator, or
evaluate a real conversation. For fresh v13 G4 acquisition, the user has
authorized direct user text from non-VEIL parent sessions in either Claude Code
history or the local daily Codex session logs. System/developer instructions,
attachments, tool results, subagent logs, VEIL sessions, IDs, paths, URLs, and
raw transcripts remain excluded from v13 artifacts.

## Natural-corpus coverage adjustment

The original 1/2/2/2 stratification assumed that four outcome types could be
found naturally in historical logs. The authorized Claude Code and Codex
parent-session corpus does not contain fresh `existing-match` or `observe`
examples after v1--v12 overlap rejection. v13 therefore evaluates the
available natural corpus instead of asking the user to manufacture logs.

G4-v13 accepts at least three distinct fresh sessions, preserves the actual
candidate category counts, and records every unobserved category. G5 still
requires independent two-reviewer classification; it may reject any candidate.
G6--G9 may execute only if the merged corpus has at least three unique
sessions. The close must state that this is a partial natural-corpus UX
evaluation: it cannot claim `existing-match` or `observe` behavior was
observed when those categories remain absent.

## v13 runner contract

The adapter owns parsing, v13 metadata checks, result persistence, runtime
access guards, and terminal gates. It loads the real file
`workspace/audit/20260721-independent-semantic-holdout-v4/evaluate_semantic_holdout.py`
by exact path and invokes only its callable `score_prevalidated` kernel. It
must never call the v4 CLI `main()` or create the v4 result layout.

Before any expected outcome label is read, preflight must reject: an existing
result directory; malformed/duplicate JSON; an unknown or missing top-level
metadata field; metadata identity or attestation mismatch; an invalid file
record; source-state mismatch; invalid generated schema; invalid generated
semantic frame; and a generated/runtime session-set mismatch. A preflight
rejection creates no result directory.

After successful preflight, the adapter creates the result directory exactly
once and writes a `runtime-started` manifest. Every later exception overwrites
only that manifest with `runtime-error`; it never starts a second run. A
successful terminal manifest has exactly the required fields, includes the
before/after measured source state, access counts, case/summary file records,
and exactly the ten gates below.

## Ten gates and acceptance fixtures

The disposable fixture contains seven synthetic v4-compatible cases and
generated payloads. It is distinct from all real-conversation sources. The
passing fixture must invoke the actual v4 kernel and make all ten gates true.
Each negative fixture changes one named boundary and asserts that boundary is
rejected or false while preserving the expected lifecycle boundary. Some
scoring facts are causally coupled (for example, removing an exception frame
changes both its classification and its question count); their negative proof
must report that coupling instead of falsely claiming that only one derived
score changed.

| Gate | Passing proof | Isolated negative proof |
| --- | --- | --- |
| `strict_preflight` | exact schemas, records, source state, and blind payload validate | one malformed metadata/payload invariant is rejected before result creation |
| `runtime_started` | terminal manifest retains a recorded runtime start | injected failure before start leaves no result directory |
| `real_v4_core_scored` | result carries exact core path and real `score_prevalidated` response | a deliberately non-callable/wrong core path is rejected |
| `seven_case_count` | exactly seven case results | one valid eighth case makes this gate false |
| `exact_session_set` | corpus, runtime, and generated sets are identical | one generated session replacement makes this gate false before scoring |
| `classification_match` | real-core actual outcomes match reviewed expected outcomes | one expected outcome mutation makes this gate false after scoring |
| `exception_question_contract` | each session's question count matches its expected exception presence | one question contract mutation makes this gate false after scoring |
| `canonical_db_access_zero` | patched reachable `sqlite3.connect` counter remains zero | an injected DB call reaches the patch, increments it, and yields `runtime-error` |
| `raw_text_fallback_zero` | guarded runtime-row construction never invokes fallback | an injected fallback call reaches the guard, increments it, and yields `runtime-error` |
| `terminal_manifest_schema` | scored terminal manifest validates its exact field set and records | terminal-schema verifier rejects one missing or unknown field |

The DB guard wraps `sqlite3.connect` around the actual real-core call. The raw
fallback guard is the only conversion fallback entry point used by the adapter;
construction of the label-free runtime rows calls it when required input is
absent. Therefore its negative fixture exercises the same callable path as
production conversion, not a disconnected counter.

## Execution order and stop conditions

1. Implement the adapter, terminal-manifest verifier, and the acceptance suite
   in `workspace/audit/20260723-real-conversation-ux-v13/`.
2. Run the focused suite, then the repository test suite, and static checks
   that include untracked v13 files.
3. Record the exact test evidence and synchronize `execution.md`.
4. Only if every v13 acceptance fixture passes, begin fresh G4-v13 source
   eligibility, then G5 independent two-reviewer corpus, G6 input fixation,
   G7 blind generation once, G8 evaluation once, and G9 evidence close.

Any failed real-v13 generation or evaluation is preserved as a terminal,
non-rerunnable evidence package. A failure in this disposable suite is not a
v13 evaluation run and may be corrected and rerun.

## Production G6--G8 package contract

The v13 production run is a partial natural-corpus evaluation with an expected
case count of **three**, not the seven synthetic cases used by the disposable
integration suite. `seven_case_count` is therefore not a production gate.
The production terminal gate is `expected_case_count`, which is true only when
the scored result count equals the `expected_case_count` fixed in the input
manifest. The terminal record retains `evaluation_scope` and the three
unobserved categories so it cannot be read as a full multi-category result.

G6 atomically creates `frozen/` from a staging directory. Its manifest has the
exact fields `contract_version`, `holdout_id`, `status`, `evaluation_scope`,
`expected_case_count`, `reviewed_corpus`, `runtime_input`,
`generator_procedure`, `source_state`, and `artifact_policy`. Its attestation
has the exact fields `contract_version`, `holdout_id`, `manifest`,
`reviewed_corpus`, `runtime_input`, `generator_procedure`, and `source_state`.
`runtime-input.jsonl` is derived only from the merged reviewed corpus and has
only `session_id`, `source_text`, and `registered_terms`; it carries no review
label. The fixed source inventory contains the freeze, generation, evaluator,
adapter, semantic-frame validator, and real-v4-core sources. Every record is
path/hash/bytes checked before the single rename. A failed copy, metadata,
verification, or rename leaves no final `frozen/` directory.

G7 may create the previously absent `generated-frames.jsonl` exactly once and
must simultaneously create `generation-attestation.json`. The latter records
the exact generated-file hash, the fixed runtime-input hash, and the
generator-procedure hash. The generator is given only the fixed procedure,
semantic-frame schema, and label-free runtime input; it must not read the
reviewed corpus, canonical snapshot, source-selection material, database, or
previous evaluation evidence. A generation failure is terminal evidence and
does not permit overwrite.

G8 first verifies the G6 manifest and attestation, then the G7 generation
attestation and generated frame schema/session set. It rejects any mismatch
before result-directory creation. After runtime starts it records either one
terminal scored manifest with `expected_case_count`, exact-session-set,
classification, question-contract, DB-access, raw-fallback, source-state, and
terminal-schema gates, or one terminal `runtime-error` manifest. Neither
terminal path may be rerun.
