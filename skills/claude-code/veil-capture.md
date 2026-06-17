# veil-capture

## Output format

Output only the following template.

```
- {term} (current) → {candidate1} (candidate 1) | {candidate2} (candidate 2)
```

- One line per adopted term
- If candidate 3 exists, append `| {candidate3} (candidate 3)` at the end
- If there are no terms to adopt, output only `Nothing to adopt.` and stop
- After the list, output exactly one of:
  - en: `Candidate 1 will be registered for each. To override, reply with the term and your choice (e.g. "current state → keep current"). Reply OK to proceed.`
  - ja: `各語の候補1を登録します。変更したい場合は語と選択肢を返信してください（例: "current state → 現状のまま"）。そのまま進む場合はOKと返信してください。`

**Locale override (ja):** Use `（現状）`, `（候補1）`, `（候補2）` labels instead of English equivalents.

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
- Industry-standard technical terms: candidate 1 = katakana (ja) or kept as-is (en)
- Terms with established Japanese translations: candidate 1 = Japanese (e.g., false positive → 誤検知)
- English-only terms: identifiers, official names, spec names, command names
- Candidate 2 is required; candidate 3 is optional (omit if none)
- One concept, one preferred form

---

## Post-selection processing

After receiving the user's selection, execute the following steps in order. Do not output intermediate results.

Read `~/.veil/config.json` to get `veil_root` (the absolute path to the veil repo). Use it for all commands below.

1. Record the selected preferred form:
   ```
   python {veil_root}/shared/tools/veil-db.py upsert-rule --db ~/.veil/veil.db \
     --term "{term}" --preferred "{candidate1}" \
     [--preferred-alt-2 "{candidate2}"] [--preferred-alt-3 "{candidate3}"]
   ```
   Pass each candidate as a separate flag. Do NOT pass `|`-separated strings as `--preferred`.
   If `~/.veil/veil.db` does not exist, first run `python {veil_root}/shared/tools/veil-db.py init-db --db ~/.veil/veil.db`.
2. Regenerate the mirror using `python {veil_root}/shared/tools/veil-db.py export-mirror`.
3. Regenerate the HTML using `python {veil_root}/shared/tools/veil-db.py export-html`.
4. Read `sync_script` from `~/.veil/config.json`.
   Check if any sync targets are registered with `python {sync_script} --list`.
   If no targets are listed, scan the current working directory for AI config files
   (CLAUDE.md, AGENTS.md, GEMINI.md, .cursorrules, .aider.conf.yml, .github/copilot-instructions.md)
   and register the first found with `python {sync_script} --add <path>` (siblings auto-register).
   Then run `python {sync_script}`.
5. Output confirmation (expand `~` to the actual absolute home directory path):
   - en: `{selected} registered. To review or modify terms, see [veil.html](file://<home>/.veil/veil.html).`
   - ja: `{selected}で登録しました。登録語句を閲覧や修正したい場合は、[veil.html](file://<home>/.veil/veil.html)で確認してください。`

Report failure in one line and stop only if steps 1–4 fail.
