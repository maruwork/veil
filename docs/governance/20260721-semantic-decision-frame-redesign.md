# VEIL semantic decision-frame redesign

**Status:** required redesign after independent holdout v3. This document does
not authorize Git, install, sync, canonical DB writes, distribution, or real
conversation collection.

## 1. Why the current model must be replaced

Independent holdouts v1, v2, and v3 all failed on their first eligible run.
v3 passed only 26/40 cases and repeated both dangerous failure directions:

- durable changes, conflicts, and definitions were silently excluded or only
  observed;
- ordinary identifiers and explicitly negated wording created user questions;
- apostrophes and quote-like syntax became false term boundaries;
- temporary definitions and repeated descriptions depended on exact cue words.

The defect is architectural. `analyze_capture_outcomes()` currently asks one
flat regex/classifier path to discover a term, infer the speech act, decide
persistence, resolve negation and scope, assess impact, and choose the UX
outcome. Adding another wording cue improves seen cases but cannot establish a
stable boundary for unseen natural language.

## 2. Fixed product decision

The normal task-close route will use two layers:

```text
host AI: conversation -> evidence-backed semantic decision frames -> self-review
local VEIL: validate frames -> exact DB match -> deterministic policy -> 0 or 1 question
```

The host AI may do more background work. The user must not classify tokens,
approve intermediate frames, run a candidate wizard, or see internal parser
steps. Local VEIL remains zero-dependency and retains all write authority.

The standalone regex/classifier may remain as a diagnostic and fallback for
lexical inspection, but it is no longer evidence that arbitrary conversation
intent was understood and must not be the production task-close decision
engine.

## 3. Semantic frame contract

The AI produces only wording that may represent a vocabulary decision. It does
not emit every token or ordinary noun. The complete payload has this shape:

```json
{
  "contract_version": "2",
  "frames": [
    {
      "frame_id": "stable within this analysis",
      "term": "exact wording under review",
      "intent": "mention|adopt|rename|define|conflict",
      "persistence": "none|temporary|durable|unclear",
      "polarity": "affirmed|negated|reported",
      "scope": "one-off|session|project|global|unclear",
      "from_term": null,
      "preferred": null,
      "conflict_group": null,
      "impact": "low|medium|high",
      "term_evidence": {
        "text": "verbatim substring containing the term",
        "occurrence": 1
      },
      "intent_evidence": [
        {"text": "verbatim substring proving intent, polarity, scope, or persistence", "occurrence": 1}
      ],
      "confidence": "high|medium|low"
    }
  ],
  "critic": {
    "status": "confirmed|needs-review",
    "confirmed_frame_ids": [],
    "rejected_frame_ids": [],
    "unresolved_frame_ids": [],
    "missing_frames": []
  }
}
```

Rules for the AI extractor:

1. Return no frame for ordinary prose, an identifier assignment, a proper noun,
   a historical quotation, or an example. A rejected/negated request may be
   omitted; if emitted for audit, mark its polarity accurately.
2. Preserve the user's exact term and exact evidence. Do not invent a preferred
   form during extraction.
3. Represent a rename as one frame with `from_term` and `preferred`; do not
   create two unrelated questions.
4. Give competing forms one `conflict_group` so the local engine can batch
   them as one unresolved decision.
5. Use `unclear` instead of guessing persistence or scope.
6. Enumerate the complete durable inventory for the conversation. A second
   background review explicitly checks for a missed durable decision and a
   spurious frame.

## 4. Local evidence validation

Local VEIL treats AI output as untrusted data. Before policy evaluation it
must:

1. validate the JSON schema and allowed enums;
2. resolve every evidence substring and requested occurrence against the exact
   input text;
3. require the term, `from_term`, and `preferred` values to be supported by the
   cited evidence;
4. reject duplicate frame IDs, impossible mappings, empty terms, and conflict
   groups with fewer than two distinct forms;
5. normalize terms only after evidence validation;
6. read the canonical DB only for exact registered matches; and
7. perform no DB, HTML, Skill, target, Git, or external write.

Invalid frames do not become rules or semantic outcomes. The CLI returns one
structured analysis-stage error with `write_allowed=false`; the Skill may
correct the background payload once. A second validation failure stops with one
concise failure result and no DB, HTML, or sync write. It must not fall back to
raw-text regex as semantic proof.

## 5. Deterministic outcome policy

The local engine maps validated semantic facts, not cue words:

| Validated state | Outcome | User work |
|---|---|---|
| exact registered use, no rename/conflict/requested wording change | `existing-match` | none |
| `polarity=negated` or `reported`, or `persistence=none` | `exclude` | none |
| temporary/one-off definition or low-impact unclear recurrence | `observe` | none |
| affirmed durable adopt/rename/definition | `exception` | one combined question |
| conflict group or high-impact unclear durable decision | `exception` | same combined question |
| no semantic frame and no exact registered match | no decision item | none |

Only an accepted exception mapping may later enter the existing atomic batch
write. Repetition alone never creates a durable rule. One session still has
question count `0` or `1`, regardless of frame count.

## 6. Two-pass background review

The normal Skill performs two internal steps before invoking local policy:

1. **Extractor pass:** produce decision frames and exact evidence.
2. **Critic pass:** inspect the conversation plus frames and return:
   - missing durable decisions;
   - spurious frames;
   - unsupported evidence;
   - unresolved polarity, persistence, scope, or mapping.

The critic does not ask the user. Confirmed frames proceed to local validation;
it may reject spurious extractor frames while retaining `status=confirmed`.
`status=needs-review` is reserved for unresolved or newly found missing frames,
which become one combined `exception`, not a silent resolution. If the AI
surface cannot perform structured extraction, the run stops with an analysis
failure; exact existing-match and raw-text results may be reported as
diagnostic only and must not pretend to prove semantic coverage.

## 7. UX contract

Normal task close:

- no frames or only automatic outcomes: no VEIL-specific output;
- one or more exceptions: one concise combined question containing only the
  unresolved durable decisions and any already supplied preferred forms;
- accepted mappings: one atomic local write, then export and sync;
- failed validation/write/export/sync: one concise failed-stage result.

The HTML remains an optional review/recovery surface. Because static HTML has
no semantic AI, it may copy a structured AI-review request and display returned
validated frames, but it must not claim that its local regex preview proves the
normal-flow decision.

## 8. Implementation surfaces and work order

### Phase A - contract and read-only policy engine

1. Add a dependency-free `DecisionFrame` schema and validator in a new M2
   module.
2. Add deterministic frame-to-outcome policy separately from text extraction.
3. Add CLI JSON input through a file or stdin-safe structured channel; never
   interpolate conversation text into a shell command.
4. Keep contract v1 raw-text outcomes available only as an explicitly marked
   diagnostic during migration.

### Phase B - Skill integration

1. Update Codex and Claude Skills with the same extractor and critic contract.
2. Generate the temporary frame payload in a per-run authorized location,
   validate it locally, read back the result, and remove only that exact
   temporary file.
3. Keep zero-decision runs silent and batch all exceptions once.

### Phase C - HTML and documentation alignment

1. Stop treating browser regex analysis as production semantic proof.
2. Add import/display of validated frame results or copy-to-AI recovery flow.
3. Align README, design authority, locales, and formal Browser E2E with the
   frame contract.

### Phase D - verification

1. Unit-test schema validation, exact evidence resolution, policy mapping,
   rename aliasing, conflict grouping, critic disagreement, and no-write gates.
2. Add mutation/property cases for punctuation, apostrophes, quote styles,
   clause order, negation, scope, and equivalent request wording. These test
   invariants, not memorized phrases.
3. Re-run v1-v3 only as development corpora after implementation.
4. Run full pytest, formal Edge E2E, syntax checks, and `git diff --check` from
   one source state.
5. Freeze a new unseen synthetic end-to-end holdout in which the host AI
   actually produces frames; policy-only fixture success is insufficient.
6. Only after synthetic success, obtain explicit approval for conversation
   scope, anonymization, retention, and two-reviewer handling before any real
   conversation evaluation.

## 9. Completion and stop rules

The redesign is not complete until all of these are true:

- zero high-impact false exclusions and zero unexpected exceptions in a new
  unseen end-to-end holdout;
- every ordinary session has zero questions and every exception session has
  one combined question;
- the extractor/critic evidence can be audited back to exact input text;
- policy and DB behavior are deterministic and no-write before acceptance;
- Python/Skill/HTML/documentation contracts agree;
- approved real-conversation evaluation succeeds before any claim that VEIL's
  overall UX is proven usable.

Until then: no Git release, install, sync, installed-output refresh, remote CI,
or `STALE` remediation.
