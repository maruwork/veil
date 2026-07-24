# VEIL session handover — 2026-07-21 (semantic UX evaluation)

**Status:** continuation handover. This is not release approval. It does not
authorize staging, commit, push, install, sync, HTML export, DB writes,
`~/.veil` changes, remote CI, or remote changes.

## Read order

1. Root `AGENTS.md`, `README.md`, and `common/README.md`.
2. `docs/governance/20260720-veil-session-handover.md` for migration/Git
   boundaries and historical M1/M2/G/C/R/P scope.
3. `docs/veil-design.md` and `docs/veil-capture-classification.md`.
4. This handover, then the exact tool, Skill, test, or audit artifact touched.

Do not broad-read `workspace/`, `archive/`, or `.trash-migration/`. Only the
specific `workspace/audit/20260721-*` paths cited below are in scope. Do not
use `C:\tmp`.

## Goal and non-goal

VEIL was resumed because the former classifier/taxonomy tests did not prove
that ordinary conversations receive correct automatic handling or that users
are asked only when a durable vocabulary decision is necessary. The goal is
not fewer AI operations. It is fewer, simpler user judgments while preserving
vocabulary quality and operational reliability.

The desired behavior is:

- ordinary process/status/tool language: silent automatic handling, zero VEIL
  questions;
- exact established wording: automatic `existing-match`;
- a genuine durable definition, adoption, rename, conflict, or material
  uncertainty: one combined exception question;
- no automatic canonical DB write from classification alone.

Do not make a change merely to reduce implementation size, candidate counts,
or test duration. Do not use fixtures as evidence of general real-conversation
accuracy.

## Why VEIL paused, and why this work resumed

VEIL development was paused because prior progress mainly demonstrated that a
fixed taxonomy, fixtures, and local commands agreed with one another. It did
not demonstrate either of the user-facing properties that matter: which real
conversation wording VEIL can cover, and whether it can process that wording
correctly without repeatedly asking the user to decide. More candidate tables,
regexes, or a lighter-looking UI would not answer that question.

The work resumed after two facts were separated:

1. The pre-existing raw-text classifier repeatedly failed independent unseen
   synthetic holdouts across quotation, directed change, conflict, durable
   definition, temporary scope, negation, and token-boundary cases. Those
   failures were cross-family, so adding phrase exceptions was rejected.
2. The replacement architecture makes the host AI extract exact-evidence
   semantic decision frames and run a critic pass; local VEIL validates those
   untrusted frames and alone owns deterministic policy and all writes. This
   is deliberately not an AI-authorized DB-write path.

An independent synthetic semantic holdout then passed, proving this bounded
automation contract. It did **not** prove usability on real conversations.
The user therefore explicitly authorized the narrow, anonymized,
two-reviewer real-conversation evaluation now in progress. The current v1--v4
sequence is the missing evidence path, not a side project and not a reason to
broaden release scope.

### Evidence hierarchy and decision rule

```text
fixture/taxonomy regression        -> protects a known contract only
independent synthetic holdout pass -> proves the bounded automation contract
independent real-conversation run  -> tests natural-language usability boundary
release/install/remote CI          -> distribution readiness, separately gated
```

Never promote a lower level to a higher-level claim. In particular, neither a
passing synthetic holdout nor a passing small real sample proves that all VEIL
UX is usable; it only decides the next evidence or design step.

## Permanent safety boundaries

- Canonical vocabulary is `~/.veil/veil.db`; all audit DB reads are read-only.
- Artifact writes are limited to `workspace/audit/`; retention is 30 days and
  deletion requires the repository owner.
- Preserve the large dirty worktree and the M1/M2/G/C/R/P ledger. Do not reset,
  restore, clean, stage, commit, push, install, sync, regenerate installed
  HTML, or alter remote state.
- The installed HTML and both installed Skills were intentionally `STALE` at
  the last delivery check. Source-side work does not mean the installed UX is
  improved.
- The source changes continue to be a mixed migration candidate. Distribution
  and Git release review are a later, separately authorized step.

Git scrutiny precedes UX installation/generation because this is a large,
mixed dirty worktree: migration/freshness work, capture UX, Skills, docs, and
generated/distribution concerns coexist. Installing, syncing, or creating a
release before the source scope and evidence are stable would make it
impossible to distinguish a UX result from a delivery-state change. Safe
read-only verification and narrowly scoped source work continue without waiting
for release authority; delivery and Git operations do not.

## What is implemented and verified

The source has a contract-v2 semantic-frame route:

- `shared/tools/veil_decision_frames.py` validates evidence-backed frames plus
  an independent critic; it does not infer decisions from raw text itself.
- `shared/runtime/veil-classify.py --semantic-frames` applies deterministic
  `exclude` / `observe` / `existing-match` / `exception` policy with no write.
- The Codex and Claude capture Skills, review UI, docs, tests, and E2E were
  updated in the dirty worktree. The user is shown at most one batched
  exception question.
- The independent synthetic holdout v4 passed 40/40. Earlier verification also
  recorded `276 passed` for the full pytest suite, Edge E2E, and
  `git diff --check`; re-run before any release claim because the worktree has
  changed afterward.

After the real-conversation v3 finding, a generic **primary lexical target**
rule was added to both Skills and the main design/classification docs:

- a definition/correction/contrast frames the wording whose meaning, allowed
  use, or preferred form is actually decided;
- generic predicates and explanatory phrases are evidence, not extra frames,
  unless independently decided;
- several independent primary targets may coexist in a session.

Focused regression after that edit:

```text
python -m pytest tests/test_skills.py tests/test_decision_frames.py -q
21 passed
git diff --check
pass
```

## Real-conversation evaluation history

The user authorized up to 100 anonymized Codex conversations from the preceding
30 days, excluding VEIL development. No raw transcript, personal name, secret,
absolute path, DB write, Git operation, install, sync, or remote change is
authorized. The corpus is independently labeled by two reviewers, then frozen;
the frame generator receives only blind runtime inputs.

### v1 — preserved, invalid corpus

`workspace/audit/20260721-real-conversation-ux-v1/`

The first run failed. It is not implementation-quality evidence because
reviewers put interesting words, rather than exact read-only canonical DB
facts, in `registered_terms`, and allowed duplicate/conflicting concepts.
Preserve it; do not repair its input or result.

### v2 — preserved failed evidence; eligibility contract defect

`workspace/audit/20260721-real-conversation-ux-v2/`

The first run failed 0/3 exact. Reviewers labeled a named artifact, a release
status, and an acceptance-control phrase as `observe`; blind extraction emitted
no semantic frame. The root cause was that the contract confused a complete
natural concept with a VEIL vocabulary candidate. See
`v2-cause-analysis.md`.

The corrective eligibility rule is already recorded in
`docs/governance/20260721-real-conversation-v2-evaluation-protocol.md`: an
`observe` target needs a repeatable wording choice *and* lexical evidence of a
definition, contrast, preferred form, stated reuse, ambiguity, or explicit
wording request. Ordinary work states/process/tool mentions are `exclude`.

### v3 — preserved failed evidence; target-granularity defect

`workspace/audit/20260721-real-conversation-ux-v3/`

The frozen first run had 2/4 exact results, with schema/evidence checks, no DB
access, no raw fallback, source-state integrity, and question counts all
passing. It failed because the corpus selected one primary term while blind
generation also framed generic explanatory phrases, and one generator term was
broader than the reviewer term. See `v3-cause-analysis.md`.

Do not patch individual phrases from either run. The primary-target rule above
is the generalized corrective implementation.

Mechanical provenance note: the raw v3 Reviewer-A corpus used
`reviewer.reviewer_id` instead of the contract key `reviewer.id`. Before v3
freeze, the reviewed `corpus.jsonl` was mechanically corrected to `id` without
altering its labels or reasons. The frozen corpus/result is preserved failed
evidence; do not treat v3 as a passing proof or rewrite it.

## Current exact state: v4 ready for freeze

`workspace/audit/20260721-real-conversation-ux-v4/` contains:

- `input/anonymized-source.jsonl`: eight new sanitized excerpts, not reused
  from v1/v2/v3;
- `input/canonical-snapshot.json`: filtered read-only snapshot of the three
  active normalized canonical terms;
- `reviewed/reviewer-a-corpus.jsonl` and `reviewer-a-report.json`;
- `reviewed/corpus.jsonl` and `reviewed/review-report.json`: Reviewer B retry
  completed; this corpus currently has 9 rows and is the only v4 input to
  freeze;
- `freeze_real_holdout.py` and `evaluate_real_holdout.py`.

The initial Reviewer-B agent made no artifacts and was interrupted. A fresh,
independent Reviewer-B retry completed the reviewed corpus/report. Do not
replace that second review with the first incomplete agent.

The v4 freeze wrapper reuses the generic mechanics of v3 freeze while setting
v4 paths, reviewers, holdout ID, and prior-source exclusion. Both v3/v4 freeze
scripts and the v4 evaluator passed `py_compile`; `git diff --check` passed.

## Exact next sequence

1. Inspect only v4 `reviewed/corpus.jsonl` and `review-report.json` for the
   freeze contract. Confirm the `reviewer.id` key is present (not
   `reviewer_id`), `second_review.reviewer_id` is `reviewer-b-real-v4`, each
   `registered_terms` entry is in the snapshot, contexts/terms are verbatim,
   primary targets are not support phrases, and duplicate normalized terms are
   absent within each session.
2. Run the v4 freeze once. Do not overwrite an existing `frozen/` directory:

   ```powershell
   rtk python workspace/audit/20260721-real-conversation-ux-v4/freeze_real_holdout.py `
     --reviewed workspace/audit/20260721-real-conversation-ux-v4/reviewed `
     --frozen workspace/audit/20260721-real-conversation-ux-v4/frozen
   ```

3. Use a fresh blind generator agent. It may read only v4
   `frozen/runtime-input.jsonl` and `shared/tools/veil_decision_frames.py`.
   It must write one contract-v2 payload per session to
   `frozen/generated-frames.jsonl`; it must not read reviewed corpus, labels,
   results, or older holdouts.
4. Run the exact command recorded by the frozen manifest, once:

   ```powershell
   rtk python workspace/audit/20260721-real-conversation-ux-v4/evaluate_real_holdout.py `
     --corpus workspace/audit/20260721-real-conversation-ux-v4/frozen/frozen-corpus.jsonl `
     --runtime-input workspace/audit/20260721-real-conversation-ux-v4/frozen/runtime-input.jsonl `
     --generated-frames workspace/audit/20260721-real-conversation-ux-v4/frozen/generated-frames.jsonl `
     --manifest workspace/audit/20260721-real-conversation-ux-v4/frozen/frozen-manifest.json `
     --attestation workspace/audit/20260721-real-conversation-ux-v4/frozen/freeze-attestation.json `
     --result-dir workspace/audit/20260721-real-conversation-ux-v4/frozen/results/first-run
   ```

5. Preserve the result regardless of outcome. If it fails, perform cause
   analysis before changing source; never add phrase-specific regex cues. If it
   passes, rerun the relevant source tests, full pytest with a unique workspace
   basetemp, Edge E2E, and `git diff --check` on the same source state.
6. Even a v4 pass is not proof that all VEIL UX is usable. Only then design a
   separately authorized, larger real-conversation sample or other operational
   evidence. Do not install/release/commit merely because an evaluation passes.

## Safe verification commands

```powershell
rtk git status --short
rtk git diff --check
rtk python -m py_compile workspace/audit/20260721-real-conversation-ux-v4/freeze_real_holdout.py workspace/audit/20260721-real-conversation-ux-v4/evaluate_real_holdout.py
rtk python -m pytest tests/test_skills.py tests/test_decision_frames.py -q
```

Use a new unique `workspace/audit/<run>` basetemp for any full suite; keep
`-p no:cacheprovider` because the pre-existing workspace cache may be
access-denied. The historic 64-second timeout was not reproduced under the
unique-basetemp condition; do not claim its cause is fully established without
the original command and conditions.
