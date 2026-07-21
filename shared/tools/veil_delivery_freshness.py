"""M1 delivery fingerprints for generated VEIL review HTML."""
from __future__ import annotations

import hashlib
import json
import re
from typing import Any, Mapping, Sequence

MANIFEST_FORMAT = 1
MANIFEST_ID = "veil-freshness-manifest"
_MANIFEST_RE = re.compile(
    rf'<script id="{MANIFEST_ID}" type="application/json">(.*?)</script>', re.DOTALL
)


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def active_rule_rows(rows: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    fields = ("term_original", "term_normalized", "preferred", "preferred_alt_2", "preferred_alt_3")
    return sorted(
        [{field: row.get(field) for field in fields} for row in rows if row.get("status") == "active"],
        key=lambda row: (str(row["term_normalized"]), str(row["term_original"]).lower()),
    )


def build_manifest(
    *, template: str, ui_by_lang: Mapping[str, Any], capture_taxonomy: Mapping[str, Any],
    rows: Sequence[Mapping[str, Any]], settings: Mapping[str, str], content_sha256: str = "",
) -> dict[str, Any]:
    return {
        "format": MANIFEST_FORMAT,
        "template_sha256": sha256_text(template),
        "i18n_sha256": sha256_text(canonical_json(ui_by_lang)),
        "capture_taxonomy_sha256": sha256_text(canonical_json(capture_taxonomy)),
        "active_rules_sha256": sha256_text(canonical_json(active_rule_rows(rows))),
        "settings_sha256": sha256_text(canonical_json(dict(settings))),
        "content_sha256": content_sha256,
    }


def _manifest_tag(manifest: Mapping[str, Any]) -> str:
    return f'<script id="{MANIFEST_ID}" type="application/json">{canonical_json(dict(manifest))}</script>'


def embed_manifest(content: str, manifest: Mapping[str, Any]) -> str:
    if "</body>" not in content:
        raise ValueError("review HTML has no body closing tag")
    return content.replace("</body>", _manifest_tag(manifest) + "\n</body>", 1)


def render_with_manifest(content: str, **manifest_inputs: Any) -> str:
    blank = build_manifest(**manifest_inputs)
    fingerprinted = embed_manifest(content, blank)
    manifest = build_manifest(**manifest_inputs, content_sha256=sha256_text(fingerprinted))
    return embed_manifest(content, manifest)


def read_manifest(content: str) -> tuple[dict[str, Any] | None, str | None]:
    match = _MANIFEST_RE.search(content)
    if not match:
        return None, "missing"
    try:
        manifest = json.loads(match.group(1))
    except json.JSONDecodeError:
        return None, "malformed"
    if not isinstance(manifest, dict):
        return None, "malformed"
    return manifest, None


def verify_manifest(content: str, **manifest_inputs: Any) -> str:
    manifest, error = read_manifest(content)
    if error:
        return "STALE" if error == "missing" else "ERROR"
    expected = build_manifest(**manifest_inputs)
    if any(manifest.get(key) != value for key, value in expected.items() if key != "content_sha256"):
        return "STALE"
    match = _MANIFEST_RE.search(content)
    assert match is not None
    blank = content[:match.start(1)] + canonical_json({**manifest, "content_sha256": ""}) + content[match.end(1):]
    if manifest.get("content_sha256") != sha256_text(blank):
        return "ERROR"
    return "OK"
