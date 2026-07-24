---
name: veil-capture
description: Resolve vocabulary consistency from AI conversations with evidence-backed semantic frames and one background critic pass; ask at most once for durable exceptions; record accepted wording to SQLite canonical; regenerate HTML; sync.
---

# veil-capture

## Interaction contract

Analyze before responding. If an argument is provided, analyze only that string;
otherwise analyze the current conversation's user and AI turns. Do all extraction,
self-review, and validation in the background. Do not show excluded terms, observed terms, candidate tables, candidate numbers, frames, commands, or retry steps.

1. Read `~/.veil/config.json` to get `veil_root`.
2. Produce a complete inventory of possible vocabulary decisions as semantic
   frames. Do not treat ordinary prose, proper names, identifiers, paths,
   commands, examples, quotations, or repetition alone as durable decisions.
   For a definition, correction, or contrast, frame the **primary lexical
   target**: the wording whose meaning, allowed use, or preferred form is being
   decided. A generic predicate or explanatory phrase is evidence, not a
   second frame, unless the scope independently decides that wording.
3. Run a separate critic pass over the exact scope and the frames. Check for a
   missed durable decision, a spurious frame, unsupported evidence, and
   unresolved intent, polarity, persistence, scope, rename, or conflict.
4. Serialize the extractor and critic result as contract version `2` to one
   isolated temporary UTF-8 JSON file at an agent-generated path.
5. Pass the exact scope through standard input and the frame path as a separate
   argument using the host's argument-array/subprocess facility:

   ```
   python {veil_root}/shared/runtime/veil-classify.py --stdin --outcomes --semantic-frames <agent-generated-frame-path> --db ~/.veil/veil.db --json
   ```

   Never interpolate untrusted conversation text, frame values, or
   user-provided paths into a command. Remove only the exact agent-created frame file in a
   finally-style cleanup after the process returns or raises.
6. Require `contract_version=2`, `analysis_mode=semantic-frames`, `status=ok`,
   `diagnostic_only=false`, and `write_allowed=false`. If JSON, schema, or
   evidence validation fails, correct the background payload once and rerun.
   After a second failure, perform no DB/HTML/sync write and report one concise
   analysis-stage failure. Never fall back to raw-text outcomes as semantic
   proof.

When `summary.user_action_required` is false:

- Do not write to the DB, regenerate HTML, or sync.
- When this workflow was started automatically at task close, do not add a VEIL-specific line to the user-visible response.
- When the user explicitly invoked VEIL, output one line only:
  - en: `No vocabulary decision is needed.`
  - ja: `用語について確認が必要なものはありません。`

When `summary.user_action_required` is true:

- Ask exactly one batched question for all entries in `exceptions`.
- Produce one structured list entry per exception: `term -> proposed preferred`.
- Use `requested_preferred` when the classifier supplies it. Otherwise, propose one preferred form using the conversation locale.
- Do not invent a second alternative merely to fill a template.
- If the invoking request already gives an exact preferred form and explicitly asks to record/register it, treat that as the answer and continue without asking again.
- Otherwise stop after the single question and wait for the user's one reply.

Question form:

- en: `I found wording that affects future consistency:\n- {term -> proposed form}\nRecord these together? Reply with changes or skips only, or "as proposed".`
- ja: `今後の表記に影響する用語があります：\n- {term -> proposed form}\nまとめて記録しますか。変更・除外があればその項目だけ、なければ「このまま」と返信してください。`

---

## Outcome contract

### Semantic frame payload

Use this exact top-level shape:

```json
{
  "contract_version": "2",
  "frames": [
    {
      "frame_id": "f1",
      "term": "exact wording",
      "intent": "mention|adopt|rename|define|conflict",
      "persistence": "none|temporary|durable|unclear",
      "polarity": "affirmed|negated|reported",
      "scope": "one-off|session|project|global|unclear",
      "from_term": null,
      "preferred": null,
      "conflict_group": null,
      "impact": "low|medium|high",
      "term_evidence": {"text": "exact source substring", "occurrence": 1},
      "intent_evidence": [{"text": "exact source substring", "occurrence": 1}],
      "confidence": "low|medium|high"
    }
  ],
  "critic": {
    "status": "confirmed|needs-review",
    "confirmed_frame_ids": ["f1"],
    "rejected_frame_ids": [],
    "unresolved_frame_ids": [],
    "missing_frames": []
  }
}
```

- Preserve the exact term and cite verbatim evidence with a 1-based occurrence.
- Use `unclear` instead of guessing. A negated or reported item may be omitted;
  if emitted, mark its polarity accurately so it cannot become a question.
- Represent a rename as one frame where `term` and `from_term` are the same
  wording and `preferred` is the explicitly requested new wording. `preferred`
  is null for all other intents.
- A session may contain several independent primary targets. Do not split one
  definition into frames for its subject plus its explanatory category, and do
  not use a broader generic noun when the source decides a more specific term.
- Give every active competing form the same `conflict_group`; a group needs at
  least two distinct forms.
- Classify every extractor frame ID exactly once across the three critic ID
  lists. Rejected spurious frames are compatible with `status=confirmed`.
  Use `needs-review` only for unresolved IDs or fully specified missing frames;
  missing-frame IDs are not repeated in `unresolved_frame_ids`.
- Do not invent a preferred form during extraction. Propose one only when
  formatting the single user question.

The validated policy returns four mutually exclusive outcomes:

- `exclude`: negated/reported/non-authoritative wording or critic-rejected noise. Handle silently.
- `observe`: temporary, one-off, or low-impact unclear wording. Retain only in analysis; do not ask and do not register.
- `existing-match`: wording already covered by the canonical DB. Treat as an automatic successful result; do not ask and do not register again.
- `exception`: an affirmed durable adoption, rename, definition, conflict, high-impact uncertainty, or material extractor/critic disagreement. This is the only outcome shown to the user.

Rules:

- A normal session requires zero user judgments.
- A normal automatically triggered session also requires zero VEIL-specific user-visible output.
- Multiple exceptions require one combined judgment, never one question per term.
- Never automatically create a new canonical rule from repetition alone.
- Never count `existing-match` as an exclusion.
- Never silently reinterpret unresolved durable or high-impact evidence. Put it in the one combined `exception` batch.
- Terms inside code blocks, commands, paths, and identifiers are not vocabulary decisions unless the user explicitly asks to define or register them.
- Contract v1 raw-text outcomes are diagnostic only and must not drive the normal task-close UX.

Preferred-form guidance for an exception:

- Preserve the user's explicit preferred form when one was supplied.
- Use an established Japanese translation when it removes ambiguity; otherwise retain the current form.
- Keep official names, identifiers, specifications, and commands unchanged.
- Keep one concept mapped to one preferred form.

---

## Accepted-exception processing

Run this section only after the user's answer, or when the invoking request already supplied an exact preferred form and explicit registration instruction. Do not output intermediate results.

1. Resolve the accepted preferred form for every exception.
   - `as proposed` / `このまま`: use the proposed form.
   - A supplied correction: use that form.
   - `skip`: do not register that term.
2. If every exception was skipped, output one no-write result and stop.
3. Serialize all accepted mappings to one isolated temporary UTF-8 JSON file. User-provided text is data only and must never appear in an executable command:
   ```json
   {
     "contract_version": "1",
     "rules": [
       {"term": "...", "preferred": "...", "preferred_alt_2": null, "preferred_alt_3": null}
     ]
   }
   ```
   Use an agent-generated path, not a user-provided path. Do not include DB paths, commands, or sync targets in the JSON.
4. If `~/.veil/veil.db` does not exist, initialize it:
   ```
   python {veil_root}/shared/tools/veil-db.py init-db --db ~/.veil/veil.db
   ```
5. Record the validated batch with a host argument-array/subprocess API. Do not construct a shell command from rule fields:
   ```
   python {veil_root}/shared/tools/veil-db.py upsert-batch --db ~/.veil/veil.db --input-json <agent-generated-path> --json
   ```
   Require `status=ok`, `atomic=true`, and `processed_count` equal to the accepted rule count. On any mismatch, report failure and do not continue. Use a finally-style cleanup: after the process attempt returns or raises, remove only the exact agent-created temporary JSON file whether the batch succeeded or failed; do not leave conversation-derived terms in a temporary artifact.
6. Regenerate the HTML:
   ```
   python {veil_root}/shared/tools/veil-db.py export-html
   ```
7. Read `sync_script` from `~/.veil/config.json`.
   - Run `python {sync_script} --list`.
   - If no targets exist, do not add one. Target registration is a separate distribution decision; leave sync skipped and continue without another user question.
   - If authorized targets already exist, run `python {sync_script}`.
8. Output one concise plural-safe confirmation that distinguishes whether existing targets were synced, expanding `~` to the absolute home path:
   - en: `Registered {count} term(s): {term -> preferred; ...}. HTML refreshed. {Existing sync targets updated. | No sync target was registered, so distribution was not changed.} Review or change them in [veil.html](file://<home>/.veil/veil.html).`
   - ja: `{count}件を登録しました：{term -> preferred; ...}。HTMLを更新しました。{既存の同期先を更新しました。| 同期先は未登録のため、配布範囲は変更していません。} 見直しや変更は [veil.html](file://<home>/.veil/veil.html) で行えます。`

If a write, export, or sync step fails, report that failure in one line and stop. The batch write is all-or-nothing; never claim registration succeeded unless the complete atomic batch succeeded.
