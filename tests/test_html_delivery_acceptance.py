from __future__ import annotations

from tests.html_delivery_acceptance import run_acceptance


def test_disposable_html_maintenance_delivery_path(tmp_path) -> None:
    result = run_acceptance(tmp_path)

    assert result["ok"] is True
    assert result["temp_only"] is True
    assert result["html_selected_contract"] == {
        "current state": {
            "term": "current state",
            "current_preferred": "present state",
        },
        "old lane": {
            "term": "old lane",
            "current_preferred": "approved lane",
        },
    }
    assert result["before_freshness"] == "OK"
    assert result["stale_before_regeneration"] == "STALE"
    assert result["final_freshness"] == "OK"
    assert result["changed_preferred"] == "current condition"
    assert result["retired_status"] == "retired"
    assert result["changed_visible"] is True
    assert result["retired_hidden"] is True
