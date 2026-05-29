from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from real_estate_investor.orchestrator import RealEstateOrchestrator


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Real Estate Investment Analyst")
    sub = parser.add_subparsers(dest="command", required=True)

    analyze = sub.add_parser("analyze", help="Analyze a property and produce recommendation output")
    analyze.add_argument("--address", required=True, help="Property address")
    analyze.add_argument("--assumptions-json", help="JSON string or path for financial assumptions")
    analyze.add_argument("--weights-json", help="JSON string or path for scoring weights")
    analyze.add_argument("--user-overrides-json", help="JSON string or path for missing data overrides")
    analyze.add_argument("--output-json", help="Path to write result JSON")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    orchestrator = RealEstateOrchestrator()

    if args.command == "analyze":
        assumptions = _parse_json_input(args.assumptions_json)
        weights = _parse_json_input(args.weights_json)
        overrides = _parse_json_input(args.user_overrides_json)
        result = orchestrator.analyze(
            property_address=args.address,
            financial_assumptions=assumptions or None,
            user_weights=weights or None,
            user_overrides=overrides or None,
        )
        rendered = json.dumps(result, indent=2)
        if args.output_json:
            output_path = Path(args.output_json)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(rendered, encoding="utf-8")
        print(rendered)
        return 0

    raise SystemExit(f"Unknown command: {args.command}")


def _parse_json_input(raw: str | None) -> dict[str, Any]:
    if not raw:
        return {}
    maybe_file = Path(raw)
    if maybe_file.exists():
        return json.loads(maybe_file.read_text(encoding="utf-8"))
    return json.loads(raw)


if __name__ == "__main__":
    raise SystemExit(main())
