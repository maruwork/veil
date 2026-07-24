# VEIL independent holdout protocol

**Status:** evaluation contract only. No real conversation scope is approved by
this file, and no Git, install, sync, canonical DB, or distribution write is
authorized.

## Purpose

Prove whether the end-to-end semantic route (host-AI extractor, separate critic,
local evidence validation, and deterministic policy) hides no durable
high-impact decision, resolves existing rules correctly, and reduces user work
to zero questions in ordinary sessions or one combined question in exception
sessions. The tuned 100-case development corpus and v1-v3 raw-text holdouts
cannot satisfy this purpose.

## Independence boundary

1. The implementation author and the evaluator must not author or revise the
   holdout labels.
2. Use either an explicitly approved real-conversation scope or synthetic data
   authored by an independent reviewer. The default is synthetic so no private
   conversation is read without a separate approval.
3. Reviewer A authors and labels the cases. Reviewer B checks every high-impact
   or ambiguous case plus a documented random sample of the remaining cases.
4. Disagreement is labelled `exception`; it is never forced into an automatic
   outcome.
5. Freeze the corpus and manifest before the runtime sees the first case. A
   post-run label or case edit creates a new holdout version and invalidates the
   former result as release evidence.
6. For a new version, both reviewers must avoid prior holdout corpora, runtime
   implementation, regression fixtures, evaluator outputs, and failure
   summaries until their review and freeze duties are complete.

## Evaluator semantics

- For contract v2 evaluations, freeze a separate `runtime-input.jsonl` derived
  from the reviewed corpus. It contains only session ID, exact concatenated
  source text, and registered terms. It contains no expected outcomes, terms,
  reasons, impact labels, source classes, or reviewer verdicts.
- Derive each session source deterministically: keep the first occurrence of
  each distinct context in corpus row order and join those contexts with
  exactly one blank line (`\n\n`). Sort and deduplicate registered terms.
- The host AI under test may read only `runtime-input.jsonl`, the current
  installed/source Skill contract, and the schema description. It must produce
  one contract v2 semantic-frame plus critic payload per session before the
  evaluator reads labels. Hand-authored policy fixtures are ineligible.
- The local evaluator validates every generated payload through
  `analyze_decision_frames()`. A schema/evidence failure is a failed session; it
  must not fall back to contract v1 raw-text outcomes.
- A session may contain multiple term-in-context rows with different context
  strings. The evaluator concatenates distinct contexts in row order and uses
  the union of registered terms, matching the one-review-at-task-close UX.
- A change or registration mapping may represent the reviewed term as either
  the runtime signal's source term or its structured `requested_preferred`
  value. The evaluator must match both without creating a second user item.
- Every runtime `exception` must correspond to a reviewed exception row.
  An extra exception hidden inside the same combined question is a UX failure,
  even when the session question count remains one.
- Exact equality with the manifest-recorded evaluator command is a first-run
  preflight gate. A later recovery or development rerun must use a new result
  directory, declare its preserved prior result, remain input/DB bounded, and
  is never release evidence after runtime behavior has changed.

## Required record per term-in-context

Each JSONL row must contain:

```json
{
  "contract_version": "2",
  "case_id": "unique stable id",
  "session_id": "group used for question counting",
  "context": "minimum text needed for the decision",
  "term": "term under review",
  "registered_terms": [],
  "expected_outcome": "exclude|observe|existing-match|exception",
  "impact": "low|medium|high",
  "reason": "human explanation of the expected outcome",
  "source_class": "identifier|proper-noun|ordinary-prose|existing-rule|explicit-request|change|conflict|definition|negative-or-quoted-meta|other",
  "reviewer": {"id": "reviewer-a", "reviewed_at": "RFC3339"},
  "second_review": {
    "required": true,
    "reviewer_id": "reviewer-b",
    "verdict": "agree|disagree",
    "reason": "review explanation",
    "reviewed_at": "RFC3339"
  },
  "provenance": {
    "kind": "independent-synthetic|approved-real-conversation",
    "scope_id": "approved scope or synthetic batch id",
    "contains_real_conversation": false
  }
}
```

No row may omit reviewer, impact, reason, source class, or provenance. A
high-impact or ambiguous row is invalid without a completed second review.
The reviewer labels describe expected user outcomes; they must not contain the
semantic frames that the host AI will later generate.

## Minimum coverage

The frozen set must include ordinary prose, identifiers, proper nouns, exact
existing matches, explicit English and Japanese requests, quoted requested
terms, `the phrase`, existing-rule changes, competing preferred forms,
high-impact definitions, negation, historical quotation, examples/test
fixtures, and multi-exception sessions. At least 20 sessions must contain no
exception, and at least 10 must contain two or more exceptions so question
count is measured rather than inferred from single-term cases.

Each new version must use newly authored terms and contexts rather than
paraphrasing the prior version's failed rows. It must include natural request
variants (`register`/`save`, preferred-wording changes, descriptive repetition,
and scoped low-impact definitions) without exposing prior runtime results to
either reviewer.

For contract v2, punctuation, clause order, negation, persistence, temporary
scope, rename mapping, and conflict grouping must vary independently. Passing a
policy-only fixture does not satisfy this coverage; the host AI must infer and
cite the frames from the frozen source text.

## Freeze manifest

Before the first evaluation, write a manifest beside the JSONL with:

- corpus and blind runtime-input SHA-256 and byte counts;
- schema/contract version;
- case, session, source-class, impact, and outcome counts;
- reviewer A and B identities;
- creation and freeze timestamps;
- source-state identifier: `HEAD`, tracked worktree-diff SHA-256 when dirty,
  and a release-scope inventory SHA-256 over each sorted normalized path plus
  its raw bytes. The inventory must include the exact runtime/test paths in the
  classification ledger so untracked source cannot escape the identifier;
- exact read-only local evaluator command and the declared host-AI generation
  procedure;
- artifact owner, retention deadline, and deletion authority;
- `first_runtime_execution_at: null`.

Before runtime, the freeze custodian must also write a separate attestation
that hashes the exact frozen corpus, blind runtime input, frozen manifest,
approved-matrix authority, and this protocol. The evaluator verifies the
attestation before importing VEIL. It records its own hash, the generated-frame
artifact hash, and the first runtime timestamp in the separate result manifest;
it never edits frozen inputs.

The evaluator first verifies the hash and schema, then writes the first runtime
timestamp to a separate result manifest. It never edits the corpus manifest or
corpus.

## Release gates

- zero high-impact false exclusions;
- exclusion precision >= 99%;
- existing-match precision >= 99%;
- every ordinary session has zero questions;
- every exception session has exactly one combined question;
- zero unreviewed or unexpected exception terms inside that combined question;
- every generated frame and evidence reference passes local contract v2
  validation, with zero raw-text fallback;
- no automatic canonical write;
- no result derived from a corpus whose hash changed after freeze.

The development corpus, pytest, and Browser E2E remain necessary regression
evidence but cannot substitute for this independent result.
