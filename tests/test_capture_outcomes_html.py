from __future__ import annotations

from pathlib import Path

from shared.tools.veil_html_assets import _HTML_TEMPLATE, _HTML_UI_BY_LANG, _HTML_UI_EN
from shared.tools.veil_html_review import render_review_html


def _render() -> str:
    return render_review_html(
        [
            {
                "term_original": "current state",
                "term_normalized": "current state",
                "preferred": "present state",
                "preferred_alt_2": "current status",
                "preferred_alt_3": None,
                "status": "active",
            },
            {
                "term_original": "retired term",
                "term_normalized": "retired term",
                "preferred": "retired wording",
                "preferred_alt_2": None,
                "preferred_alt_3": None,
                "status": "retired",
            },
        ],
        _HTML_UI_EN,
        template=_HTML_TEMPLATE,
        ui_by_lang=_HTML_UI_BY_LANG,
    )


def test_html_is_rulebook_and_recovery_surface() -> None:
    content = _render()

    assert content.index("Registered rules") < content.index("Actions")
    assert "current state" in content
    assert "present state" in content
    assert "current status" in content
    assert "retired term" not in content
    assert 'id="review-input"' in content
    assert 'id="review-copy-btn"' in content
    assert 'id="change-form"' in content
    assert 'class="button request-change-btn"' in content


def test_html_has_one_semantic_review_route_and_no_local_classifier() -> None:
    content = _render()

    assert content.count('id="review-copy-btn"') == 1
    assert "Run the installed VEIL capture workflow" in content
    for forbidden in (
        "_captureConfig",
        "analyzeCaptureOutcomes",
        "classifyCaptureTerm",
        "capture-analyze-btn",
        "capture-output",
        "buildDbCliCommand",
        "upsert-rule",
        "delete-rule",
        "export-html",
    ):
        assert forbidden not in content


def test_html_never_attempts_browser_storage_or_network_writes() -> None:
    content = _render()

    for forbidden in (
        "fetch(",
        "XMLHttpRequest",
        "indexedDB",
        "localStorage",
        "sessionStorage",
        "WebSocket",
    ):
        assert forbidden not in content
    assert "navigator.clipboard.writeText" in content


def test_template_is_utf8_and_contains_no_unresolved_runtime_placeholders() -> None:
    content = _render()

    assert Path("shared/tools/veil_review_template.html").read_text(encoding="utf-8")
    assert "__UI_" not in content
    assert "__ROWS__" not in content
