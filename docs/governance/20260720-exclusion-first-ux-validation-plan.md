# VEIL exclusion-first UX validation plan

**Status:** reopened remediation and evaluation plan. The first implementation
attempt is not release-ready. No canonical DB, installed HTML, installed Skill,
sync target, installer, staging, commit, push, merge, or remote operation is
authorized by this document.

**Purpose:** reduce the number of judgments demanded from the user. AI may do more background work, but ordinary sessions must not expose candidate tables, manual commands, or a multi-step capture-to-registration loop.

## 2026-07-21 audit correction

- The 100 cases under `workspace/audit/20260721-exclusion-first-holdout/` and
  `tests/fixtures/veil_capture_outcome_stratified.json` are reclassified as a
  **development corpus**. The evaluator generated the data and its failures
  were used to tune the implementation, so this data is not a holdout.
- A passing pytest count is regression evidence only. At audit reopening the
  formal runner failed; the corrected `tests/browser_e2e_runner.py --json` is a
  separate release gate and now passes locally against the new UX contract.
- Explicit quoted intent, `the phrase`, existing-rule changes, conflicts, and
  structured multi-result completion are mandatory development cases before a
  new holdout is frozen.
- The automation matrix required by WP-4 was explicitly approved and fixed on
  2026-07-21. Release-complete or general-usability claims still require the
  independent holdout.
- A future holdout must use a separately named directory, must be frozen after
  annotation and before its first runtime execution, and must carry
  `context`, `term`, `expected_outcome`, `impact`, `reason`, `source_class`,
  `reviewer`, and second-review metadata for high-impact or ambiguous items.
- Independent holdout v1 was then frozen at 40 cases / 30 sessions and failed
  its first completed evaluation: 18/40 exact outcomes, 6 high-impact false
  exclusions, exclusion precision 36.67%, and failed question-count gates.
  The frozen inputs and canonical DB remained unchanged.
- v1 failures exposed five root classes: narrow quoted-registration syntax,
  missed natural change/conflict requests, incomplete definition-impact cues,
  lexical-only repetition handling, and descriptive Japanese `呼んでいます`
  being confused with an instruction. Source and Python/HTML parity tests were
  corrected. A later v1 development rerun reached 40/40 with no unexpected
  exceptions, but is explicitly ineligible as release evidence because v1 was
  already seen and the runtime scope changed. A newly frozen v2 is required.
- Independent holdout v2 was separately authored, reviewed 40/40 with no
  reviewer disagreement, attested, and frozen before its first runtime run.
  Its frozen corpus SHA-256 is
  `1965c56e78101f479d3d17d0aaec4f979981f75113cf454054266ef341a1d93d`.
  The first run preserved every input/source identity and the canonical DB but
  failed: 26/40 exact outcomes, 7 high-impact false exclusions, 52.17%
  exclusion precision, failed exception-session question counts, and
  unexpected exception terms.
- v2 showed a deeper boundary defect: quoted content was masked before intent
  analysis and later recovered by narrow word-order regexes. The corrected
  path now evaluates each quoted term against its current sentence plus one
  preceding scope sentence for explicit persistence, complete inventories,
  conflict, durable definition, repeated description, temporary scope, and
  term-directed negation. Generic meta labels such as `quoted phrase`,
  `というフレーズ`, and `引用語` cannot become terms.
- The post-fix v2 **development-only** rerun reached 40/40, 100% exclusion and
  existing-match precision, zero high-impact false exclusions, zero unexpected
  exception terms, 20 ordinary sessions with zero questions, and 10 exception
  sessions with one combined question. This is not release evidence because
  v2 was seen before the runtime behavior changed. A newly frozen v3 is
  required.
- Independent holdout v3 was newly authored and reviewed 40/40 with no label
  disagreement. Its original first command stopped before runtime import due
  only to manifest-schema key mismatches. The immutable corpus was mechanically
  re-frozen byte-for-byte under the existing evaluator schema; the eligible
  first runtime run then failed at 26/40, with 3 high-impact false exclusions,
  57.89% exclusion precision, unexpected exception terms, and failures in both
  ordinary- and exception-session question counts. All source/input/evaluator
  identities and canonical DB files remained unchanged.
- v3 confirms that further cue or phrase additions are not an acceptable
  remediation. The required architecture is recorded in
  `20260721-semantic-decision-frame-redesign.md`: host AI produces
  evidence-backed semantic decision frames and performs a background critic
  pass; local VEIL validates the evidence and applies deterministic no-write
  policy. Raw-text regex outcomes become diagnostic rather than production
  proof.
- Independent semantic holdout v4 was authored by Reviewer A, reviewed 40/40
  by Reviewer B with zero disagreement or ambiguity, and frozen before the
  host AI saw its labels. Its blind runtime input remained byte-identical
  across both reviews. The host AI then generated contract-v2 extractor and
  critic payloads from only the blind input and current Skill/schema. The
  immutable first run passed 40/40 exact outcomes across 30 sessions: all 20
  ordinary sessions required zero questions, all 10 two-exception sessions
  required exactly one combined question, both precision measures were 100%,
  and there were zero high-impact false exclusions, unexpected exceptions,
  validation errors, raw-text fallbacks, or canonical DB accesses. The frozen
  source identity was unchanged during the run.

Current remediation evidence (2026-07-21): contract v2 now has a dependency-free
semantic-frame/evidence/critic validator and deterministic no-write policy,
safe CLI file input, invariant-focused tests, and matching Codex/Claude Skill
instructions. Contract v1 raw-text output is explicitly diagnostic. The HTML
primary recovery action now copies the complete text for semantic AI review;
its regex preview is labelled diagnostic and cannot declare review complete.
The updated formal Edge runner passes diagnostic labeling, complete-text
semantic request copy, English/Japanese locale, fine-tuning, clipboard
success/fallback, and zero direct writes. After the v4 first run, the same
source passed all 276 pytest cases in 79.46 seconds, the formal local Edge E2E,
Python syntax checks, and `git diff --check`. This establishes the approved
automation matrix on an unseen independent synthetic set; it does not establish
real-conversation usability or authorize remote CI or distribution. The next
eligible UX evidence requires separate approval of the real-conversation
scope, anonymization, retention, and two-reviewer handling before any such
conversation is read.

## 1. Product hypothesis and boundary

The hypothesis is not "find more candidate terms." It is: most extracted strings are not durable vocabulary decisions, so exclude them before they reach the user and inspect only the small unresolved remainder.

```text
User: conversation ends -> no VEIL output, or one combined durable-decision question
AI:   semantic extractor -> independent critic -> exact-evidence frame payload
VEIL: local validation -> exact existing-rule match -> deterministic no-write policy
      -> automatic outcome or one combined exception batch
```

This proposal does not authorize direct browser writes or a second canonical store. `~/.veil/veil.db` remains the only canonical vocabulary store. It permits no writes to canonical, distribution, external, or Git state. It permits bounded evaluation-artifact writes only under `workspace/audit/<run>/`; those artifacts are never vocabulary rules.

## 2. Decisions that require evidence

| ID | Decision | Evidence required | Default until proven |
|---|---|---|---|
| D1 | Which strings never need user attention? | Labelled corpus and false-exclusion review | Do not auto-register new rules |
| D2 | Which outcomes can be automatic? | Precision by outcome and impact tier | Only exact existing-rule normalization |
| D3 | What must be reported? | Scenario review | Outcome, count, exceptions only |
| D4 | When may an exception be deferred? | Recurrence and impact analysis | Observe; do not sync or canonicalize |
| D5 | Does the flow reduce burden? | Judgment-count comparison | Do not change visible flow for aesthetics |

## 3. Evaluation outcomes

Every extracted string receives one evaluation outcome. These are not runtime or database states.

| Outcome | Meaning | User visibility | DB/sync effect |
|---|---|---|---|
| `exclude` | Clearly unrelated to a durable vocabulary decision | Never | None |
| `observe` | Not safe to decide yet | Never in normal flow | None |
| `existing-match` | A valid normalized match to an existing rule | Count only | No write during evaluation |
| `exception` | Conflict, high impact, or insufficient evidence | Concise question/batch | None until resolved |

Initial exclusion categories to test:

1. file names, paths, URLs, command options, hashes, identifiers, and config keys;
2. product names, organizations, people, and established proper nouns;
3. broad technical terms that are not locally defined in context;
4. ordinary prose, bare verbs, generic adjectives, and session-log residue;
5. one-off low-signal strings; and

`existing-match` is not an exclusion: it is a meaningful operational outcome
and must be counted separately from excluded noise.

`observe` is not deletion: a term can be reconsidered only after recurrence, material impact, or an explicit user request.

## 4. Work packages

### WP-1: Inventory current classifier behavior

**Inputs:** `veil_capture_taxonomy.py`, `veil_capture_classifier.py`, `veil-classify.py`, classification design doc, tests, and fixtures.

**Tasks:**

1. List every taxonomy set and candidate gate.
2. Map every branch to `exclude`, `observe`, `existing-match`, or `exception`.
3. Identify rules that only suppress fixture residue rather than express a comprehensible product policy.
4. Record overlap, contradiction, and unknown-term behavior.

**Artifact:** `workspace/audit/<run>/classifier-inventory.json` with rule source, current behavior, proposed outcome, and rationale.

**Exit criterion:** every current candidate/exclusion branch is mapped; DB, HTML, and sync target remain unchanged.

### WP-2: Build a labelled evaluation corpus

**Goal:** measure user-facing residual work, not dictionary coverage.

**Tasks:**

1. Obtain explicit scope approval for source conversations, date range, and
   anonymization before reading any real conversation.
2. Define one sampling unit as one extracted term plus the minimum surrounding
   context needed to decide whether it is durable vocabulary.
3. Stratify the first 100 items across identifiers, proper nouns, industry
   terms, generic prose, local coined phrases, existing matches, and ambiguous
   cases. Add items if any stratum is too small to evaluate.
4. Reserve a documented holdout set before tuning any rule.
5. Record each item as `context`, `term`, `expected_outcome`, `impact`,
   `reason`, `source_class`, and `reviewer`.
6. Define impact as low (no downstream effect), medium (local wording effect),
   or high (could create an incorrect canonical/sync decision).
7. Use two reviewers for high-impact and ambiguous items. Record disagreement
   as `exception`; do not force a false gold label.
8. Before changing a rule, measure the current classifier's extracted count,
   candidate count, outcome distribution, and questions-per-session baseline
   on the held-out corpus.

**Artifact:** corpus and annotation metadata under `workspace/audit/<run>/` only. The run directory name, retention owner, retention deadline, deletion authority, and exact reproduction command are recorded in `summary.md`; only that named owner may delete it after the deadline.

**Exit criterion:** category balance, provenance, and uncertainty are recorded; no item enters SQLite or the default profile.

### WP-3: Run a no-write shadow evaluator

**Tasks:**

1. Run extraction, classification, normalization, and existing-rule matching against the corpus.
2. For every input, record observed label, proposed outcome, existing match, confidence signal, expected outcome, and mismatch reason.
3. Prohibit `upsert-rule`, `export-html`, `veil-sync.py`, installers, and installed Skill paths.
4. Calculate extracted, excluded, observed, existing-match, exception, false-exclusion, and false-escalation counts.

**Artifacts:** `shadow-results.jsonl` and `summary.md` under the same audit run directory.

**Exit criterion:** results are reproducible from the corpus; all writes remain within that run directory.

### WP-4: Decide automation boundaries

**Approved automation matrix — fixed 2026-07-21 by explicit user authorization:**

| Situation | Automatic work | User-visible work | Persistence |
|---|---|---|---|
| no frame, negated/reported wording, or critic-rejected noise | `exclude` | none | none |
| validated temporary/one-off or low-impact unclear wording | `observe` | none | none |
| exact registered wording with no requested mapping change | `existing-match` | none | none |
| affirmed durable adopt/rename/definition, conflict, high-impact uncertainty, or material critic disagreement | `exception` | one combined question per session | only accepted mappings, one atomic batch |
| frame validation/write/export/sync failure | stop at failed stage | one concise failure result | never claim later stages completed |

This matrix remains the approved authority for independent holdout v1 and later
versions unless the user explicitly changes it. Any behavior change after a
holdout version is frozen invalidates that version's result as release evidence
and requires a new version. The normal trigger is automatic at a substantive
task close; explicit manual invocation runs the same semantic contract on the
supplied scope. HTML is an optional review and
recovery surface, not a required step in the ordinary flow.

| Metric | Definition | Recommended initial gate |
|---|---|---|
| Exclusion precision | excluded items that are truly non-decisions | >= 99% for high-impact contexts |
| Existing-match precision | automatic match agrees with labelled outcome | >= 99% |
| False exclusion | durable decision hidden by exclusion | 0 in high-impact holdout |
| Unexpected exception | unreviewed term added to the combined user question | 0 |
| Exception rate | user-visible items / all items | materially lower than current candidate rate |
| Judgment count | required questions per session | near zero in ordinary sessions |

**Rules:** never auto-create a new canonical rule in this phase; auto-resolve only exact normalized matches that meet the gate; send conflicts and high-impact changes to `exception`; keep low-confidence material in `observe`.

**Exit criterion:** an approved matrix states which outcomes are automatic, observed, or user-visible.

### WP-5: Specify the visible result contract

**Normal automatically triggered result:** no VEIL-specific output.

**Normal explicitly invoked result:** one localized no-decision sentence.

**Exception:**

```text
I found wording that affects future consistency:
- release readiness -> release readiness
Record these together? Reply with changes or skips only, or "as proposed".
```

The normal result must not expose candidate tables, candidate numbering, classification labels, manual commands, or required copy/paste.

**Exit criterion:** scenario walkthrough covers no-exception, existing-match, ambiguity, conflict, failure, and recovery; a user can understand the result without internal terminology.

### WP-6: Separate authorization for new scope and release

The user authorized safe remediation after the audit, so fixes required to
restore the stated exclusion-first contract may proceed. New feature scope and
release remain prohibited until WP-1 through WP-5 evidence is reviewed, the
automation matrix is approved, every hunk is ledger-classified, and Browser
E2E plus the independent holdout have policy-compliant execution paths.

## 5. Explicit non-work

- Do not make Candidate 2 optional merely to remove a field.
- Do not expose semantic-frame generation, critic review, or a referent table as a user step.
- Do not write evaluation observations to `~/.veil/veil.db`.
- Do not regenerate HTML, install Skills, sync targets, stage, commit, push, or alter Git history.
- Do not claim correctness from fixture lockstep or test count alone.
