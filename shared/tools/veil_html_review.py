#!/usr/bin/env python3
"""M2 review-HTML renderer.

This module owns browser-review markup and interaction payload construction. It
accepts canonical rows as input and never opens or writes the SQLite store.
"""

from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Any, Mapping


def _render_alt_cell(term: str, alt: str | None, copy_btn: str = "Copy") -> str:
    if not alt or not str(alt).strip():
        return ""
    return (
        f'<div class="cell">'
        f'<span class="alt">{html.escape(str(alt))}</span>'
        f'<button class="copy-btn" data-term="{html.escape(term)}" data-alt="{html.escape(str(alt))}" '
        f'title="{html.escape(copy_btn)}" aria-label="{html.escape(copy_btn)}" onclick="copy(this)">'
        f'{html.escape(copy_btn)}</button>'
        f'</div>'
    )


def _render_delete_cell(term: str, preferred: str, delete_btn: str = "Delete") -> str:
    return (
        f'<button class="copy-btn danger-btn delete-btn" data-term="{html.escape(term)}" '
        f'data-preferred="{html.escape(preferred)}" title="{html.escape(delete_btn)}" '
        f'aria-label="{html.escape(delete_btn)}" onclick="copyDeleteInstruction(this)">'
        f'{html.escape(delete_btn)}</button>'
    )


def render_review_html(
    rows: list[dict[str, Any]],
    ui: Mapping[str, str],
    *,
    template: str,
    ui_by_lang: Mapping[str, Mapping[str, str]],
    capture_config: Mapping[str, Any],
    db_cli_path: str,
    db_path: str,
    html_path: str,
) -> str:
    """Render the M2 review UI from already-read canonical rows."""

    def js(key: str, default: str) -> str:
        return json.dumps(ui.get(key, default), ensure_ascii=False)[1:-1]

    def h(key: str, default: str) -> str:
        return html.escape(ui.get(key, default))

    copy_btn = ui.get("copy_btn", "Copy")
    delete_btn = ui.get("delete_btn", "Delete")
    rows_sorted = sorted(
        (row for row in rows if row.get("status") == "active"),
        key=lambda row: (str(row["term_normalized"]), str(row["term_original"]).lower()),
    )
    row_parts: list[str] = []
    for row in rows_sorted:
        term = str(row["term_original"])
        term_normalized = str(row["term_normalized"])
        preferred = str(row["preferred"])
        alt2 = row.get("preferred_alt_2")
        alt3 = row.get("preferred_alt_3")
        first_char = term[0] if term else "?"
        section = first_char.upper() if first_char.isalpha() else "?"
        row_parts.append(
            f"    <tr data-term=\"{html.escape(term)}\" data-term-normalized=\"{html.escape(term_normalized)}\">\n"
            f"      <td><span class=\"section-label\">{html.escape(section)}</span>"
            f"<span class=\"term\">{html.escape(term)}</span></td>\n"
            f"      <td><span class=\"preferred\">{html.escape(preferred)}</span></td>\n"
            f"      <td>{_render_alt_cell(term, str(alt2) if alt2 else None, copy_btn)}</td>\n"
            f"      <td>{_render_alt_cell(term, str(alt3) if alt3 else None, copy_btn)}</td>\n"
            f"      <td>{_render_delete_cell(term, preferred, delete_btn)}</td>\n"
            f"    </tr>"
        )

    count = len(rows_sorted)
    count_init = ui.get("count_registered", "{n} terms registered").replace("{n}", str(count))
    content = template
    content = content.replace("__UI_LANG__", h("lang", "en"))
    content = content.replace("__DB_CLI_PATH__", json.dumps(db_cli_path, ensure_ascii=False))
    content = content.replace("__DB_PATH__", json.dumps(Path(db_path).as_posix(), ensure_ascii=False))
    content = content.replace("__HTML_PATH__", json.dumps(Path(html_path).as_posix(), ensure_ascii=False))
    content = content.replace("__UI_TITLE__", h("title", "VEIL - Vocabulary Rules"))
    content = content.replace("__UI_I18N__", json.dumps(ui_by_lang, ensure_ascii=False))
    content = content.replace("__CAPTURE_CONFIG__", json.dumps(capture_config, ensure_ascii=False))
    content = content.replace("__UI_COUNT_INIT__", html.escape(count_init))
    labels = {
        "__UI_SEARCH_PLACEHOLDER__": ("search_placeholder", "Search terms..."),
        "__UI_CAPTURE_TITLE__": ("capture_title", "Draft Capture"),
        "__UI_CAPTURE_DESCRIPTION__": ("capture_description", "Paste source text here to get a local undefined-wording preview. This favors conversation-local labels over specialist terminology."),
        "__UI_CAPTURE_PLACEHOLDER__": ("capture_placeholder", "Paste text to analyze..."),
        "__UI_CAPTURE_BTN__": ("capture_btn", "Analyze Draft"),
        "__UI_CAPTURE_COPY_OUTPUT_BTN__": ("capture_copy_output_btn", "Copy Draft Output"),
        "__UI_CAPTURE_COPY_PROMPT_BTN__": ("capture_copy_prompt_btn", "Copy AI Prompt"),
        "__UI_CAPTURE_RESULT_TITLE__": ("capture_result_title", "Draft Output"),
        "__UI_CAPTURE_EMPTY__": ("capture_empty", "Paste text and run analysis."),
        "__UI_CAPTURE_NOTE__": ("capture_note", "This is a local preview for undefined wording. Use Copy AI Prompt when you want a better judgment from the chat model."),
        "__UI_INSTRUCTION__": ("instruction", "Use Draft Capture to investigate undefined wording. Click a preview line to load the registration form, then copy a registration request for chat-side registration."),
        "__UI_REGISTER_TITLE__": ("register_title", "Register a new rule"),
        "__UI_FIELD_TERM__": ("field_term", "Term"),
        "__UI_FIELD_PREFERRED__": ("field_preferred", "Preferred"),
        "__UI_FIELD_ALT2__": ("field_alt2", "Candidate 2"),
        "__UI_FIELD_ALT3__": ("field_alt3", "Candidate 3"),
        "__UI_REGISTER_TERM_PLACEHOLDER__": ("register_term_placeholder", "e.g. current state"),
        "__UI_REGISTER_PREFERRED_PLACEHOLDER__": ("register_preferred_placeholder", "e.g. present state"),
        "__UI_REGISTER_ALT2_PLACEHOLDER__": ("register_alt2_placeholder", "Optional alternative"),
        "__UI_REGISTER_ALT3_PLACEHOLDER__": ("register_alt3_placeholder", "Optional alternative"),
        "__UI_REGISTER_BTN__": ("register_btn", "Copy Registration Request"),
        "__UI_REGISTER_COMMANDS_BTN__": ("register_commands_btn", "Copy Commands"),
        "__UI_COL_TERM__": ("col_term", "Term"),
        "__UI_COL_PREFERRED__": ("col_preferred", "Preferred (candidate 1)"),
        "__UI_COL_ALT2__": ("col_alt2", "Candidate 2"),
        "__UI_COL_ALT3__": ("col_alt3", "Candidate 3"),
        "__UI_COL_ACTIONS__": ("col_actions", "Actions"),
    }
    for placeholder, (key, default) in labels.items():
        content = content.replace(placeholder, h(key, default))
    messages = {
        "__UI_COPY_INSTRUCTION__": ("copy_instruction", "Change '{term}' to '{candidate}'"),
        "__UI_COPY_BTN__": ("copy_btn", "Copy"),
        "__UI_DELETE_BTN__": ("delete_btn", "Delete"),
        "__UI_COPY_DONE__": ("copy_done", "Copied"),
        "__UI_COPY_MANUAL__": ("copy_manual", "Clipboard access is unavailable. Copy this text manually:"),
        "__UI_COPY_MANUAL_DONE__": ("copy_manual_done", "Manual copy prompt opened."),
        "__UI_COPY_FAILED__": ("copy_failed", "Copy failed. Copy the text manually from the prompt."),
        "__UI_CAPTURE_COPY_OUTPUT_COPIED__": ("capture_copy_output_copied", "Draft output copied."),
        "__UI_CAPTURE_COPY_PROMPT_COPIED__": ("capture_copy_prompt_copied", "AI prompt copied."),
        "__UI_CAPTURE_NONE__": ("capture_none", "No preview candidates."),
        "__UI_CAPTURE_READY__": ("capture_ready", "Draft preview generated."),
        "__UI_CAPTURE_CURRENT_LABEL__": ("capture_current_label", " (current)"),
        "__UI_CAPTURE_CANDIDATE1_LABEL__": ("capture_candidate1_label", " (candidate 1)"),
        "__UI_CAPTURE_CANDIDATE2_LABEL__": ("capture_candidate2_label", " (candidate 2)"),
        "__UI_CAPTURE_FOOTER__": ("capture_footer", "Candidate 1 is the current local draft."),
        "__UI_CAPTURE_KEEP_CURRENT__": ("capture_keep_current", "keep current"),
        "__UI_CAPTURE_PROMPT_HEADER__": ("capture_prompt_header", "Use veil-capture semantics on the following text only."),
        "__UI_REGISTER_MISSING__": ("register_missing", "Term and preferred form are required."),
        "__UI_REGISTER_COPIED__": ("register_copied", "Registration request copied."),
        "__UI_REGISTER_COMMANDS_COPIED__": ("register_commands_copied", "Registration commands copied."),
        "__UI_DELETE_COPIED__": ("delete_copied", "Deletion commands copied."),
        "__UI_DELETE_INSTRUCTION_HEADER__": ("delete_instruction_header", "Run these commands to delete this rule:"),
        "__UI_REGISTER_INSTRUCTION_HEADER__": ("register_instruction_header", "Run these commands to register this rule:"),
        "__UI_REGISTER_PROMPT_HEADER__": ("register_prompt_header", "Register this VEIL rule in the current repository:"),
        "__UI_REGISTER_PROMPT_FOOTER__": ("register_prompt_footer", "Update the SQLite canonical, then regenerate the mirror and veil.html."),
        "__UI_COUNT_REGISTERED__": ("count_registered", "{n} terms registered"),
        "__UI_COUNT_MATCHING__": ("count_matching", "{n} terms matching"),
    }
    for placeholder, (key, default) in messages.items():
        content = content.replace(placeholder, js(key, default))
    return content.replace("__ROWS__", "\n".join(row_parts))
