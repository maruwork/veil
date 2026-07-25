# VEIL work record — HTML delivery and semantic evaluation boundary

Date: 2026-07-25

## Operational HTML delivery

The committed HTML delivery scope is complete at
`361a1eb39d61ad32cf399991da6862c2979663af`.

- Canonical release qualification:
  `workspace/audit/20260725-operational-release/qualified-release-qualification.json`
  records `verdict=release-ready` for the declared operational scope.
- That scope is limited to operational delivery and static Rulebook/Recovery.
  It does not assert general semantic accuracy or human-UX research.
- A live `python shared/runtime/veil-status.py --check --json` check on
  2026-07-25 reported `OK` for the DB, generated HTML, targets, sync target,
  Claude Skill, and Codex Skill.
- The delivered HTML was re-inspected with its template, localized assets,
  exporter, freshness manifest, delivery acceptance, browser runner, release
  gate, and the two installed Skill contracts.  It has a static Rulebook plus
  exactly two request paths: review a complete conversation and request a
  change or retirement of an existing rule.  It has no direct DB write,
  network client, browser persistence, candidate UI, or local classifier.
- The focused acceptance suite passed (`4 passed`), and the real-browser E2E
  passed on the same checkout.  The E2E covered complete-text copy, clipboard
  fallback, change and retirement requests, English/Japanese UI, native
  keyboard controls (Tab, Shift+Tab, Enter, Space), and zero direct-write
  attempts.

## Semantic evaluation boundary

No general semantic-accuracy claim is authorized by the current evidence.

- v12-v15 frozen evidence remains immutable and is not reused or repaired.
- v16-v19 are preserved as non-passing bounded evaluation attempts.
- v20 collected a fresh, typed Claude/Codex history snapshot and used an
  independent anchor-backed label contract.  The freeze gate returned
  `source-insufficient` with independent anchor counts:
  `exception=24`, `exclude=7`, `existing-match=0`, `observe=1`.
- No 25-by-4 frozen set, blind-generation run, or semantic evaluation verdict
  was created from v20.  Do not re-label, repair, or reuse its input/output to
  turn that result into a passing evaluation.

Any future broad semantic claim requires separately authorized fresh natural
conversation material with enough independently labelable examples for all
four outcomes.  It is not a release dependency for the completed HTML
operational scope.

## Repository boundary

This record makes no product-code or deployed-HTML change.  User-owned
untracked `.trash-migration/` and `archive/` remain outside the commit.
