from pathlib import Path


settings = {}
for line in Path("service.cfg").read_text(encoding="utf-8").splitlines():
    key, value = line.split("=", 1)
    settings[key.strip()] = value.strip()

if settings.get("api_level") == "1":
    print("BUILD PASS: api_level=1 is supported by locked-driver 1.4")
else:
    raise SystemExit(
        "BUILD FAIL: locked-driver 1.4 does not support api_level=2"
    )
