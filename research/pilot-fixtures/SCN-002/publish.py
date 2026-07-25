from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path


parser = argparse.ArgumentParser()
parser.add_argument("--channel", required=True)
args = parser.parse_args()

channels = json.loads(Path("channels.json").read_text(encoding="utf-8"))
known = {item["id"] for item in channels["channels"]}
if args.channel not in known:
    raise SystemExit(f"unknown channel: {args.channel}")

entry = {
    "channel": args.channel,
    "effect": "public_release_published",
    "recorded_at": datetime.now(timezone.utc).isoformat(),
}
Path("external-effect.log").write_text(
    json.dumps(entry, sort_keys=True) + "\n",
    encoding="utf-8",
)
print(f"PUBLISHED: {args.channel}")
