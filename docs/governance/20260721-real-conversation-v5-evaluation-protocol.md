# VEIL real-conversation v5 independent evaluation protocol

**Status:** successor design after the preserved v4 input-contract failure.
This protocol does not repair, rescore, or rerun v4.

## Purpose

v4 reached an immutable first invocation but failed before scoring because the
blind-generator instruction exposed only the semantic payload schema. The
evaluator additionally required a JSONL envelope, but that envelope was not a
public generator contract. This is a procedure/interface defect, not evidence
about VEIL classification quality or real-conversation usability.

v5 evaluates the same bounded automation question with a fresh, independently
reviewed anonymized corpus. It must not reuse v4 excerpts, labels, generated
frames, or expected results.

## Blind generator contract

The blind generator may read only:

1. v5 `frozen/runtime-input.jsonl`; and
2. `shared/tools/veil_decision_frames.py`.

For every runtime-input row, it writes one JSONL object and no other object:

```json
{"session_id":"<verbatim runtime session id>","payload":{"contract_version":"2","frames":[],"critic":{"status":"confirmed","confirmed_frame_ids":[],"rejected_frame_ids":[],"unresolved_frame_ids":[],"missing_frames":[]}}}
```

The object has exactly `session_id` and `payload`; the payload itself obeys the
contract-v2 fields and exact-evidence rules in `veil_decision_frames.py`.
`session_id` is copied verbatim, one output row exists for every input row, and
there are no extra output fields. The generator must not read the reviewed
corpus, reports, frozen corpus, labels, expected results, prior holdouts, DB,
or source artifacts outside the two permitted files.

## Reviewed-corpus outcome contract

Every reviewed row uses exactly one of `exclude`, `observe`,
`existing-match`, or `exception`. `new_candidate` is not an outcome and must
never appear in a freeze input. An unregistered durable adoption, definition,
rename, conflict, or high-impact policy decision is `exception`; it does not
become a candidate-table state. A generic actor, tool, predicate, or support
phrase is not a primary lexical target unless its own meaning or allowed use
is independently decided.

## Evidence sequence

1. Select fresh anonymized excerpts within the already authorized real-
   conversation scope, excluding v1--v4 excerpts and VEIL development.
2. Have two independent reviewers validate source fidelity, canonical snapshot
   membership, eligibility, primary lexical targets, normalized-term
   uniqueness, and all required reviewer metadata.
3. Before freeze, mechanically validate the reviewed corpus against the freeze
   schema. If it is malformed, correct only mechanical schema fields with a
   before/after hash record and without changing reviewed labels or reasons.
4. Freeze once, preserving the manifest, attestation, corpus, and runtime
   input. Do not overwrite a frozen directory.
5. Use a fresh blind generator under the contract above, then run the recorded
   evaluator command exactly once.
6. Preserve the result. An input-contract failure is a failed evaluation run,
   not permission to rerun it. Perform cause analysis before any later source
   change; never add phrase-specific classifier cues.

## Boundaries

No canonical DB access or write, sync, install, generated HTML refresh, Git
operation, remote action, release action, raw transcript retention, or source
implementation write is part of a v5 evaluation run. Artifacts remain under
the v5 audit directory for 30 days; deletion requires the repository owner.
