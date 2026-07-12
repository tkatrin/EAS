"""Generate and enforce the EAS requirement-coverage report."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Sequence

from .registry import build_coverage, validate_registries


MINIMUM_METRICS = {
    "with_validator_rules",
    "structurally_machine_checkable",
    "behaviorally_assessable",
    "covered_by_scenarios",
}
MAXIMUM_METRICS = {"currently_unobservable"}


def render_coverage_markdown(coverage: dict[str, Any]) -> str:
    """Render a deterministic human-readable coverage snapshot."""

    summary = coverage["summary"]
    levels = summary["by_level"]
    checkability = summary["machine_checkable"]
    lines = [
        "# EAS 0.1 requirement coverage",
        "",
        "Generated from `registry/requirements.json` and "
        "`registry/validator-rules.json`. Counts describe declared, tested "
        "reference-tool coverage; they do not establish empirical validity.",
        "",
        f"- Registry version: `{coverage['registry_version']}`",
        f"- Total requirements: **{summary['total_requirements']}**",
        f"- Mandatory (`MUST`): **{levels['MUST']}**",
        f"- Advisory (`SHOULD`): **{levels['SHOULD']}**",
        f"- Permissions (`MAY`): **{levels['MAY']}**",
        f"- Fully machine-checkable: **{checkability['full']}**",
        f"- Partially machine-checkable: **{checkability['partial']}**",
        f"- Currently unobservable: **{summary['currently_unobservable']}**",
        f"- With validator rules: **{summary['with_validator_rules']}**",
        f"- Structurally machine-checkable: **{summary['structurally_machine_checkable']}**",
        f"- Behaviorally assessable: **{summary['behaviorally_assessable']}**",
        f"- Covered by scenarios: **{summary['covered_by_scenarios']}**",
        "",
        "## Requirements without validator rules",
        "",
    ]
    uncovered_rules = coverage["uncovered"]["validator_rules"]
    lines.extend(f"- `{item}`" for item in uncovered_rules)
    lines.extend(("", "## Requirements without scenarios", ""))
    uncovered_scenarios = coverage["uncovered"]["scenarios"]
    lines.extend(f"- `{item}`" for item in uncovered_scenarios)
    return "\n".join(lines) + "\n"


def check_coverage_baseline(
    coverage: dict[str, Any], baseline: dict[str, Any]
) -> list[str]:
    """Return regressions against explicit minimum and maximum metrics."""

    issues: list[str] = []
    summary = coverage["summary"]
    minimum = baseline.get("minimum", {})
    maximum = baseline.get("maximum", {})
    for metric in sorted(MINIMUM_METRICS):
        expected = minimum.get(metric)
        if not isinstance(expected, int):
            issues.append(f"baseline minimum.{metric} must be an integer")
        elif summary[metric] < expected:
            issues.append(
                f"{metric} regressed: observed {summary[metric]}, minimum {expected}"
            )
    for metric in sorted(MAXIMUM_METRICS):
        expected = maximum.get(metric)
        if not isinstance(expected, int):
            issues.append(f"baseline maximum.{metric} must be an integer")
        elif summary[metric] > expected:
            issues.append(
                f"{metric} regressed: observed {summary[metric]}, maximum {expected}"
            )
    return issues


def _load(path: Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate EAS requirement coverage.")
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--check", type=Path, help="require this report to be current")
    parser.add_argument("--baseline", type=Path, help="enforce coverage thresholds")
    args = parser.parse_args(argv)

    requirements = _load(args.root / "registry" / "requirements.json")
    rules = _load(args.root / "registry" / "validator-rules.json")
    registry_issues = validate_registries(requirements, rules, args.root)
    if registry_issues:
        for issue in registry_issues:
            print(issue)
        return 1

    coverage = build_coverage(requirements, rules)
    rendered = render_coverage_markdown(coverage)
    failed = False
    if args.check is not None:
        try:
            committed = args.check.read_text(encoding="utf-8")
        except OSError as error:
            print(f"coverage report cannot be read: {error}")
            failed = True
        else:
            if committed != rendered:
                print(f"coverage report is stale: {args.check}")
                failed = True
    if args.baseline is not None:
        regressions = check_coverage_baseline(coverage, _load(args.baseline))
        for regression in regressions:
            print(f"coverage regression: {regression}")
        failed = failed or bool(regressions)
    if args.check is None:
        print(rendered, end="")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
