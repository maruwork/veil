# VEIL Capture Classification

This document defines three separate layers:

1. first-pass labels answer `What kind of string is this?`;
2. contract v1 raw-text outcomes provide lexical diagnostics; and
3. contract v2 semantic decision frames answer `Does the user need to decide anything?`.

Labels and raw-text outcomes never authorize registration. The primary UX
contract is `analyze_decision_frames()` / `veil-classify.py --outcomes
--semantic-frames <path>`. The host AI extracts evidence-backed frames and runs
a separate critic pass; local VEIL validates the untrusted payload and applies
the deterministic outcome policy.

## Outcome contract

- `exclude`: validated negated, reported, non-authoritative, or critic-rejected wording. Silent and non-persistent.
- `observe`: validated temporary, one-off, or low-impact unclear wording. Silent and non-persistent.
- `existing-match`: exact canonical coverage. Automatic success; never count it as exclusion.
- `exception`: affirmed durable adoption, rename, definition, conflict,
  high-impact uncertainty, or material extractor/critic disagreement. The only
  user-visible state.

Every run exposes `user_action_required` and `question_count`. Normal runs have `question_count=0`; any number of exceptions is batched into `question_count=1`. No outcome writes to the canonical DB. The Skill writes only after an explicit exception is accepted or the invoking request already supplied an exact preferred form and explicit registration instruction.

Fail-closed rules for the normal semantic route:

- raw repetition or taxonomy membership -> no durable semantic frame
- negated/reported/non-authoritative evidence -> `exclude`
- temporary/one-off or low-impact unclear evidence -> `observe`
- exact registered term -> `existing-match`
- affirmed durable or high-impact unresolved evidence -> `exception`
- invalid semantic payload -> structured analysis failure, no raw-text fallback,
  no DB/HTML/sync write
- never auto-register a new rule from a frame, taxonomy, fixture, or repetition

### Primary lexical target

For a definition, correction, or contrast, the frame term is the primary
lexical target: the wording whose meaning, allowed use, or preferred form is
being decided. A generic predicate or explanatory phrase is cited as evidence,
not emitted as another frame, unless the source independently decides that
wording. A session can contain several independent primary targets, but not
several labels for one definition.

## Labels

- `industry_term`
  - Industry or specialist term.
  - VEIL still classifies this, but it is a non-target bucket for registration.
- `coined_or_shortened`
  - Project-local coined wording, shorthand, or compressed phrase.
- `file_config_identifier`
  - File name, path, glob, config name, acronym-like identifier, or machine-processed token.
- `other`
  - Ordinary word or phrase that does not look like a useful terminology target.
- `unknown`
  - Still unclear after first-pass rules because the string remains ambiguous or underspecified.

## Current rule direction

- Prefer `file_config_identifier` when the string is clearly mechanical.
- Do not treat an all-caps status or ordinary word as `file_config_identifier` unless it is actually a known acronym-like identifier such as `CI`, `README`, or `SE`.
- Prefer `industry_term` for known specialist terms such as `migration`.
- Prefer known workflow or VCS terms such as `branch`, `mainline`, `checkpoint`, and `normalize` as `industry_term`.
- Treat CI/process-specialist terms such as `workflow` as `industry_term` when they name concrete engineering mechanics rather than just broad status words.
- Treat handoff/runtime engineering terms such as `console`, `scope`, `dataset`, `endpoint`, `readback`, `ruleset`, `OAuth`, `secret`, and `token` as `industry_term`.
- Treat concrete platform/configuration mechanics such as `base URL` and `branch protection` as `industry_term`.
- Do not surface `industry_term` items as VEIL registration candidates just because they are known or repeated.
- Prefer `coined_or_shortened` for project-local phrasing such as `root clutter` or `maintainer-only files`.
- Prefer explicit coined phrase matches over broad suffix or hyphen heuristics, so ordinary bigrams do not get mislabeled.
- Allow a small known list of multiword file/config phrases to be extracted even when they appear as plain words, so schema-like labels such as `guided path` or `trial packet` are not missed.
- Treat known hyphenated local names such as `veil-capture` explicitly instead of treating every hyphenated word as coined wording.
- Strip Markdown link destinations before extraction so `[label](path)` contributes `label` without path-fragment noise.
- Strip `(line 190)`-style reference suffixes before extraction so file references do not leak `line` noise.
- Skip bare one-letter tokens during extraction so outline markers such as `A` or `X` do not survive as fake unknown terms.
- Use `other` for broad ordinary words such as `review`.
- Use `other` for low-signal prose singles such as `this`, `would`, `skill`, `setup`, `selected`, or `validation` so they do not linger as fake unresolved terminology.
- Use `other` for session-log residue such as `sandbox`, `connector`, `markdown`, `agentic`, `dogfooding`, user handles, and similar non-target prose singles.
- Use `other` for VEIL work-session prose residue such as `classification`, `classifier`, `extractor`, `handover`, `locale`, `patching`, and `polishing` when they are being mentioned as conversation wording rather than as terms to register.
- Use `other` for trailing utility prose such as `validate` and `static` when they appear as plain wording rather than product labels or config keys.
- Treat obvious proper nouns such as `GitHub` or `PowerShell` as `other` when they are clearly outside the target categories.
- Use `unknown` only when the first pass still cannot tell what kind of term it is.
- Legacy candidate extraction remains available for regression and compatibility. Its repeated-term allowlists do not define the user interaction and do not authorize registration.
- The HTML review panel is an optional recovery surface. Its regex preview is
  contract v1 `raw-text-diagnostic` and cannot prove semantic coverage. The
  primary action copies the complete text for the installed AI Skill; preview
  entries may be loaded only for manual fine-tuning after AI review.
- Python and HTML/JS raw-text diagnostics remain in lockstep only as regression
  evidence. They are not evidence that arbitrary conversations are understood.

## Chat seed input

`shared/runtime/veil-classify.py` can also read chat transcript JSON with `--chat-json`.
That lets VEIL reuse a conversation export directly instead of requiring manual copy-by-copy term entry first.

The chat-json reader accepts nested transcript shapes through keys such as
`messages`, `conversation`, `turns`, `items`, and `parts`, then reads textual
content from keys such as `text`, `content`, `value`, `message`, and `body`.
Blank segments are dropped, but textual segments remain in input order and keep
their repeated occurrences before classification.

The primary mode is `--outcomes --semantic-frames <path>`. The source text is
passed separately through stdin, a file, or `--text`; the semantic-frame JSON
path is agent-generated and passed as a separate argument. The CLI also retains
diagnostic modes:

For a frozen blind evaluation, the generator's JSONL output has one additional
public envelope: every runtime-input session produces exactly one object with
only `session_id` (copied verbatim from runtime input) and `payload` (the
contract-v2 semantic-frame object). `BLIND_GENERATOR_JSONL_CONTRACT` and
`build_blind_generated_row()` in `shared/tools/veil_decision_frames.py` are the
single source for that envelope; evaluation code must import its field set
rather than duplicate it.

- `--outcomes --semantic-frames <path>`
  - validates contract v2 evidence and returns the authoritative four-state
    read-only policy result with a zero-or-one question summary
- `--outcomes` without `--semantic-frames`
  - returns contract v1 with `analysis_mode=raw-text-diagnostic`,
    `diagnostic_only=true`, and `write_allowed=false`
- `--preview-only`
  - returns local undefined-wording preview results, including single-occurrence internal labels
- `--investigation-only`
  - returns the broader HTML-style investigation results for difficult sentences
- `--adoptable-only`
  - returns only repeated terms that VEIL would currently consider viable registration candidates

`tests/fixtures/veil_capture_attachment_long_tail.txt` is the compact regression corpus for attachment-derived long-tail wording that previously fell into `unknown`.
`tests/fixtures/veil_capture_attachment_candidates.txt` is the compact candidate-gate corpus for attachment-derived wording that should keep only the current high-signal adoptable set while excluding repeated noise such as proper nouns, file identifiers, and generic phrases.
`tests/fixtures/veil_capture_chat_transcript.json` is the chat-shaped regression corpus for transcript ingestion. It should keep the expected coined / industry / file-config boundaries without leaking any adoptable candidates.

## Classification and outcome release gates

The 100-case stratified fixture and frozen v1-v3 sets are development corpora.
Each v1-v3 first eligible run failed, so none is release evidence. The capture
boundary is release-ready only while all of the following stay true:

- attachment long-tail regression produces no accidental unknown leakage;
- Python label classification and HTML/JS label classification remain in lockstep;
- Python and HTML/JS raw-text diagnostics match on their bounded regression contract;
- semantic schema, exact evidence, rename, conflict, critic disagreement, and
  no-write behavior pass invariant-focused tests;
- a new unseen, independently authored and reviewed end-to-end synthetic
  holdout requires the host AI to produce frames and records provenance, impact,
  reason, source class, reviewer, and required second-review metadata;
- high-impact false exclusions are zero in that independent holdout;
- exception precision and existing-match precision are at least 99%;
- normal sessions require zero questions and exception sessions at most one combined question;
- Skill and HTML normal output contain no candidate table or numbered-candidate instruction;
- accepted multi-result registration uses one validated all-or-nothing JSON batch; and
- the formal browser runner proves recovery wording, diagnostic labeling,
  complete-text AI prompt copy, locale behavior, fine-tuning, clipboard
  fallback, and zero direct writes; and
- a separately approved, anonymized, two-reviewer real-conversation evaluation
  passes before claiming VEIL's overall UX is usable.

Legacy candidate tests remain regression evidence for the old helper APIs. Passing them is not evidence that arbitrary conversations are handled correctly.

## Seed examples

- `migration` -> `industry_term`
- `tracked file` -> `industry_term`
- `API` -> `industry_term`
- `JSON` -> `industry_term`
- `base url` -> `industry_term`
- `branch` -> `industry_term`
- `branch protection` -> `industry_term`
- `read only` -> `industry_term`
- `append only` -> `industry_term`
- `fail close` -> `industry_term`
- `machine readable` -> `industry_term`
- `mainline` -> `industry_term`
- `use case` -> `industry_term`
- `checkpoint` -> `industry_term`
- `workflow` -> `industry_term`
- `console` -> `industry_term`
- `scope` -> `industry_term`
- `dataset` -> `industry_term`
- `endpoint` -> `industry_term`
- `readback` -> `industry_term`
- `ruleset` -> `industry_term`
- `OAuth` -> `industry_term`
- `secret` -> `industry_term`
- `token` -> `industry_term`
- `DB` -> `industry_term`
- `UI` -> `industry_term`
- `UX` -> `industry_term`
- `HTML` -> `industry_term`
- `normalize` -> `industry_term`
- `prompt` -> `industry_term`
- `package` -> `industry_term`
- `packaging` -> `industry_term`
- `release` -> `industry_term`
- `security` -> `industry_term`
- `sync` -> `industry_term`
- `checkout` -> `industry_term`
- `reset` -> `industry_term`
- `guardrail` -> `industry_term`
- `worktree` -> `industry_term`
- `adapter` -> `industry_term`
- `artifact` -> `industry_term`
- `audit` -> `industry_term`
- `backlog` -> `industry_term`
- `bytecode` -> `industry_term`
- `commit` -> `industry_term`
- `contract` -> `industry_term`
- `control plane` -> `industry_term`
- `coordinator` -> `industry_term`
- `coupling` -> `industry_term`
- `database` -> `industry_term`
- `drift` -> `industry_term`
- `execution` -> `industry_term`
- `filesystem` -> `industry_term`
- `grep` -> `industry_term`
- `generator` -> `industry_term`
- `healthcheck` -> `industry_term`
- `hook` -> `industry_term`
- `instrumentation` -> `industry_term`
- `kernel` -> `industry_term`
- `linter` -> `industry_term`
- `mtime` -> `industry_term`
- `namespace` -> `industry_term`
- `protocol` -> `industry_term`
- `push` -> `industry_term`
- `scan` -> `industry_term`
- `seed` -> `industry_term`
- `self-describing` -> `industry_term`
- `schema` -> `industry_term`
- `step` -> `industry_term`
- `subagent` -> `industry_term`
- `test` -> `industry_term`
- `trigger` -> `industry_term`
- `untracked` -> `industry_term`
- `validator` -> `industry_term`
- `writeback` -> `industry_term`
- `writer` -> `industry_term`
- `accepted-route` -> `coined_or_shortened`
- `bounded naturalness` -> `coined_or_shortened`
- `carry-forward` -> `coined_or_shortened`
- `current state` -> `coined_or_shortened`
- `dev-only` -> `coined_or_shortened`
- `maintainer-only` -> `coined_or_shortened`
- `manager-copy` -> `coined_or_shortened`
- `non-current` -> `coined_or_shortened`
- `punctuation-triple` -> `coined_or_shortened`
- `proof-blocker` -> `coined_or_shortened`
- `root clutter` -> `coined_or_shortened`
- `maintainer-only files` -> `coined_or_shortened`
- `owner-only` -> `coined_or_shortened`
- `repo` -> `coined_or_shortened`
- `repos` -> `coined_or_shortened`
- `repo truth` -> `coined_or_shortened`
- `veil-capture` -> `coined_or_shortened`
- `writable-shelf` -> `coined_or_shortened`
- `index` -> `file_config_identifier`
- `docs` -> `file_config_identifier`
- `governance` -> `file_config_identifier`
- `generated` -> `file_config_identifier`
- `template` -> `file_config_identifier`
- `packet` -> `file_config_identifier`
- `pycache` -> `file_config_identifier`
- `spec` -> `file_config_identifier`
- `folder` -> `file_config_identifier`
- `manifest` -> `file_config_identifier`
- `yaml` -> `file_config_identifier`
- `/veil-capture` -> `file_config_identifier`
- `AIM_STATUS.md` -> `file_config_identifier`
- `README` -> `file_config_identifier`
- `CI` -> `file_config_identifier`
- `SE` -> `file_config_identifier`
- `adop-pytest` -> `file_config_identifier`
- `adop-pytest-base2` -> `file_config_identifier`
- `adop-pytest-cache` -> `file_config_identifier`
- `artifact shelf` -> `file_config_identifier`
- `candidate intake note` -> `file_config_identifier`
- `compatibility diagnosis` -> `file_config_identifier`
- `dashboard common scope summary` -> `file_config_identifier`
- `data dashboard endpoint mode` -> `file_config_identifier`
- `data dashboard selected environment` -> `file_config_identifier`
- `data dashboard selected environment scope` -> `file_config_identifier`
- `data dashboard selected project scope` -> `file_config_identifier`
- `data dashboard selected tenant scope` -> `file_config_identifier`
- `data environment mode` -> `file_config_identifier`
- `data runtime surface id` -> `file_config_identifier`
- `data selected environment` -> `file_config_identifier`
- `data selected environment scope` -> `file_config_identifier`
- `data selected project scope` -> `file_config_identifier`
- `data selected tenant scope` -> `file_config_identifier`
- `decision owner` -> `file_config_identifier`
- `export html` -> `file_config_identifier`
- `filter reason` -> `file_config_identifier`
- `filter status` -> `file_config_identifier`
- `guided path` -> `file_config_identifier`
- `html path` -> `file_config_identifier`
- `index-local-composed-sample` -> `file_config_identifier`
- `judgment reason` -> `file_config_identifier`
- `judgment-report` -> `file_config_identifier`
- `landing target` -> `file_config_identifier`
- `next action` -> `file_config_identifier`
- `preventive action` -> `file_config_identifier`
- `project local` -> `file_config_identifier`
- `project oriented` -> `file_config_identifier`
- `project profile` -> `file_config_identifier`
- `quick close trial` -> `file_config_identifier`
- `quick-compare` -> `file_config_identifier`
- `quick-trial` -> `file_config_identifier`
- `declared-vs-observed` -> `file_config_identifier`
- `runtime artifact shelf` -> `file_config_identifier`
- `runtime scope readback updated` -> `file_config_identifier`
- `support docs` -> `file_config_identifier`
- `start-trial` -> `file_config_identifier`
- `URL` -> `file_config_identifier`
- `MD` -> `file_config_identifier`
- `system dev` -> `file_config_identifier`
- `trial-result` -> `file_config_identifier`
- `trial packet` -> `file_config_identifier`
- `writeback target` -> `file_config_identifier`
- `config` -> `file_config_identifier`
- `common` -> `file_config_identifier`
- `archive` -> `file_config_identifier`
- `workspace` -> `file_config_identifier`
- `mirror` -> `other`
- `skill` -> `other`
- `setup` -> `other`
- `selected` -> `other`
- `validation` -> `other`
- `sandbox` -> `other`
- `connector` -> `other`
- `markdown` -> `other`
- `dogfooding` -> `other`
- `export` -> `other`
- `import` -> `other`
- `mode` -> `other`
- `flow` -> `other`
- `naming` -> `other`
- `registration` -> `other`
- `deletion` -> `other`
- `version` -> `other`
- `targeted` -> `other`
- `warning` -> `other`
- `AI` -> `other`
- `PROJECT` -> `other`
- `FAIL` -> `other`
- `BLOCKING` -> `other`
- `current` -> `other`
- `latest` -> `other`
- `disabled` -> `other`
- `success` -> `other`
- `passed` -> `other`
- `status` -> `other`
- `pending` -> `other`
- `pattern` -> `other`
- `managed` -> `other`
- `closing` -> `other`
- `open` -> `other`
- `path` -> `other`
- `narrow` -> `other`
- `helper` -> `other`
- `ownership` -> `other`
- `transfer` -> `other`
- `local` -> `other`
- `PowerShell` -> `other`
- `Anthropic` -> `other`
- `Copilot` -> `other`
- `Pier` -> `other`
- `AIM` -> `other`
- `ADOP` -> `other`
- `Playwright` -> `other`
- `JavaScript` -> `other`
- `Vault` -> `other`
- `mypy` -> `other`
- `parse` -> `other`
- `failure` -> `other`
- `hosted` -> `other`
- `hygiene` -> `other`
- `green` -> `other`
- `dirty` -> `other`
- `clean` -> `other`
- `live state` -> `other`
- `branch question` -> `other`
- `current checkpoint` -> `other`
- `current surface` -> `other`
- `launch evidence` -> `other`
- `parse failure` -> `other`
- `repo hygiene` -> `other`
- `canonical body` -> `file_config_identifier`
- `current route` -> `other`
- `execution lane` -> `other`
- `generated sink` -> `file_config_identifier`
- `GitHub standard` -> `coined_or_shortened`
- `operator view` -> `other`
- `read surface` -> `other`
- `shelf class` -> `other`
- `current task register` -> `file_config_identifier`
- `task register` -> `other`
- `hosted gate` -> `industry_term`
- `punctuation triple` -> `other`
- `current issue` -> `other`
- `failing test` -> `other`
- `current issue` remains classifiable as `other`, but repetition alone does not make it a registration candidate.
- `gitleaks` -> proper-noun exclusion (`proper_noun_non_target`)
- `dependabot` -> proper-noun exclusion (`proper_noun_non_target`)
- `unstable wording` -> `coined_or_shortened`
- `review` -> `other`
- `keep` -> `other`
- `baseline` -> `other`
- `readiness` -> `other`
- `matrix` -> `other`
- `framework` -> `other`
- `capture` -> `other`
- `tree` -> `other`
- `disposition` -> `other`
- `inventory` -> `other`
- `principle` -> `other`
- `proposed` -> `other`
- `role` -> `other`
- `scene` -> `other`
- `stage` -> `other`
- `text` -> `other`
- `trial` -> `other`
- `verification` -> `other`
- `overview` -> `other`
- `whitelist` -> `other`
- `reviewer` -> `other`
- `auditor` -> `other`
- `engineer` -> `other`
- `Bash` -> `other`
- `Cursor` -> `other`
- `SQLite` -> `other`
- `Saiga` -> `other`
- `Symphony` -> `other`
- `server` -> `other`
- `payload` -> `other`
- `platform` -> `other`
- `license` -> `other`
- `reason` -> `other`
- `GitHub` -> `other`
- `Python` -> `other`
- `pytest` -> `other`
- `root` -> `other`
- `ordinary` -> `other`
- `noun` -> `other`
- `multiword` -> `other`
- `first-pass` -> `other`
