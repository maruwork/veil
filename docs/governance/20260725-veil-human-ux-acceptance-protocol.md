# VEIL five-person HTML UX acceptance protocol

Status: optional post-release research packet; no participant results have been recorded.

## Purpose and boundary

This is optional post-release research for the static Rulebook and Recovery
HTML page. It does not evaluate semantic classification, v12--v15 frozen
evidence, normal Skill performance, or release readiness. The coordinator must not
represent a synthetic, staff, or author session as a target-user result.

Run the protocol only against a fixed, committed source revision. Create a
disposable fixture; it contains one synthetic rule and never writes to the
canonical DB, installed HTML, installed Skills, or sync targets.

```powershell
python shared/tools/veil_human_ux_acceptance.py prepare `
  --output-dir workspace/audit/<run-id>/human-ux-fixture
```

Give every participant the generated `veil-human-ux.html`. Do not explain the
page layout, its two routes, VEIL terminology, or a workaround before the
tasks. Do not paste any copied request into an AI chat.

## Participants and session controls

- Use exactly five independent target users who did not author the page or
  implementation.
- Run one session per participant; do not let participants watch each other.
- Record only anonymous IDs such as `P01`; never record names, employer,
  contact details, transcripts, screenshots, or free-text notes in the result.
- The moderator may repeat the task verbatim and may resolve a technical page
  loading failure. The moderator must not show a control, name a route, tell a
  participant where to look, or explain a product concept.
- If moderator navigation help is needed, record it and continue. It is a
  fail-closed result, not a reason to replace the participant.

## Verbatim tasks

Present these one at a time, without describing the page structure.

1. `Find whether “current state” has a preferred form. Tell me the preferred form.`
2. `The preferred form for “current state” is wrong. Use this page to request changing it to “current condition”. Do not paste the copied request anywhere.`
3. `Use this page to prepare a review request for this exact conversation: “We should consistently use the decision boundary in the release discussion.” Do not paste the copied request anywhere.`

After all tasks, ask:

1. `If this page shows no matching rule, does that prove no review is needed?`
2. `Did copying a request save or change a rule?`
3. `When should you not open this page?`

The moderator records only the predefined boolean answers and any predefined
confusion code. A correct answer to the last question is that ordinary task
close / normal conversation review belongs to the installed Skill, not this
recovery page.

## Result file and decision

Copy `records-template.json` to `records.json` and record the five sessions.
Then run:

```powershell
python shared/tools/veil_human_ux_acceptance.py evaluate `
  --fixture-manifest workspace/audit/<run-id>/human-ux-fixture/fixture-manifest.json `
  --records workspace/audit/<run-id>/human-ux-fixture/records.json `
  --output workspace/audit/<run-id>/human-ux-report.json
```

The evaluator is fail-closed. It returns `human-ux-passed` only if all five
sessions bind to one fixture/source, every task succeeds without moderator
navigation help for at least four participants, both misconception counts are
zero, at least four participants know when not to open HTML, and no design
confusion is observed.

Any observed confusion returns `requires-revision`. The remedy is a design
change followed by a new committed source revision and a fresh five-person
run; a help-text explanation or reuse of prior participant records is not
valid. Human research does not change release status; delivery and hosted
release gates are evaluated separately.
