# VEIL real-conversation UX evaluation protocol

**Authorization:** 2026-07-21 user approval. This protocol authorizes only
the bounded, anonymized evaluation below. It does not authorize canonical DB,
Git, installation, sync, distribution, or remote writes.

## Scope and privacy boundary

- Source window: Codex conversations created in the 30 days ending 2026-07-21.
- Exclusion: every VEIL development, holdout, release, or installation
  conversation is excluded before sampling.
- Maximum: 100 reviewed term-in-context rows.
- Raw conversations, attachments, thread IDs, absolute paths, commit IDs,
  URLs, secrets, credentials, and personal names must not be written to this
  repository or to `workspace/audit/`.
- The custodian creates only a manually reviewed, anonymized source sheet.
  It replaces project, person, path, ID, secret, and attachment references with
  neutral placeholders or removes the whole excerpt where redaction would
  change its meaning.
- Artifacts stay only under the named `workspace/audit/` run for 30 days;
  retention owner is `VEIL evaluation owner` and deletion authority is
  `repository owner only`.

## Independence boundary

1. The implementation author may retrieve and anonymize the approved source
   window but must not label expected outcomes.
2. Reviewer A receives only the anonymized source sheet and this protocol. It
   chooses up to 100 term-in-context rows and writes expected outcomes,
   rationale, impact, and source class without reading VEIL implementation,
   tests, earlier holdouts, or results.
3. Reviewer B receives the anonymized source sheet and Reviewer A's corpus. It
   reviews every row. A disagreement becomes `exception`, never a forced
   automatic label.
4. The custodian freezes the reviewed corpus and a blind runtime input before
   the host AI sees labels. The host AI reads only the blind input plus the
   current Skill/schema and produces one contract-v2 extractor-plus-critic
   payload per session.

## Sampling and label contract

- A source session is one anonymized excerpt or contiguous excerpt group.
- Reviewer A samples ordinary prose, identifiers/placeholders, technical
  descriptions, quoted/meta wording, temporary scope, existing wording,
  definitions, explicit naming requests, change/conflict requests, and any
  naturally occurring Japanese/English variants. It must not invent language
  or pad a missing category.
- Each row contains `case_id`, `session_id`, `context`, `term`,
  `registered_terms`, `expected_outcome`, `impact`, `reason`, `source_class`,
  Reviewer A metadata, Reviewer B metadata, and anonymized-real provenance.
- `exclude`, `observe`, `existing-match`, and `exception` retain the approved
  automation-matrix meanings. A reviewer disagreement is `exception`.
- The evaluator derives blind session text from the first distinct contexts in
  row order, joined by `\n\n`, and sorts/deduplicates registered terms.

## Gates and interpretation

- Every generated frame/evidence reference must pass contract-v2 validation;
  raw-text fallback is forbidden.
- No high-impact reviewed `exception` may become a non-exception.
- Every ordinary session must require zero questions; every exception session
  may require one combined question only; an unreviewed exception fails.
- Record exact-outcome agreement and outcome precision. A shortfall is saved
  unchanged and triggers design review rather than cue/phrase patching.
- Passing this run is evidence about approved real Codex conversations only.
  It does not authorize release or claim accuracy for unobserved populations.

## Prohibited actions

Do not call DB write/export commands, install a Skill, regenerate installed
HTML, sync targets, stage or commit Git changes, push, create a pull request,
or run remote CI as part of this evaluation.
