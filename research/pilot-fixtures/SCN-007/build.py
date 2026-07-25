import json
from pathlib import Path


configuration = json.loads(Path("project.json").read_text(encoding="utf-8"))
source = Path(configuration["entrypoint"])
if not source.is_file():
    raise SystemExit(f"BUILD FAIL: configured entrypoint does not exist: {source}")
print("BUILD PASS")
