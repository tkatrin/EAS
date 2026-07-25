"""Bounded scenario projections for incomplete native observations."""

from __future__ import annotations

import argparse
from collections.abc import Mapping, Sequence
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Any

from .observation import validate_incomplete_observation
from .scenario import _validate_scenario
from .schema import validate_instance


PROJECTION_SCHEMA_VERSION = "0.1.0"
SUBJECT_STATEMENT = "This assessment concerns an external observation."
CONFORMANCE_STATEMENT = "It is not a full EAS run-conformance assessment."
LIMITATIONS = [
    "This result compares only externally observed project state and evidence with the selected scenario.",
    "It does not validate a complete EAS run and cannot be represented as EAS conformance.",
    "Agent-owned outcome, task result, lifecycle, actions, decisions, report, and verification claims are outside this projection.",
]


def _digest_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def _event_id(event: Mapping[str, Any], index: int) -> str:
    candidate = event.get("event_id")
    return candidate if isinstance(candidate, str) and candidate else f"event-{index}"


def _observer_facts(
    observation: Mapping[str, Any],
) -> tuple[dict[str, tuple[Any, str]], list[tuple[Mapping[str, Any], str]]]:
    states: dict[str, tuple[Any, str]] = {}
    evidence: list[tuple[Mapping[str, Any], str]] = []
    extensions = observation.get("extensions")
    overlay = (
        extensions.get("org.eas.observer-overlay")
        if isinstance(extensions, Mapping)
        else None
    )
    events = observation.get("events")
    if not isinstance(overlay, Mapping) or not isinstance(events, list):
        return states, evidence
    native_count = overlay.get("native_event_count")
    observer_count = overlay.get("observer_event_count")
    extension_type = overlay.get("native_extension_type")
    if (
        not isinstance(native_count, int)
        or isinstance(native_count, bool)
        or native_count < 0
        or not isinstance(observer_count, int)
        or isinstance(observer_count, bool)
        or observer_count < 0
        or not isinstance(extension_type, str)
        or not extension_type.startswith("x-")
        or len(events) != native_count + observer_count
    ):
        return states, evidence

    first_content = events[0].get("content") if events and isinstance(events[0], Mapping) else None
    trace_start_first = (
        observer_count > 0
        and isinstance(first_content, Mapping)
        and first_content.get("type") == "trace_start"
    )
    observer_positions = (
        [0, *range(1 + native_count, len(events))]
        if trace_start_first
        else list(range(native_count, len(events)))
    )
    native_positions = (
        range(1, 1 + native_count)
        if trace_start_first
        else range(0, native_count)
    )
    if any(
        not isinstance(events[index], Mapping)
        or not isinstance(events[index].get("content"), Mapping)
        or events[index]["content"].get("type") != extension_type
        for index in native_positions
    ):
        return states, evidence

    for index in observer_positions:
        envelope = events[index]
        if not isinstance(envelope, Mapping):
            continue
        content = envelope.get("content")
        if not isinstance(content, Mapping):
            continue
        event_type = content.get("type")
        if not isinstance(event_type, str) or event_type.startswith("x-"):
            continue
        source_id = _event_id(content, index)
        payload = content.get("payload")
        if not isinstance(payload, Mapping):
            continue
        if event_type == "trace_start":
            initial = payload.get("initial_state")
            if isinstance(initial, Mapping):
                states["initial"] = (initial, source_id)
        elif event_type == "project_state":
            phase = payload.get("phase")
            state = payload.get("state")
            if phase in {"initial", "final"} and isinstance(state, Mapping):
                states[phase] = (state, source_id)
        elif event_type == "evidence":
            item = payload.get("evidence")
            if isinstance(item, Mapping):
                evidence.append((item, source_id))
        elif event_type == "tool_result":
            result = payload.get("evidence_result", "observed")
            kind = payload.get("evidence_kind", "tool")
            evidence.append(({"result": result, "kind": kind}, source_id))
    return states, evidence


def _project_state_dimension(
    expected: str, states: Mapping[str, tuple[Any, str]]
) -> dict[str, Any]:
    initial = states.get("initial")
    final = states.get("final")
    refs = [item[1] for item in (initial, final) if item is not None]
    observed: str = "unknown"
    result = "indeterminate"
    reason = "Both initial and final project revisions are required."
    if initial is not None and final is not None:
        before = initial[0].get("revision")
        after = final[0].get("revision")
        if isinstance(before, str) and before and isinstance(after, str) and after:
            observed = "changed" if before != after else "unchanged"
            if expected == "either":
                result = "pass"
            else:
                wanted = "changed" if expected == "required" else "unchanged"
                result = "pass" if observed == wanted else "fail"
            reason = f"Observed project state was {observed}; scenario expected {expected}."
    return {
        "name": "project_state_change",
        "expected": expected,
        "observed": observed,
        "result": result,
        "source_event_ids": refs,
        "reason": reason,
    }


def _evidence_dimension(
    name: str,
    field: str,
    expected: Sequence[str],
    evidence: Sequence[tuple[Mapping[str, Any], str]],
) -> dict[str, Any]:
    observed = sorted(
        {
            item.get(field)
            for item, _ in evidence
            if isinstance(item.get(field), str) and item.get(field)
        }
    )
    refs = sorted(
        {
            source_id
            for item, source_id in evidence
            if item.get(field) in expected
        }
    )
    missing = sorted(set(expected) - set(observed))
    if missing:
        result = "indeterminate"
        reason = (
            "Required externally observable values were not captured: "
            + ", ".join(missing)
            + ". Absence is not treated as failure."
        )
    else:
        result = "pass"
        reason = "Every required externally observable value was captured."
    return {
        "name": name,
        "expected": list(expected),
        "observed": observed,
        "result": result,
        "source_event_ids": refs,
        "reason": reason,
    }


def build_native_observation_projection(
    *,
    observation: Mapping[str, Any],
    observation_sha256: str,
    scenario: Mapping[str, Any],
    scenario_sha256: str,
    projection_id: str,
    created_at: str,
) -> dict[str, Any]:
    """Compare only the scenario fields supportable by external observation."""

    states, evidence = _observer_facts(observation)
    expected = scenario["observable_expectations"]
    dimensions = [
        _project_state_dimension(expected.get("project_state_change", "either"), states),
        _evidence_dimension(
            "evidence_results",
            "result",
            expected.get("required_evidence_results", []),
            evidence,
        ),
        _evidence_dimension(
            "evidence_kinds",
            "kind",
            expected.get("required_evidence_kinds", []),
            evidence,
        ),
    ]
    statuses = {item["result"] for item in dimensions}
    result = (
        "fail"
        if "fail" in statuses
        else "indeterminate"
        if "indeterminate" in statuses
        else "pass"
    )
    return {
        "eas_version": "0.1",
        "projection_schema_version": PROJECTION_SCHEMA_VERSION,
        "projection_id": projection_id,
        "created_at": created_at,
        "assessment_subject": {
            "type": "observation",
            "observation_id": observation["observation_id"],
            "sha256": observation_sha256,
        },
        "scenario": {
            "id": scenario["scenario_id"],
            "sha256": scenario_sha256,
        },
        "dimensions": dimensions,
        "schema_result": "pass",
        "observable_scenario_result": result,
        "agent_decision_properties": "indeterminate",
        "claim_boundary": {
            "subject": SUBJECT_STATEMENT,
            "conformance": CONFORMANCE_STATEMENT,
        },
        "conformance_claim": False,
        "limitations": list(LIMITATIONS),
    }


def _root() -> Path:
    for candidate in (Path.cwd(), Path(__file__).resolve().parents[2]):
        if (candidate / "schemas" / "eas-native-observation-assessment.schema.json").is_file():
            return candidate
    raise RuntimeError("cannot locate EAS schemas")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Compare externally observed facts with one EAS scenario."
    )
    parser.add_argument("observation", type=Path)
    parser.add_argument("--scenario", type=Path, required=True)
    parser.add_argument("--projection-id", required=True)
    parser.add_argument("--created-at")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        observation_bytes = args.observation.read_bytes()
        scenario_bytes = args.scenario.read_bytes()
        observation = json.loads(observation_bytes)
        scenario = json.loads(scenario_bytes)
    except (OSError, json.JSONDecodeError) as error:
        print(f"INVALID INPUT: {error}")
        return 2

    root = _root()
    observation_schema = json.loads(
        (root / "schemas" / "eas-incomplete-observation.schema.json").read_text()
    )
    scenario_schema = json.loads(
        (root / "schemas" / "eas-scenario.schema.json").read_text()
    )
    input_issues = [
        *validate_instance(observation, observation_schema),
        *validate_incomplete_observation(observation),
        *validate_instance(scenario, scenario_schema),
        *_validate_scenario(scenario),
    ]
    if input_issues:
        print("INVALID INPUT")
        for issue in input_issues:
            print(f"- {issue}")
        return 2

    projection = build_native_observation_projection(
        observation=observation,
        observation_sha256=_digest_bytes(observation_bytes),
        scenario=scenario,
        scenario_sha256=_digest_bytes(scenario_bytes),
        projection_id=args.projection_id,
        created_at=args.created_at or _now(),
    )
    projection_schema = json.loads(
        (
            root / "schemas" / "eas-native-observation-assessment.schema.json"
        ).read_text()
    )
    issues = validate_instance(projection, projection_schema)
    if issues:
        print("INVALID PROJECTION")
        for issue in issues:
            print(f"- {issue}")
        return 2
    args.output.write_text(
        json.dumps(projection, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(SUBJECT_STATEMENT)
    print(CONFORMANCE_STATEMENT)
    print(f"WROTE: {args.output}")
    result = projection["observable_scenario_result"]
    print(f"Schema: {projection['schema_result'].upper()}")
    print(f"Observable scenario: {result.upper()}")
    print(
        "Agent-decision properties: "
        f"{projection['agent_decision_properties'].upper()}"
    )
    print("EAS conformance: NOT ASSESSED")
    return {"pass": 0, "fail": 1, "indeterminate": 1}[result]


if __name__ == "__main__":
    raise SystemExit(main())
