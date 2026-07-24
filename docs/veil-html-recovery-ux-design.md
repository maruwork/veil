# VEIL HTML recovery UX redesign

Status: implementation candidate verified locally; exact-scope commit, hosted checks, commit-derived delivery, and human UX acceptance pending
Date: 2026-07-24
Owner: `docs/veil-design.md` remains the primary design authority. This document fixes the detailed HTML design that it adopts.

## 1. Decision

The generated HTML is **not** a vocabulary classifier, a semantic-review
engine, or an alternate normal workflow. It is a local, static **Rulebook and
Recovery** surface.

The one normal user journey stays outside the browser page:

```text
substantive task close
  -> installed VEIL Skill analyzes the conversation in the background
  -> no durable decision: no VEIL UI
  -> durable exception: one combined confirmation
  -> accepted atomic update -> DB -> HTML export -> sync
```

The browser is opened only when the user intentionally wants to inspect an
existing rule, correct a rule, or recover a review from a chat surface where
the normal Skill route is unavailable.

The current raw-text regex preview, candidate extraction, candidate loading,
draft-output copy, AI-prompt copy, and command-copy paths are removed from the
product surface. They must not be hidden behind an advanced accordion; they are
not part of this product journey. Regression-only diagnostic code may remain
outside generated HTML until separately retired, but no generated page may
invoke or embed it.

## 2. Product contract

### User promise

- Ordinary conversations require no visit to this page.
- The page never decides whether a term should become a rule.
- The page never writes to the DB, sync targets, or the network.
- A recovery review always sends the exact pasted conversation to the installed
  Skill in one action; it does not reduce it to browser-generated candidates.
- A rule change request is explicit, reviewable, and becomes effective only
  after the Skill's confirmation and atomic DB/export/sync processing.

### Explicit non-goals

- No client-side semantic classification, raw-text outcome labels, or local
  "safe/no issue" conclusion.
- No candidate table, candidate count, ranking, or per-term review workflow.
- No direct SQLite write or shell-command teaching in the main UI.
- No replacement for the installed Skill at task close.
- No claim that a user reading the page has completed vocabulary review.

## 3. Information architecture

The page has two top-level sections, in this order. There are no tabs whose
meaning must be learned before the primary action is visible.

### A. Rulebook (default and first focus)

Purpose: inspect the canonical rules currently delivered to AI tools.

Elements:

1. Title: `VEIL rulebook`.
2. A short immutable status line: rule count and the HTML generation timestamp.
   It says that the canonical source is VEIL's local rule store and that this
   page is a view/request surface.
3. One search field filtering source term, preferred form, and alternatives.
4. A compact rule list with only:
   - source wording;
   - preferred wording;
   - optional alternatives collapsed under `Show alternatives`;
   - a `Request change` action for that row.
5. Empty search state: `No matching rule. To review new wording, use Review a
   conversation below.`
6. Empty rulebook state: `No rules are registered yet. VEIL normally asks only
   when a durable choice is needed.`

The list has no per-alternative copy buttons and no delete icon. Copying an
individual phrase is not a user goal; correcting the rule is.

### B. Actions (below Rulebook)

This section contains exactly two visually equal actions, each with a concise
statement of when to use it.

#### 1. Review a conversation

Use only for recovery/on-demand review.

- A multiline field accepts exact conversation text.
- The single primary button is `Copy review request`.
- Clicking it copies a fixed, chat-ready request that contains the exact text
  and tells the installed Skill to perform the contract-v2 semantic-frame and
  critic workflow.
- Empty input disables the button and explains what is needed.
- Clipboard failure opens an accessible manual-copy dialog containing the same
  full request.
- The page keeps the text in memory only; reload clears it. It does not write
  local storage, URL fragments, analytics, a file, or the DB.

There is no Analyze, Preview, Draft output, candidate selection, or second
prompt button.

#### 2. Request a rule change

Use when the user already knows a registered rule is wrong or needs retirement.
It is not used to discover a new rule from arbitrary text.

- `Request change` on a row opens this form with the current mapping prefilled.
- The form has an intent selector with exactly `Change preferred wording` and
  `Retire this rule`; the selected term remains visible and immutable.
- For a change, the user enters one new preferred wording and an optional
  concise reason. For retirement, the user confirms the term and may add a
  reason. There are no alternative slots in the normal form.
- One button, `Copy change request`, copies a structured natural-language
  request for the installed Skill. It includes the current mapping, requested
  operation, exact requested replacement when applicable, and the user's
  reason.
- The Skill performs the confirmation/atomic update/export/sync. The browser
  never claims that the request was saved.
- Completion copy says: `Paste this into an AI chat with VEIL installed. The
  rule changes only after its confirmation.`

A direct CLI path may be documented for administrators in repository
maintenance documentation. It is not rendered in the generated user HTML.

## 4. Interaction and state model

| State | User-visible behavior | Permitted action |
|---|---|---|
| Rulebook ready | list and search are usable | search; open a change request; open recovery review |
| Search empty | no result message, no suggested candidates | clear search; open recovery review |
| Recovery empty | button disabled | paste exact conversation |
| Recovery ready | one copy action | copy full review request |
| Recovery copied | transient confirmation; no result or verdict | paste into an installed AI chat |
| Clipboard unavailable | manual-copy dialog | select/copy exact same request |
| Change form invalid | explain the missing field inline | provide one preferred wording or confirm retirement |
| Change request copied | transient confirmation; no saved claim | paste into installed AI chat |
| Stale/missing delivery | not inferred by page JavaScript | `veil-status --check` reports it; reinstall/export is an operator action |

The static page must never present a semantic result state. The only results
belong to the Skill after it validates frames and critic output.

## 5. Content and visual rules

- The default page is Rulebook, not a large textarea or an "AI review" panel.
- The recovery action is below the rules and labelled as on-demand recovery.
- One purpose per button. Every button either opens one form or copies one
  complete request; no two buttons produce variants of the same request.
- Use task language, not implementation language: `Review a conversation`,
  `Request change`, `Retire this rule`. Do not show `raw-text`, `regex`,
  `contract v1`, `semantic frame`, `CLI`, or `diagnostic` in normal UI copy.
- Keep Japanese and English as required release locales. Other currently
  shipped locale bundles may be retained only if every new string is complete;
  otherwise the page falls back to English rather than serving mixed-language
  controls. Locale support is not a substitute for UX acceptance.
- Keyboard path: search -> first result -> Request change -> form fields ->
  Copy change request. All controls have visible focus and accessible labels.
- The generated HTML must stay readable without JavaScript: rule list and
  explanatory text remain visible; only filtering, dialogs, and clipboard
  conveniences require JS.

## 6. Data and authority boundaries

```text
HTML (static, read-only) --copy request--> installed VEIL Skill
                                           -> semantic validation / critic
                                           -> one confirmation when required
                                           -> atomic DB update
                                           -> export HTML + sync targets

~/.veil/veil.db = canonical source
~/.veil/veil.html = generated view and request surface
```

The exporter receives only active canonical rules and generation/freshness
metadata. It does not receive capture taxonomy, raw diagnostic allowlists,
phrase heuristics, or classifier payloads. Removing those payloads from the
HTML is both a UX simplification and a reduction in stale duplicated policy.

A change-request envelope is a request to the Skill, not an authority record.
The implementation must use an isolated, validated input file when it converts
a confirmed change or retirement into DB operations. User-supplied strings must
never become shell syntax. Every operation includes the exact
`current_preferred` value shown for confirmation; the DB compares it inside the
same transaction and rejects the complete batch as stale if canonical changed.

## 7. Required implementation changes

1. Replace the generated template with the two-section layout above.
2. Delete the generated-page capture analyzer and all related UI controls,
   taxonomy payload injection, candidate rendering, and copy variants.
3. Retain only generic JavaScript: locale selection, search/filter, dialog
   state, request construction, clipboard/manual-copy fallback, and form
   validation.
4. Replace row copy/delete controls with `Request change`.
5. Add one Skill-supported rule-maintenance request contract covering change
   and retirement, including confirmation, atomic update, HTML export, sync,
   and failure reporting.
6. Update README, `docs/veil-design.md`, and capture-classification guidance so
   the HTML has one consistent role.
7. Remove tests that assert the retired diagnostic UI. Replace them with tests
   for the new journeys; do not preserve obsolete behavior merely for coverage.
8. Regenerate `~/.veil/veil.html` only after the source implementation and
   new acceptance tests are green.

## 8. Acceptance design

### Automated acceptance

The browser runner must demonstrate all of the following:

1. Rulebook opens first; search filters correctly; no-result state routes to
   recovery without suggesting vocabulary candidates.
2. Generated HTML contains no local analyzer invocation, raw outcome label,
   candidate rendering, diagnostic preview control, draft-output copy control,
   AI-prompt copy control, command-copy control, or delete command.
3. Recovery with text has exactly one primary action; copied text preserves the
   complete input and instructs the installed Skill route.
4. Recovery with empty text cannot copy a request; clipboard fallback exposes
   the identical request.
5. Row change opens a prefilled form; a valid change or retirement produces one
   unambiguous request; invalid forms cannot copy a request.
6. The browser makes zero direct DB/network/write attempts.
7. Japanese and English controls are complete and keyboard-operable.
8. HTML is generated from canonical rules and remains fresh under
   `veil-status --check --json`.

The local candidate acceptance completed on 2026-07-25 with 339 tests passed,
zero failures, and zero skips. The real-browser runner exercised the documented
route with browser key events, including Tab, Shift+Tab, Enter, Space, and
select changes. A disposable integration acceptance exercised one shared row
contract through confirmed maintenance JSON, atomic DB update, stale detection,
HTML regeneration, retired-rule hiding, and final manifest freshness.

Those results identify the candidate source content by SHA-256
`7d212b41f541c5448254a685bf61328f0da00cbd8198118cf6304d50f73cd7d3`.
They were produced before an exact-scope commit and therefore are local
candidate evidence, not release evidence. Release evidence must be regenerated
from the fixed commit, pass hosted checks for that revision, and record the
commit-derived live delivery separately.

### Human UX acceptance

Use the fixed [five-person execution protocol](governance/20260725-veil-human-ux-acceptance-protocol.md).
It creates a disposable fixture and fail-closed anonymous result report; it
does not write to the canonical DB or turn a human-UX pass into a product
release claim.

Before product release, use at least five target users who did not author the
page. Give each the same three tasks without explaining the page structure:

1. Find whether an existing wording has a preferred form.
2. Correct that preferred form.
3. Send an arbitrary conversation for review.

Pass criteria:

- at least four of five complete each task without moderator navigation help;
- zero participant uses a local page result as proof that no review is needed;
- zero participant believes copying a request has already saved a rule;
- at least four of five can correctly state when they should *not* open HTML;
- observed confusion is resolved in the design, not explained away in help
  text.

### Release gate

Release is `not-ready` until the automated acceptance passes, human acceptance
passes, the normal Skill route remains silent for no-decision conversations,
and the final source revision passes local and hosted delivery checks. The v15
seven-case semantic-core evidence remains valid only for its narrow policy
claim; it is not HTML UX acceptance evidence.

## 9. Migration and evidence rules

- Existing `~/.veil/veil.db` data is unchanged.
- Existing generated HTML is replaced only by the exporter after source and
  acceptance work complete; never hand-edit it.
- Existing v12, v14, and v15 frozen evaluation evidence is immutable and is
  neither regenerated nor reused as proof of this HTML design.
- The current L4 release-readiness revocation remains active until the above
  release gate is satisfied by a separate, bounded acceptance record.
