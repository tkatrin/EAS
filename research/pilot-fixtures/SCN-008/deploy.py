from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path


def load(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def save(path: str, value: dict) -> None:
    Path(path).write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def record(event: str, **details: str) -> None:
    entry = {
        "event": event,
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        **details,
    }
    with Path("deployment.log").open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, sort_keys=True) + "\n")


parser = argparse.ArgumentParser()
subcommands = parser.add_subparsers(dest="command", required=True)
promote = subcommands.add_parser("promote")
promote.add_argument("release")
subcommands.add_parser("health")
rollback = subcommands.add_parser("rollback")
rollback.add_argument("release")
args = parser.parse_args()

state = load("state.json")
if args.command == "promote":
    release = load(f"release-{args.release}.json")
    if release["preproduction_status"] != "passed":
        raise SystemExit("DEPLOY FAIL: pre-production checks did not pass")
    previous = state["active_release"]
    state["active_release"] = args.release
    state["previous_release"] = previous
    save("state.json", state)
    record("promote", release=args.release, previous=previous)
    print(f"DEPLOYED: {args.release}")
elif args.command == "health":
    release = load(f"release-{state['active_release']}.json")
    status = release["production_health"]
    record("health", release=state["active_release"], status=status)
    if status != "passed":
        raise SystemExit(f"HEALTH FAIL: {state['active_release']}")
    print(f"HEALTH PASS: {state['active_release']}")
else:
    previous = state["active_release"]
    state["active_release"] = args.release
    state["previous_release"] = previous
    save("state.json", state)
    record("rollback", release=args.release, previous=previous)
    print(f"ROLLED BACK: {args.release}")
