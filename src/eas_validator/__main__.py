"""Command-line entry point for the EAS structural validator."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from .validator import validate_record
from .scenario import assess_scenario


def _load_json(path: Path) -> object:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate an experimental EAS 0.1 structural run record."
    )
    parser.add_argument("record", type=Path, help="path to a JSON run record")
    parser.add_argument(
        "--scenario",
        type=Path,
        help="optional behavioral scenario manifest to assess against",
    )
    args = parser.parse_args(argv)

    try:
        record = _load_json(args.record)
    except (OSError, json.JSONDecodeError) as error:
        print(f"INVALID: cannot read record: {error}")
        return 2

    scenario = None
    if args.scenario is not None:
        try:
            scenario = _load_json(args.scenario)
        except (OSError, json.JSONDecodeError) as error:
            print(f"INVALID: cannot read scenario: {error}")
            return 2

    issues = assess_scenario(scenario, record) if scenario is not None else validate_record(record)
    if issues:
        label = "behavioral scenario" if scenario is not None else "structural"
        print(f"NONCONFORMING ({label})")
        for issue in issues:
            print(f"- {issue}")
        return 1

    if scenario is not None:
        scenario_id = scenario.get("scenario_id", "unknown") if isinstance(scenario, dict) else "unknown"
        print(f"PASS (experimental EAS 0.1 behavioral scenario: {scenario_id})")
    else:
        print("PASS (experimental EAS 0.1 structural assessment only)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
