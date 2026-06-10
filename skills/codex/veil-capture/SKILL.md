---
name: veil-capture
description: Detect English terms, coined phrases, and abbreviations from AI conversation; record the preferred form to SQLite canonical; regenerate the markdown mirror and sync. Use after a conversation to update vocabulary rules, or pass text as an argument to analyze specific content.
---

# veil-capture

## Output format

Output only the following template.

```
- {term} (current) → {candidate1} (candidate 1) | {candidate2} (candidate 2)

Select current or a candidate.
```

- One line per adopted term
- If candidate 3 exists, append `| {candidate3} (candidate 3)` at the end
- If there are no terms to adopt, output only `Nothing to adopt.` and stop

---

## Term selection criteria

**Scope**
- If an argument is provided, analyze only that string
- If no argument is provided, analyze the full current conversation (both AI and user turns)

**Terms to adopt**
- Terms or compound phrases that appear 2 or more times in the scope
- Prefer state terms, judgment terms, structural terms, and operational labels over bare verbs
- Prefer compound phrases over single words (take the shortest meaningful unit)
- Normalize case, singular/plural, and hyphen/underscore variation before deduplication
- Adopt high-frequency, high-impact terms first; skip the rest

**Terms to exclude**
- Proper nouns: product names, service names, tool names, organization names, official feature names
- Terms inside backticks or double quotes
- `key=value` patterns, identifiers, spec names, command names, paths
- Terms already registered in `~/.veil/veil.db` or `~/.veil/rules/*.md` (case-insensitive)
- Bare general verbs such as close / closed / update
- Terms where a preferred form cannot be decided

**Preferred form guidance**
- Keep established technical English terms as-is when they are already standard (e.g., canonical → canonical (keep), sync → sync (keep))
- Prefer the more precise or concise English term when alternatives exist (e.g., false positive → false positive (keep), validator → validator (keep) | checker)
- Avoid coined compounds when a cleaner English term exists
- Candidate 2 is required; candidate 3 is optional (omit if none)
- One concept, one preferred form

---

## Post-selection processing

After receiving the user's selection, execute the following steps in order. Do not output execution results to the user.

1. Record the selected preferred form using `python shared/tools/veil-db.py upsert-rule --db ~/.veil/veil.db` (include candidates 2 and 3 if present). If `veil.db` does not exist, write directly to `~/.veil/rules/`.
2. Regenerate the mirror using `python shared/tools/veil-db.py export-mirror`.
3. Check `sync_script` in `~/.veil/config.json`; if present, run `shared/runtime/veil-sync.py`.

Report failure in one line and stop only if a step fails.
