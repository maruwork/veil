# VEIL real-conversation v2 independent evaluation protocol

## Purpose and boundary

This protocol corrects the invalid v1 corpus construction without changing the
preserved v1 source or first-run result. It measures the current frozen
classification behavior on newly selected, anonymized real-conversation
excerpts. It is not a release authorization and it does not prove all VEIL UX.

The only permitted artifacts are under
`workspace/audit/20260721-real-conversation-ux-v2/`. They are retained for 30
days; deletion requires the repository owner. DB, Git, install, sync, remote,
and source implementation writes are out of scope.

## Inputs and roles

- `input/anonymized-source.jsonl` contains only newly selected excerpts from
  the approved 30-day window. It must contain neither a personal name, secret,
  absolute path, raw conversation identifier, nor an excerpt already in v1.
- `input/canonical-snapshot.json` is a read-only filtered snapshot of the
  active canonical normalized terms. Reviewers may put a value in
  `registered_terms` only when it is an exact member of that snapshot.
- Reviewer A creates no more than 100 natural, complete-concept rows, validates
  each against the source and snapshot, and records rationale and impact.
- Reviewer B independently verifies every row against both inputs. A disagreement
  is either resolved in a replacement row before freeze or is recorded as an
  `exception`; it is never silently changed after freeze.
- The host sees only frozen runtime inputs, not corpus labels, before producing
  one semantic frame payload per session.

## Freeze and acceptance

The freeze checker rejects missing reviewer attestations, duplicate normalized
concepts within a session, invalid canonical registrations, v1 source reuse,
or a row whose context and term are not verbatim in its anonymized source.
It records source/evaluator hashes, the canonical snapshot hash, source state,
and an evaluator command before first execution.

The first evaluator run is immutable evidence. It reports exact outcomes,
false exclusions, unexpected existing matches, questions per session, source
integrity, DB access, raw fallback, and schema/evidence errors. A failing run
is retained and triggers a cause analysis before any implementation change.

## Candidate eligibility clarification after v2

`observe` is not a bucket for every complete named artifact, status, process,
or control. It requires a repeatable wording choice plus lexical evidence in
the source: a definition, contrast, preferred phrasing, stated reuse,
ambiguity, or a request to use, change, or register wording. An ordinary
mention without that evidence is `exclude`. This clarification is applied only
to a newly selected follow-up corpus; it does not modify the frozen v2 input
or result.
