"""Human-readable renderers for versioned EAS assessment records."""

from __future__ import annotations

import json
from typing import Any

from .assessment import validate_assessment_record


_RESULT_GROUPS = (
    ("pass", "Passed requirements"),
    ("fail", "Failed requirements"),
    ("indeterminate", "Indeterminate requirements"),
    ("not_applicable", "Not applicable requirements"),
)


def _validated(record: Any) -> dict[str, Any]:
    issues = validate_assessment_record(record)
    if issues:
        rendered = "; ".join(str(issue) for issue in issues)
        raise ValueError(f"cannot render invalid assessment record: {rendered}")
    return record


def _scenario_label(record: dict[str, Any]) -> str:
    scenario_set = record["scenario_set"]
    if scenario_set is None:
        return "not used"
    scenarios = ", ".join(scenario_set["scenario_ids"])
    return f"{scenario_set['id']} {scenario_set['version']} ({scenarios})"


def _result_label(item: dict[str, Any]) -> str:
    label = item["requirement_id"]
    if "title" in item:
        label += f" — {item['title']}"
    return label


def _result_detail(item: dict[str, Any]) -> str:
    detail = _result_label(item)
    reason = item.get("reason")
    if reason:
        detail += f": {reason}"
    elif item["result"] == "fail":
        detail += ": no reason recorded"
    detail += f" [{item['level']}]"
    if item["evidence_refs"]:
        detail += f"; evidence: {', '.join(item['evidence_refs'])}"
    return detail


def _grouped_results(record: dict[str, Any], result: str) -> list[dict[str, Any]]:
    return [
        item for item in record["requirement_results"] if item["result"] == result
    ]


def render_terminal(record: Any) -> str:
    """Render a plain-text report suitable for terminal output."""

    assessment = _validated(record)
    assessor = assessment["assessor"]
    registries = assessment["registries"]
    summary = assessment["summary"]
    counts = summary["counts"]

    lines = [
        f"EAS assessment: {assessment['assessment_level']}",
        f"Version: EAS {assessment['eas_version']} Working Draft",
        f"Assessment ID: {assessment['assessment_id']}",
        f"Assessment subject: {assessment['assessment_subject']['type']} "
        f"{assessment['assessment_subject']['id']}",
        f"Assessor: {assessor['name']} {assessor['version']}",
        f"Source: {assessment['source_record']['type']} "
        f"{assessment['source_record']['id']}",
        f"Scenario set: {_scenario_label(assessment)}",
        f"Requirement registry: {registries['requirements']}",
        f"Validator-rule registry: {registries['validator_rules']}",
        f"Completed: {assessment['completed_at']}",
        f"Result: {summary['result'].upper()}",
        "",
        f"Passed requirements: {counts['pass']}",
        f"Failed requirements: {counts['fail']}",
        f"Indeterminate requirements: {counts['indeterminate']}",
        f"Not applicable: {counts['not_applicable']}",
        f"Total assessed: {counts['total']}",
    ]

    for result, title in _RESULT_GROUPS:
        lines.extend(("", f"{title}:"))
        items = _grouped_results(assessment, result)
        if not items:
            lines.append("- none")
        else:
            lines.extend(f"- {_result_detail(item)}" for item in items)

    lines.extend(("", "Scope and limitations:"))
    lines.extend(f"- {limitation}" for limitation in assessment["limitations"])
    return "\n".join(lines) + "\n"


def _markdown_text(value: Any) -> str:
    return str(value).replace("\\", "\\\\").replace("|", "\\|")


def _markdown_result(item: dict[str, Any]) -> str:
    label = f"**{_markdown_text(item['requirement_id'])}**"
    if "title" in item:
        label += f" — {_markdown_text(item['title'])}"
    reason = item.get("reason")
    if reason:
        label += f": {_markdown_text(reason)}"
    elif item["result"] == "fail":
        label += ": no reason recorded"
    label += f" `[{_markdown_text(item['level'])}]`"
    if item["evidence_refs"]:
        evidence = ", ".join(_markdown_text(ref) for ref in item["evidence_refs"])
        label += f"; evidence: {evidence}"
    return label


def render_markdown(record: Any) -> str:
    """Render an assessment as a standalone Markdown report."""

    assessment = _validated(record)
    assessor = assessment["assessor"]
    registries = assessment["registries"]
    summary = assessment["summary"]
    counts = summary["counts"]

    lines = [
        "# EAS assessment report",
        "",
        "| Field | Value |",
        "| --- | --- |",
        f"| Assessment level | {_markdown_text(assessment['assessment_level'])} |",
        f"| Version | EAS {_markdown_text(assessment['eas_version'])} Working Draft |",
        f"| Assessment ID | {_markdown_text(assessment['assessment_id'])} |",
        f"| Assessment subject | {_markdown_text(assessment['assessment_subject']['type'])} "
        f"{_markdown_text(assessment['assessment_subject']['id'])} |",
        f"| Assessor | {_markdown_text(assessor['name'])} {_markdown_text(assessor['version'])} |",
        f"| Source | {_markdown_text(assessment['source_record']['type'])} "
        f"{_markdown_text(assessment['source_record']['id'])} |",
        f"| Scenario set | {_markdown_text(_scenario_label(assessment))} |",
        f"| Requirement registry | {_markdown_text(registries['requirements'])} |",
        f"| Validator-rule registry | {_markdown_text(registries['validator_rules'])} |",
        f"| Completed | {_markdown_text(assessment['completed_at'])} |",
        f"| Result | **{_markdown_text(summary['result'].upper())}** |",
        "",
        "## Summary",
        "",
        "| Requirement result | Count |",
        "| --- | ---: |",
        f"| Pass | {counts['pass']} |",
        f"| Fail | {counts['fail']} |",
        f"| Indeterminate | {counts['indeterminate']} |",
        f"| Not applicable | {counts['not_applicable']} |",
        f"| **Total** | **{counts['total']}** |",
    ]

    for result, title in _RESULT_GROUPS:
        lines.extend(("", f"## {title}", ""))
        items = _grouped_results(assessment, result)
        if not items:
            lines.append("- None.")
        else:
            lines.extend(f"- {_markdown_result(item)}" for item in items)

    lines.extend(("", "## Scope and limitations", ""))
    lines.extend(
        f"- {_markdown_text(limitation)}" for limitation in assessment["limitations"]
    )
    return "\n".join(lines) + "\n"


def render_json(record: Any, *, indent: int = 2) -> str:
    """Render the complete assessment record as deterministic JSON."""

    assessment = _validated(record)
    return json.dumps(
        assessment,
        ensure_ascii=False,
        indent=indent,
        sort_keys=True,
    ) + "\n"


def render_report(record: Any, output_format: str = "terminal") -> str:
    """Dispatch to the terminal, JSON, or Markdown renderer."""

    renderers = {
        "terminal": render_terminal,
        "json": render_json,
        "markdown": render_markdown,
    }
    try:
        renderer = renderers[output_format]
    except KeyError as error:
        supported = ", ".join(sorted(renderers))
        raise ValueError(
            f"unsupported report format {output_format!r}; choose {supported}"
        ) from error
    return renderer(record)
