# VEIL session handover — 2026-07-21 (v6 evaluation continuation)

**Status:** continuation only. This document does not authorize staging,
commit, push, installation, sync, HTML export, canonical DB writes, remote CI,
or release actions.

## Authority and boundaries

- Canonical vocabulary remains `~/.veil/veil.db`.
- `README.md` is the developer entry route; `docs/veil-design.md` is the
  design authority; `shared/runtime/`, `shared/tools/`, and `skills/` are the
  active implementation surfaces.
- `common/` is a reusable PJ Framework mirror, not project-local current
  truth. For this repeated evaluation work, the relevant shared rule is
  `common/pj-template/rules/operations/long-run-execution.md`.
- Do not broad-read `workspace/`, `archive/`, or `.trash-migration/`. Do not
  use `C:\tmp`.
- The worktree was already large and dirty. Preserve unrelated changes; do
  not reset, restore, clean, stage, commit, or push.

## Historic evidence: do not promote it

- The contract-v2 architecture is: host AI supplies exact-evidence semantic
  frames and a critic result; local VEIL validates the untrusted payload and
  applies `exclude` / `observe` / `existing-match` / `exception` with no
  classification-time DB write.
- The synthetic holdout v4 previously passed 40/40. That is not real-
  conversation usability proof.
- Real-conversation v1, v2, and v3 are preserved failed evidence. Do not
  rewrite or reuse them.
- v4 froze and was invoked once, but failed before scoring because the blind
  generator was not given the evaluator-required outer JSONL envelope. It is
  immutable failed input-contract evidence; do not rerun it.
- v5 froze and was invoked once. Its generator emitted a valid envelope with
  an empty payload, producing zero exact outcomes and a high-impact false
  exclusion. It is immutable failed evidence; do not rerun it.

## Changes made in this session

1. Added the public blind-generator envelope contract to
   `shared/tools/veil_decision_frames.py`:
   `{"session_id": "<verbatim input id>", "payload": <contract-v2 payload>}`.
   The generic holdout evaluator imports the same field set.
2. Added a focused envelope test; `tests/test_decision_frames.py` passed
   15 tests after that change. `git diff --check` passed at that point.
3. Added `docs/governance/20260721-real-conversation-v5-evaluation-protocol.md`
   and `docs/governance/20260721-real-conversation-v6-generator-procedure.md`.
4. Added v5 mechanical review-submission validation at
   `workspace/audit/20260721-real-conversation-ux-v5/validate_reviewed_submission.py`.
   It validates exact source context, verbatim term, four-state outcome,
   snapshot membership, reviewer metadata, second-review object, provenance,
   and within-session duplicates.
5. Preserved v5 review-attempt failures under its `reviewed/` directory.
   They are failed supporting artifacts, not valid corpus input.

## Current long-run record

`workspace/audit/20260721-real-conversation-ux-v6/execution.md` is the active
record. Its goal is fresh two-reviewer real-conversation evidence; its active
work unit is a reviewed corpus that passes the mechanical gate.

### v6 current state

- `input/anonymized-source.jsonl` contains one fresh anonymized source row.
- `input/canonical-snapshot.json` records the three active normalized DB terms
  from a read-only readback: `current issue`, `current state`, and
  `unstable wording`.
- Reviewer A and B artifacts exist under `reviewed/`; both were reported as
  passing the mechanical review gate.
- v6 freeze succeeded once:
  - 4 reviewed cases
  - 1 runtime session
  - 4 expected `observe` outcomes
  - 3 high-impact and 1 medium-impact rows
  - 4 agreeing second reviews
- `frozen/runtime-input.jsonl` exists.
- A fresh v6 blind generator was authorized to read only the frozen runtime
  input, `shared/tools/veil_decision_frames.py`, and the v6 generator
  procedure. It reported writing one output row to
  `frozen/generated-frames.jsonl`.
- **The v6 evaluator has not yet been invoked.** Do not inspect reviewed
  expected outcomes before the one allowed evaluator invocation.

### v6 validity defect found during handover audit

The frozen v6 manifest incorrectly fingerprints
`docs/governance/20260721-real-conversation-v5-evaluation-protocol.md`, not
the v6 generator procedure that was actually given to the blind generator.
The v6 evaluator wrapper is also a minimal copied wrapper and does not perform
the v4-style evaluator/source/snapshot fingerprint checks itself. Therefore a
v6 evaluator invocation can preserve a one-time result, but **cannot support a
claim that the v6 generation procedure was frozen and evaluated as declared**.
Do not repair or rerun v6. Preserve it as an assumptions/procedure failure,
write cause analysis after the one allowed invocation if it is run, and create
a new holdout only after the manifest and evaluator contracts are corrected.

## Exact next action

Run the v6 evaluator exactly once only if preserving the current invalid
procedure result is still useful; do not treat it as a valid v6-procedure
evaluation. Do not first read generated frames or reviewed expected labels:

```powershell
rtk python workspace/audit/20260721-real-conversation-ux-v6/evaluate_real_holdout.py `
  --corpus workspace/audit/20260721-real-conversation-ux-v6/frozen/frozen-corpus.jsonl `
  --runtime-input workspace/audit/20260721-real-conversation-ux-v6/frozen/runtime-input.jsonl `
  --generated-frames workspace/audit/20260721-real-conversation-ux-v6/frozen/generated-frames.jsonl `
  --manifest workspace/audit/20260721-real-conversation-ux-v6/frozen/frozen-manifest.json `
  --attestation workspace/audit/20260721-real-conversation-ux-v6/frozen/freeze-attestation.json `
  --result-dir workspace/audit/20260721-real-conversation-ux-v6/frozen/results/first-run
```

Preserve the result regardless of outcome. If it fails, write cause analysis
before changing source. Never add phrase-specific cues and never rerun the
same frozen evaluation.

## Process correction required

The prior operator repeatedly treated intermediate defects as terminal chat
responses. Do not do that. Under the common long-run policy, a malformed
reviewer artifact is retryable supporting work, not a stop. Keep one active
work unit, write durable evidence, and continue until an actual authority or
source-access boundary is reached.
