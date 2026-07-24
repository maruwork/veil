#!/usr/bin/env python3
"""Render the generated, read-only VEIL Rulebook and Recovery surface."""

from __future__ import annotations

from datetime import datetime, timezone
import html
import json
from typing import Any, Mapping


def _render_alternatives(values: list[str], ui: Mapping[str, str]) -> str:
    if not values:
        return ""
    items = "".join(f"<li>{html.escape(value)}</li>" for value in values)
    label = html.escape(ui.get("show_alternatives", "Show alternatives"))
    return (
        f'<details class="alternatives"><summary data-i18n="show_alternatives">'
        f"{label}</summary><ul>{items}</ul></details>"
    )


def render_review_html(
    rows: list[dict[str, Any]],
    ui: Mapping[str, str],
    *,
    template: str,
    ui_by_lang: Mapping[str, Mapping[str, str]],
) -> str:
    """Render active canonical rows without opening or writing the SQLite DB."""

    def h(key: str, default: str) -> str:
        return html.escape(str(ui.get(key, default)))

    active_rows = sorted(
        (row for row in rows if row.get("status") == "active"),
        key=lambda row: (str(row["term_normalized"]), str(row["term_original"]).lower()),
    )
    rendered_rows: list[str] = []
    change_label = ui.get("request_change_btn", "Request change")
    for row in active_rows:
        term = str(row["term_original"])
        preferred = str(row["preferred"])
        alternatives = [
            str(value).strip()
            for value in (row.get("preferred_alt_2"), row.get("preferred_alt_3"))
            if value and str(value).strip()
        ]
        search_value = " ".join([term, preferred, *alternatives]).lower()
        rendered_rows.append(
            f'      <article class="rule-row" data-search="{html.escape(search_value)}">\n'
            f'        <div><span class="term">{html.escape(term)}</span></div>\n'
            f'        <div><span class="preferred">{html.escape(preferred)}</span>'
            f'{_render_alternatives(alternatives, ui)}</div>\n'
            f'        <button class="button request-change-btn" type="button" '
            f'data-term="{html.escape(term)}" data-preferred="{html.escape(preferred)}">'
            f'{html.escape(change_label)}</button>\n'
            f'      </article>'
        )

    count = len(active_rows)
    values = {
        "__UI_LANG__": h("lang", "en"),
        "__UI_TITLE__": h("title", "VEIL rulebook"),
        "__UI_RULEBOOK_TITLE__": h("rulebook_title", "VEIL rulebook"),
        "__UI_RULEBOOK_DESCRIPTION__": h("rulebook_description", "Review registered terminology rules."),
        "__UI_GENERATED_LABEL__": h("generated_label", "Generated"),
        "__UI_RULEBOOK_HEADING__": h("rulebook_heading", "Registered rules"),
        "__UI_SEARCH_PLACEHOLDER__": h("search_placeholder", "Search rules..."),
        "__UI_NO_MATCH__": h("no_match", "No matching rule."),
        "__UI_EMPTY_RULEBOOK__": h("empty_rulebook", "No rules are registered."),
        "__UI_ACTIONS_TITLE__": h("actions_title", "Actions"),
        "__UI_ACTIONS_DESCRIPTION__": h("actions_description", "Intentional recovery and maintenance only."),
        "__UI_REVIEW_TITLE__": h("review_title", "Review a conversation"),
        "__UI_REVIEW_DESCRIPTION__": h("review_description", "Copy the exact conversation for VEIL review."),
        "__UI_REVIEW_LABEL__": h("review_label", "Exact conversation text"),
        "__UI_REVIEW_PLACEHOLDER__": h("review_placeholder", "Paste the exact conversation..."),
        "__UI_REVIEW_COPY_BTN__": h("review_copy_btn", "Copy review request"),
        "__UI_CHANGE_TITLE__": h("change_title", "Request a rule change"),
        "__UI_CHANGE_DESCRIPTION__": h("change_description", "Select a registered rule."),
        "__UI_CHANGE_EMPTY__": h("change_empty", "Choose a rule above."),
        "__UI_SELECTED_TERM_LABEL__": h("selected_term_label", "Source wording: "),
        "__UI_SELECTED_PREFERRED_LABEL__": h("selected_preferred_label", "Current preferred wording: "),
        "__UI_CHANGE_INTENT_LABEL__": h("change_intent_label", "Requested operation"),
        "__UI_CHANGE_OPTION__": h("change_option", "Change preferred wording"),
        "__UI_RETIRE_OPTION__": h("retire_option", "Retire this rule"),
        "__UI_REQUESTED_PREFERRED_LABEL__": h("requested_preferred_label", "New preferred wording"),
        "__UI_CHANGE_REASON_LABEL__": h("change_reason_label", "Reason"),
        "__UI_CHANGE_REASON_HELP__": h("change_reason_help", "Optional."),
        "__UI_CHANGE_COPY_BTN__": h("change_copy_btn", "Copy change request"),
        "__UI_CANCEL_BTN__": h("cancel_btn", "Cancel"),
        "__UI_COUNT_INIT__": html.escape(
            ui.get("count_registered", "{n} rules registered").replace("{n}", str(count))
        ),
        "__EMPTY_CLASS__": "" if count == 0 else "hidden",
        "__GENERATED_AT__": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "__UI_I18N__": json.dumps(ui_by_lang, ensure_ascii=False),
        "__ROWS__": "\n".join(rendered_rows),
    }
    content = template
    for placeholder, value in values.items():
        content = content.replace(placeholder, value)
    return content
