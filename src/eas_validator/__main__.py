"""Command-line entry point for the EAS structural validator."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from .validator import validate_record


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate an experimental EAS 0.1 structural run record."
    )
    parser.add_argument("record", type=Path, help="path to a JSON run record")
    args = parser.parse_args(argv)

    try:
        with args.record.open(encoding="utf-8") as handle:
            record = json.load(handle)
    except (OSError, json.JSONDecodeError) as error:
        print(f"INVALID: cannot read record: {error}")
        return 2

    issues = validate_record(record)
    if issues:
        print("NONCONFORMING (structural)")
        for issue in issues:
            print(f"- {issue}")
        return 1

    print("PASS (experimental EAS 0.1 structural assessment only)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
