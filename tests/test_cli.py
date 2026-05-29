from __future__ import annotations

import json

from real_estate_investor.cli import main


def test_cli_analyze_writes_output(tmp_path):
    output = tmp_path / "result.json"
    rc = main(
        [
            "analyze",
            "--address",
            "123 Main St, Springfield, IL",
            "--output-json",
            str(output),
        ]
    )
    assert rc == 0
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["property_address"] == "123 Main St, Springfield, IL"
