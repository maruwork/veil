# VEIL UX and vocabulary-quality proposal

**Status:** proposed - no implementation authorized by this record  
**Recorded:** 2026-07-19  
**Scope:** VEIL capture, registration, generated review HTML, and verification flow

## Decision summary

Keep VEIL's core flow narrow:

```text
capture -> select preferred form -> record -> sync -> lint
```

Do not make `semantic-generation` or a referent table part of VEIL's normal
registration route. They solve a separate, design-time naming problem and would
add disproportionate ceremony to ordinary vocabulary consistency work.

The one proposed simplification is to make **Candidate 2 optional in
`veil-capture` output**. Keep Candidate 2 and Candidate 3 storage and review
support; do not require the model to invent an alternative where one clear
preferred term exists.

## Evidence

### Candidate 2 requirement is not aligned with enforcement

- The installed capture skills currently require Candidate 2.
- The canonical store and `upsert-rule` interface already accept Candidate 2
  and Candidate 3 as optional values.
- Only `preferred` is propagated by `veil-sync.py` and enforced by
  `veil-lint.py`; alternatives are not synced or lint-enforced.
- The current local profile has three active rules, and only one retains a
  Candidate 2 value.

Forcing Candidate 2 therefore adds an LLM-generated choice without adding an
enforcement benefit. It can create weak synonyms, blur the one-preferred-form
contract, and increase review work.

### Capture and classification remain quality boundaries

Do not remove Draft Capture, the classifier, or the chat-side confirmation
route. Together they prevent specialist terms, identifiers, paths, and other
low-signal strings from being casually persisted as vocabulary rules. Capture
also requires repeated signal for ordinary adoption candidates.

### Current HTML parity is a prerequisite to UX judgment

The configured `veil_root` is this repository, but the current
`~/.veil/veil.html` has an earlier registration UI than the working-tree source
and current documentation. The status check confirms that the HTML exists, but
does not verify that it was generated from the current runtime source.

Do not make a larger visual or flow simplification decision until the delivered
HTML, source, and documentation represent the same version.

## Proposed work order

1. Change the capture-skill contract so Candidate 2 is optional; retain
   optional alternatives in the DB, CLI, and review HTML.
2. Add a deterministic freshness or source-version check for generated
   `~/.veil/veil.html`, then regenerate it as part of the verified delivery
   path.
3. Add browser-level acceptance coverage for the generated HTML's capture,
   registration-request, manual-command, and delete-copy paths. Current tests
   primarily assert generated markup and strings.
4. Clear or deliberately retain the stale sync target reported by
   `veil-status --check` so routine diagnostics do not normalize warnings.
5. Observe actual use before changing the visibility or existence of Candidate
   2/3 fields, Draft Capture, or the two registration routes.

## Explicit non-proposals

- Do not add a mandatory referent table or semantic-generation gate to normal
  VEIL registration.
- Do not delete Candidate 2/3 storage based on the current small profile.
- Do not remove Draft Capture or classification solely to make the HTML look
  lighter.
- Do not replace the copy-based review flow with direct browser writes without a
  separate authority and safety decision.

## Verification snapshot

- Full test suite passed in an isolated temporary base directory:
  `187 passed`.
- The repository-default pytest temporary path was inaccessible in the current
  Windows environment, causing setup failures; this is a test-environment
  reliability issue rather than an application-logic failure.
- Python compilation for `shared/` and `tests/` passed.
